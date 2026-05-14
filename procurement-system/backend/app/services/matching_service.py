from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any

import numpy as np

from app.services.llm_service import LLMService

_ST_MODEL = None


def _get_st_model() -> Any:
    global _ST_MODEL
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:  # pragma: no cover
        return None
    if _ST_MODEL is None:
        _ST_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _ST_MODEL


class ProductMatchingService:
    """Three-layer matching: GTIN/ASIN, brand+model, embedding/LLM."""

    def __init__(self) -> None:
        self.llm_service = LLMService()

    async def match_listings(self, listings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        clusters: list[dict[str, Any]] = []
        unmatched = [dict(l) for l in listings]
        for x in unmatched:
            x.pop("_matched", None)

        clusters.extend(self._match_by_gtin(unmatched))
        unmatched = [l for l in unmatched if not l.get("_matched")]

        clusters.extend(self._match_by_brand_model(unmatched))
        unmatched = [l for l in unmatched if not l.get("_matched")]

        if len(unmatched) > 1:
            clusters.extend(await self._match_by_embedding_llm(unmatched))
        elif len(unmatched) == 1:
            clusters.append(
                {
                    "canonical_name": unmatched[0]["title"],
                    "confidence_level": "LOW",
                    "matching_method": "singleton",
                    "listings": unmatched,
                    "gtin": unmatched[0].get("gtin"),
                    "brand": unmatched[0].get("brand"),
                    "model": unmatched[0].get("model"),
                }
            )

        return clusters

    def _match_by_gtin(self, listings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        groups: dict[str, list[dict[str, Any]]] = {}
        for listing in listings:
            gtin = listing.get("gtin") or listing.get("asin") or listing.get("source_id")
            if not gtin:
                continue
            groups.setdefault(str(gtin), []).append(listing)
            listing["_matched"] = True

        clusters: list[dict[str, Any]] = []
        for gtin, group in groups.items():
            clusters.append(
                {
                    "canonical_name": group[0]["title"],
                    "gtin": gtin,
                    "brand": group[0].get("brand"),
                    "model": group[0].get("model"),
                    "confidence_level": "HIGH",
                    "matching_method": "gtin",
                    "listings": group,
                }
            )
        return clusters

    def _match_by_brand_model(self, listings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        groups: dict[str, list[dict[str, Any]]] = {}
        for listing in listings:
            brand = (listing.get("brand") or "").strip().upper()
            model = (listing.get("model") or "").strip().upper()
            if not brand or not model:
                continue
            key = f"{brand}|{model}"
            groups.setdefault(key, []).append(listing)
            listing["_matched"] = True

        clusters: list[dict[str, Any]] = []
        for key, group in groups.items():
            brand, model = key.split("|", 1)
            clusters.append(
                {
                    "canonical_name": f"{brand} {model}",
                    "gtin": None,
                    "brand": brand,
                    "model": model,
                    "confidence_level": "MEDIUM",
                    "matching_method": "brand_model",
                    "listings": group,
                }
            )
        return clusters

    async def _match_by_embedding_llm(self, listings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if len(listings) < 2:
            return []

        model = _get_st_model()
        titles = [str(l.get("title") or "") for l in listings]

        if model is not None:
            embeddings = model.encode(titles, normalize_embeddings=True)
            sims = np.asarray(embeddings @ embeddings.T, dtype=float)
        else:
            n = len(listings)
            sims = np.zeros((n, n), dtype=float)
            for i in range(n):
                for j in range(i + 1, n):
                    sims[i, j] = sims[j, i] = SequenceMatcher(None, titles[i], titles[j]).ratio()

        clusters: list[dict[str, Any]] = []
        visited: set[int] = set()

        for i in range(len(listings)):
            if i in visited:
                continue
            group = [listings[i]]
            visited.add(i)
            for j in range(i + 1, len(listings)):
                if j in visited:
                    continue
                if float(sims[i, j]) > 0.85:
                    judge = await self.llm_service.judge_same_product(listings[i], listings[j])
                    if judge.get("is_same_product") and float(judge.get("confidence") or 0) > 0.9:
                        group.append(listings[j])
                        visited.add(j)
            clusters.append(
                {
                    "canonical_name": listings[i]["title"],
                    "gtin": listings[i].get("gtin"),
                    "brand": listings[i].get("brand"),
                    "model": listings[i].get("model"),
                    "confidence_level": "LOW",
                    "matching_method": "embedding_llm",
                    "listings": group,
                }
            )
        for l in listings:
            l.pop("_matched", None)
        return clusters
