import logging
from typing import Any

from app.crawlers.base import BaseCrawler

logger = logging.getLogger(__name__)


class LocalB2BCrawler(BaseCrawler):
    """
    Placeholder for a local B2B marketplace.
    Returns mock data; replace with real API/scraper for production.
    """

    async def search(self, query: str, filters: dict[str, Any]) -> list[dict[str, Any]]:
        await self.random_delay()
        return self._mock_results(query)

    def _mock_results(self, query: str) -> list[dict[str, Any]]:
        return [
            {
                "source": "local_b2b",
                "source_id": "LB2B-001",
                "title": f"{query} - Local Distributor",
                "price": 28.50,
                "currency": "USD",
                "rating": 4.0,
                "review_count": 22,
                "lead_time_days": 5,
                "moq": 10,
                "in_stock": True,
                "seller_name": "Local Office Supplies Inc.",
                "seller_rating": 4.2,
                "url": "https://localb2b.example.com/product/001",
            },
        ]
