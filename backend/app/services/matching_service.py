import logging
import numpy as np
from typing import Any

from app.services.llm_service import LLMService
from app.utils.normalizer import normalize_brand, normalize_model

logger = logging.getLogger(__name__)


class ProductMatchingService:
    """
    3-Layer product matching:
    1. GTIN/ASIN direct match  → HIGH confidence
    2. Brand + Model match     → MEDIUM confidence
    3. Embedding + LLM judge   → LOW confidence
    """

    def __init__(self):
        self.llm_service = LLMService()
        self._embedding_model = None

    def _get_embedding_model(self):
        if self._embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                logger.warning(f"Could not load embedding model: {e}")
        return self._embedding_model

    async def match_listings(self, listings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        clusters: list[dict[str, Any]] = []
        working = [dict(l) for l in listings]

        # Layer 1
        gtin_clusters = self._match_by_gtin(working)
        clusters.extend(gtin_clusters)
        working = [l for l in working if not l.get("_matched")]

        # Layer 2
        bm_clusters = self._match_by_brand_model(working)
        clusters.extend(bm_clusters)
        working = [l for l in working if not l.get("_matched")]

        # Layer 3 (optional — falls back gracefully if model unavailable)
        if working:
            emb_clusters = await self._match_by_embedding_llm(working)
            clusters.extend(emb_clusters)

        return clusters

    def _match_by_gtin(self, listings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        groups: dict[str, list] = {}
        for listing in listings:
            gtin = listing.get("gtin") or listing.get("source_id") or listing.get("asin")
            if not gtin:
                continue
            groups.setdefault(gtin, []).append(listing)
            listing["_matched"] = True

        return [
            {
                "canonical_name": group[0]["title"],
                "gtin": gtin,
                "confidence_level": "HIGH",
                "matching_method": "gtin",
                "listings": group,
            }
            for gtin, group in groups.items()
            if group
        ]

    def _match_by_brand_model(self, listings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        groups: dict[str, list] = {}
        for listing in listings:
            brand = normalize_brand(listing.get("brand"))
            model = normalize_model(listing.get("model"))
            if not brand or not model:
                continue
            key = f"{brand}|{model}"
            groups.setdefault(key, []).append(listing)
            listing["_matched"] = True

        clusters = []
        for key, group in groups.items():
            brand, model = key.split("|", 1)
            clusters.append({
                "canonical_name": f"{brand} {model}",
                "brand": brand,
                "model": model,
                "confidence_level": "MEDIUM",
                "matching_method": "brand_model",
                "listings": group,
            })
        return clusters

    async def _match_by_embedding_llm(
        self, listings: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        if len(listings) == 1:
            return [{
                "canonical_name": listings[0]["title"],
                "confidence_level": "LOW",
                "matching_method": "no_match",
                "listings": listings,
            }]

        model = self._get_embedding_model()
        if model is None:
            # Fallback: each listing is its own cluster
            return [
                {
                    "canonical_name": l["title"],
                    "confidence_level": "LOW",
                    "matching_method": "no_match",
                    "listings": [l],
                }
                for l in listings
            ]

        titles = [l["title"] for l in listings]
        embeddings = model.encode(titles, normalize_embeddings=True)
        similarities = np.dot(embeddings, embeddings.T)

        visited: set[int] = set()
        clusters = []

        for i in range(len(listings)):
            if i in visited:
                continue
            group = [listings[i]]
            visited.add(i)

            for j in range(i + 1, len(listings)):
                if j in visited:
                    continue
                if float(similarities[i][j]) > 0.85:
                    try:
                        judgment = await self.llm_service.judge_same_product(listings[i], listings[j])
                        if judgment.is_same_product and judgment.confidence > 0.9:
                            group.append(listings[j])
                            visited.add(j)
                    except Exception as e:
                        logger.warning(f"LLM matching call failed: {e}")

            clusters.append({
                "canonical_name": listings[i]["title"],
                "confidence_level": "LOW",
                "matching_method": "embedding_llm",
                "listings": group,
            })

        return clusters
