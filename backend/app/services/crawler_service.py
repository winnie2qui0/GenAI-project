import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.crawlers.amazon import AmazonCrawler
from app.crawlers.alibaba import AlibabaCrawler
from app.crawlers.pchome import PChomeCrawler
from app.crawlers.local_b2b import LocalB2BCrawler
from app.models.listing import Listing
from app.models.product_cluster import ProductCluster
from app.models.procurement_request import ProcurementRequest
from app.models.scoring_result import ScoringResult
from app.services.matching_service import ProductMatchingService
from app.services.scoring_service import ScoringService
from app.services.anomaly_service import AnomalyDetectionService
from app.services.llm_service import LLMService
from app.utils.currency import convert_to_usd

logger = logging.getLogger(__name__)
settings = get_settings()

# In-memory status tracker (sufficient for MVP single-process)
_status_store: dict[str, dict[str, Any]] = {}


def get_status(request_id: str) -> dict[str, Any]:
    return _status_store.get(request_id, {"status": "pending", "progress": {}})


def set_status(request_id: str, status: str, progress: dict[str, Any]):
    _status_store[request_id] = {"status": status, "progress": progress}


class CrawlerService:
    def __init__(self):
        self.crawlers = {
            "amazon": AmazonCrawler(),
            "alibaba": AlibabaCrawler(),
            "pchome": PChomeCrawler(),
            "local_b2b": LocalB2BCrawler(),
        }
        self.matcher = ProductMatchingService()
        self.scorer = ScoringService()
        self.anomaly_detector = AnomalyDetectionService()
        self.llm_service = LLMService()

    async def run_pipeline(
        self,
        db: AsyncSession,
        request_id: uuid.UUID,
        items: list[dict[str, Any]],
    ):
        rid = str(request_id)
        try:
            set_status(rid, "crawling", {"platforms_crawled": 0, "total_platforms": 4, "listings_found": 0, "clusters_created": 0})

            all_raw_listings: list[dict[str, Any]] = []
            platforms = list(self.crawlers.keys())

            for i, (platform, crawler) in enumerate(self.crawlers.items()):
                for item in items:
                    query = f"{item.get('brand', '')} {item.get('model', '')} {item['product_name']}".strip()
                    filters = {
                        "max_price": item.get("max_price"),
                        "quantity": item.get("quantity", 1),
                    }
                    try:
                        results = await crawler.search(query, filters)
                        for r in results:
                            r["_item_ref"] = item
                        all_raw_listings.extend(results)
                    except Exception as e:
                        logger.warning(f"Crawler {platform} failed for '{query}': {e}")

                set_status(rid, "crawling", {
                    "platforms_crawled": i + 1,
                    "total_platforms": len(platforms),
                    "listings_found": len(all_raw_listings),
                    "clusters_created": 0,
                })

            # Normalize prices to USD
            for listing in all_raw_listings:
                listing["price_normalized_usd"] = convert_to_usd(
                    float(listing.get("price", 0)),
                    listing.get("currency", "USD"),
                )

            set_status(rid, "matching", {"listings_found": len(all_raw_listings), "clusters_created": 0, "platforms_crawled": 4, "total_platforms": 4})

            # Match listings into clusters
            clusters = await self.matcher.match_listings(all_raw_listings)

            set_status(rid, "scoring", {"listings_found": len(all_raw_listings), "clusters_created": len(clusters), "platforms_crawled": 4, "total_platforms": 4})

            # Persist clusters and listings, then score
            cache_ttl = datetime.utcnow() + timedelta(hours=settings.cache_ttl_hours)

            for cluster_data in clusters:
                cluster_obj = ProductCluster(
                    request_id=request_id,
                    canonical_name=cluster_data["canonical_name"],
                    gtin=cluster_data.get("gtin"),
                    brand=cluster_data.get("brand"),
                    model=cluster_data.get("model"),
                    confidence_level=cluster_data["confidence_level"],
                    matching_method=cluster_data.get("matching_method"),
                )
                db.add(cluster_obj)
                await db.flush()

                listing_objs = []
                for raw in cluster_data["listings"]:
                    listing_obj = Listing(
                        cluster_id=cluster_obj.id,
                        source=raw.get("source", "unknown"),
                        source_id=raw.get("source_id"),
                        title=raw["title"],
                        url=raw.get("url", ""),
                        price=float(raw.get("price", 0)),
                        currency=raw.get("currency", "USD"),
                        price_normalized_usd=raw.get("price_normalized_usd"),
                        moq=int(raw.get("moq") or 1),
                        in_stock=raw.get("in_stock", True),
                        lead_time_days=raw.get("lead_time_days"),
                        rating=raw.get("rating"),
                        review_count=raw.get("review_count"),
                        seller_name=raw.get("seller_name"),
                        seller_rating=raw.get("seller_rating"),
                        raw_data=raw,
                        cache_expires_at=cache_ttl,
                    )
                    db.add(listing_obj)
                    listing_objs.append(listing_obj)

                await db.flush()

                # Detect anomalies (uses first item's requirement as reference)
                item_req = cluster_data["listings"][0].get("_item_ref", {}) if cluster_data["listings"] else {}
                listing_dicts = [
                    {
                        "id": str(lo.id),
                        "price_normalized_usd": float(lo.price_normalized_usd or 0),
                        "lead_time_days": lo.lead_time_days,
                        "rating": float(lo.rating) if lo.rating else None,
                        "review_count": lo.review_count,
                        "moq": lo.moq,
                        "seller_name": lo.seller_name,
                        "source": lo.source,
                    }
                    for lo in listing_objs
                ]
                listing_dicts = self.anomaly_detector.detect_anomalies(listing_dicts, item_req)
                scores = self.scorer.calculate_scores(listing_dicts, item_req)

                for score, listing_obj in zip(
                    sorted(scores, key=lambda x: x["listing_id"]),
                    sorted(listing_objs, key=lambda x: str(x.id)),
                ):
                    # Re-match by listing_id
                    matched_score = next((s for s in scores if s["listing_id"] == str(listing_obj.id)), None)
                    if not matched_score:
                        continue

                    matched_listing_dict = next((d for d in listing_dicts if d["id"] == str(listing_obj.id)), {})

                    sr = ScoringResult(
                        request_id=request_id,
                        cluster_id=cluster_obj.id,
                        listing_id=listing_obj.id,
                        price_score=matched_score["price_score"],
                        delivery_score=matched_score["delivery_score"],
                        rating_score=matched_score["rating_score"],
                        trust_score=matched_score["trust_score"],
                        final_score=matched_score["final_score"],
                        rank=matched_score["rank"],
                        anomalies=matched_listing_dict.get("anomalies", []),
                        weights_used=matched_score["weights_used"],
                    )
                    db.add(sr)

            # Generate LLM explanation for top cluster
            if clusters:
                top_cluster_scores = await self._build_top_scores(db, request_id)
                explanation = await self.llm_service.generate_explanation(
                    user_requirement=str(items[0]) if items else "",
                    ranked_results=top_cluster_scores[:3],
                    anomalies=[],
                )
                # Store explanation on rank-1 scoring result
                result = await db.execute(
                    select(ScoringResult)
                    .where(ScoringResult.request_id == request_id, ScoringResult.rank == 1)
                    .limit(1)
                )
                top_sr = result.scalar_one_or_none()
                if top_sr:
                    top_sr.llm_explanation = explanation

            # Mark request complete
            req_result = await db.execute(
                select(ProcurementRequest).where(ProcurementRequest.id == request_id)
            )
            req_obj = req_result.scalar_one_or_none()
            if req_obj:
                req_obj.status = "completed"

            await db.commit()
            set_status(rid, "completed", {"listings_found": len(all_raw_listings), "clusters_created": len(clusters), "platforms_crawled": 4, "total_platforms": 4})

        except Exception as e:
            logger.error(f"Pipeline error for {request_id}: {e}", exc_info=True)
            await db.rollback()
            set_status(rid, "failed", {"error": str(e)})
            req_result = await db.execute(
                select(ProcurementRequest).where(ProcurementRequest.id == request_id)
            )
            req_obj = req_result.scalar_one_or_none()
            if req_obj:
                req_obj.status = "failed"
            await db.commit()

    async def _build_top_scores(self, db: AsyncSession, request_id: uuid.UUID) -> list[dict]:
        result = await db.execute(
            select(ScoringResult, Listing)
            .join(Listing, ScoringResult.listing_id == Listing.id)
            .where(ScoringResult.request_id == request_id)
            .order_by(ScoringResult.final_score.desc())
            .limit(3)
        )
        rows = result.all()
        return [
            {
                "rank": sr.rank,
                "source": l.source,
                "title": l.title,
                "price_usd": float(l.price_normalized_usd or 0),
                "delivery_days": l.lead_time_days,
                "rating": float(l.rating) if l.rating else None,
                "final_score": float(sr.final_score),
            }
            for sr, l in rows
        ]
