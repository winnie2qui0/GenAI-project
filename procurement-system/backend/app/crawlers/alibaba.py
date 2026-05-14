from __future__ import annotations

from typing import Any

from app.crawlers.base import BaseCrawler


class AlibabaCrawler(BaseCrawler):
    async def search(self, query: str, filters: dict[str, Any]) -> list[dict[str, Any]]:
        await self.random_delay()
        usd = float(filters.get("max_price") or 120.0)
        return [
            {
                "source": "alibaba",
                "source_id": "ALI-DEMO-1",
                "title": f"{query} — Alibaba wholesale (demo)",
                "price": round(usd * 0.88, 2),
                "currency": "USD",
                "rating": 4.2,
                "review_count": 80,
                "url": "https://www.alibaba.com/product/demo",
                "moq": int(filters.get("moq_acceptable") or 1),
                "lead_time_days": 10,
                "in_stock": True,
                "seller_name": "DemoFactory",
                "gtin": None,
                "brand": filters.get("brand"),
                "model": filters.get("model"),
            }
        ]
