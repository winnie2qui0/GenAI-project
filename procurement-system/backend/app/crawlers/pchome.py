from __future__ import annotations

from typing import Any

from app.crawlers.base import BaseCrawler


class PChomeCrawler(BaseCrawler):
    async def search(self, query: str, filters: dict[str, Any]) -> list[dict[str, Any]]:
        await self.random_delay()
        twd = float(filters.get("max_price") or 3000) * 30
        return [
            {
                "source": "pchome",
                "source_id": "PCH-DEMO-1",
                "title": f"{query} — PChome 24h (demo)",
                "price": round(twd * 0.9, 0),
                "currency": "TWD",
                "rating": 4.6,
                "review_count": 220,
                "url": "https://24h.pchome.com.tw/prod/demo",
                "moq": 1,
                "lead_time_days": 2,
                "in_stock": True,
                "seller_name": "PChome",
                "gtin": None,
                "brand": filters.get("brand"),
                "model": filters.get("model"),
            }
        ]
