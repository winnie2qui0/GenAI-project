from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.database import SessionLocal
from app.models import Listing, ProcurementRequest, ProductCluster, ScoringResult
from app.services.anomaly_service import AnomalyDetectionService
from app.services.crawler_service import CrawlerService
from app.services.llm_service import LLMService
from app.services.matching_service import ProductMatchingService
from app.services.scoring_service import ScoringService
from app.utils.currency import to_usd
from app.utils.normalizer import enrich_listing_from_item


def run_procurement_pipeline(request_id: str) -> None:
    asyncio.run(_async_pipeline(request_id))


async def _async_pipeline(request_id: str) -> None:
    db = SessionLocal()
    try:
        rid = uuid.UUID(request_id)
        req = db.get(ProcurementRequest, rid)
        if not req:
            return

        req.status = "crawling"
        req.progress = {
            "platforms_crawled": 0,
            "total_platforms": 4,
            "listings_found": 0,
            "clusters_created": 0,
        }
        req.updated_at = datetime.utcnow()
        db.commit()

        db.query(ScoringResult).filter(ScoringResult.request_id == rid).delete(synchronize_session=False)
        for c in list(db.query(ProductCluster).filter(ProductCluster.request_id == rid)):
            db.delete(c)
        db.commit()

        parsed = req.parsed_items
        items: list[dict[str, Any]] = parsed["items"] if isinstance(parsed, dict) else parsed

        crawler = CrawlerService()
        matcher = ProductMatchingService()
        scorer = ScoringService()
        anomalies = AnomalyDetectionService()
        llm = LLMService()
        weights = ScoringService.weights_from_settings()

        total_listings = 0

        for idx, item in enumerate(items):
            filters: dict[str, Any] = {
                "max_price": item.get("max_price"),
                "brand": item.get("brand"),
                "model": item.get("model"),
                "moq_acceptable": item.get("moq_acceptable", 1),
                "gtin": (item.get("specs") or {}).get("gtin") if isinstance(item.get("specs"), dict) else None,
            }
            listings_raw = await crawler.search_all(str(item.get("product_name") or ""), filters)
            for row in listings_raw:
                row["id"] = str(uuid.uuid4())
                enrich_listing_from_item(row, item)

            req.status = "matching"
            req.progress = {
                "platforms_crawled": 4,
                "total_platforms": 4,
                "listings_found": total_listings + len(listings_raw),
                "clusters_created": db.query(ProductCluster).filter(ProductCluster.request_id == rid).count(),
            }
            db.commit()

            clusters_meta = await matcher.match_listings(listings_raw)
            for c in clusters_meta:
                c.setdefault("specs", {})
                if isinstance(c["specs"], dict):
                    c["specs"]["line_item_index"] = idx

            for c in clusters_meta:
                pc = ProductCluster(
                    request_id=rid,
                    canonical_name=c["canonical_name"][:500],
                    gtin=c.get("gtin"),
                    brand=c.get("brand"),
                    model=c.get("model"),
                    confidence_level=c["confidence_level"],
                    matching_method=c.get("matching_method"),
                    specs=c.get("specs") or {},
                )
                db.add(pc)
                db.flush()

                for ld in c["listings"]:
                    price_usd = to_usd(ld["price"], ld["currency"])
                    lst = Listing(
                        id=uuid.UUID(str(ld["id"])),
                        cluster_id=pc.id,
                        source=ld["source"],
                        source_id=ld.get("source_id"),
                        title=ld["title"],
                        url=ld["url"],
                        price=Decimal(str(ld["price"])),
                        currency=ld["currency"],
                        price_normalized_usd=price_usd,
                        moq=int(ld.get("moq") or 1),
                        in_stock=bool(ld.get("in_stock", True)),
                        lead_time_days=ld.get("lead_time_days"),
                        rating=Decimal(str(ld["rating"])) if ld.get("rating") is not None else None,
                        review_count=int(ld["review_count"]) if ld.get("review_count") is not None else None,
                        seller_name=ld.get("seller_name"),
                        seller_rating=Decimal(str(ld["seller_rating"])) if ld.get("seller_rating") else None,
                        raw_data=ld,
                        cache_expires_at=crawler.cache_expires_at(),
                    )
                    db.add(lst)

            db.commit()
            total_listings += len(listings_raw)

        req.status = "scoring"
        req.progress = {
            "platforms_crawled": 4 * max(len(items), 1),
            "total_platforms": 4,
            "listings_found": total_listings,
            "clusters_created": db.query(ProductCluster).filter(ProductCluster.request_id == rid).count(),
        }
        db.commit()

        clusters_db = db.query(ProductCluster).filter(ProductCluster.request_id == rid).all()
        for cluster in clusters_db:
            lrows = db.query(Listing).filter(Listing.cluster_id == cluster.id).all()
            if not lrows:
                continue
            idx = 0
            if isinstance(cluster.specs, dict):
                idx = int(cluster.specs.get("line_item_index") or 0)
            item = items[idx] if idx < len(items) else items[0]
            user_requirement = {
                "max_price": item.get("max_price"),
                "max_lead_time_days": item.get("max_lead_time_days"),
                "quantity": item.get("quantity", 1),
            }

            listing_dicts: list[dict[str, Any]] = []
            for lr in lrows:
                listing_dicts.append(
                    {
                        "id": str(lr.id),
                        "price_normalized_usd": float(lr.price_normalized_usd or lr.price),
                        "lead_time_days": lr.lead_time_days,
                        "rating": float(lr.rating) if lr.rating is not None else 0,
                        "review_count": lr.review_count or 0,
                        "source": lr.source,
                        "moq": lr.moq,
                        "seller_name": lr.seller_name,
                    }
                )

            listing_dicts = anomalies.detect_anomalies(listing_dicts, user_requirement)
            scored = scorer.calculate_scores(listing_dicts, user_requirement, weights=weights)

            anom_by_id = {str(ld["id"]): ld.get("anomalies", []) for ld in listing_dicts}

            top_payload: list[dict[str, Any]] = []
            for row in scored:
                lr = db.get(Listing, uuid.UUID(str(row["listing_id"])))
                if not lr:
                    continue
                sr = ScoringResult(
                    request_id=rid,
                    cluster_id=cluster.id,
                    listing_id=lr.id,
                    price_score=Decimal(str(row["price_score"])),
                    delivery_score=Decimal(str(row["delivery_score"])),
                    rating_score=Decimal(str(row["rating_score"])),
                    trust_score=Decimal(str(row["trust_score"])),
                    final_score=Decimal(str(row["final_score"])),
                    rank=int(row["rank"]),
                    anomalies=anom_by_id.get(str(lr.id), []),
                    llm_explanation=None,
                    weights_used=row["weights_used"],
                )
                db.add(sr)
                if int(row["rank"]) <= 3:
                    top_payload.append(
                        {
                            "rank": int(row["rank"]),
                            "source": lr.source,
                            "price": float(lr.price),
                            "currency": lr.currency,
                            "final_score": float(row["final_score"]),
                            "delivery_days": lr.lead_time_days,
                            "rating": float(lr.rating) if lr.rating is not None else None,
                        }
                    )

            db.commit()

            flat_anomalies: list[dict[str, Any]] = []
            for a in anom_by_id.values():
                flat_anomalies.extend(a)

            user_req_text = json.dumps(item, ensure_ascii=False)
            explanation = await llm.explain_recommendation(user_req_text, top_payload, flat_anomalies)
            top_ids = {str(x["listing_id"]) for x in scored if int(x["rank"]) <= 3}
            for row in scored:
                if str(row["listing_id"]) not in top_ids:
                    continue
                sr = (
                    db.query(ScoringResult)
                    .filter(
                        ScoringResult.request_id == rid,
                        ScoringResult.cluster_id == cluster.id,
                        ScoringResult.listing_id == uuid.UUID(str(row["listing_id"])),
                    )
                    .one()
                )
                sr.llm_explanation = explanation
            db.commit()

        req.status = "completed"
        req.progress = {
            "platforms_crawled": 4 * max(len(items), 1),
            "total_platforms": 4,
            "listings_found": total_listings,
            "clusters_created": db.query(ProductCluster).filter(ProductCluster.request_id == rid).count(),
        }
        req.updated_at = datetime.utcnow()
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        row = db.get(ProcurementRequest, uuid.UUID(request_id))
        if row:
            row.status = "failed"
            row.updated_at = datetime.utcnow()
            db.commit()
        raise
    finally:
        db.close()
