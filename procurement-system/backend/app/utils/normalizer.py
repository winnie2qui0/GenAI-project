"""Normalize units and common procurement text fields."""

from __future__ import annotations

import re
from typing import Any


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", (title or "").strip())


def enrich_listing_from_item(listing: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    if not listing.get("brand") and item.get("brand"):
        listing["brand"] = item["brand"]
    if not listing.get("model") and item.get("model"):
        listing["model"] = item["model"]
    listing.setdefault("specs", item.get("specs") or {})
    return listing
