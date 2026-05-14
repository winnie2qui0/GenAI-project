from __future__ import annotations

from typing import Any

from app.crawlers.base import BaseCrawler


class LocalB2BCrawler(BaseCrawler):
    async def search(self, query: str, filters: dict[str, Any]) -> list[dict[str, Any]]:
        await self.random_delay()
        usd = float(filters.get("max_price") or 110.0)
        return [
            {
                "source": "local_b2b",
                "source_id": "LOCAL-DEMO-1",
                "title": f"{query} — Local B2B catalog (demo)",
                "price": round(usd * 1.02, 2),
                "currency": "USD",
                "rating": 4.0,
                "review_count": 12,
                "url": "https://example-b2b.local/items/demo",
                "moq": 1,
                "lead_time_days": 5,
                "in_stock": True,
                "seller_name": "LocalOfficeSupply",
                "gtin": filters.get("gtin"),
                "brand": filters.get("brand"),
                "model": filters.get("model"),
            }
        ]
