from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

from app.config import get_settings
from app.crawlers.alibaba import AlibabaCrawler
from app.crawlers.amazon import AmazonCrawler
from app.crawlers.local_b2b import LocalB2BCrawler
from app.crawlers.pchome import PChomeCrawler


class CrawlerService:
    def __init__(self) -> None:
        self._crawlers = [
            AmazonCrawler(),
            AlibabaCrawler(),
            PChomeCrawler(),
            LocalB2BCrawler(),
        ]

    async def search_all(self, query: str, filters: dict[str, Any]) -> list[dict[str, Any]]:
        tasks = [c.search(query, filters) for c in self._crawlers]
        parts = await asyncio.gather(*tasks, return_exceptions=True)
        out: list[dict[str, Any]] = []
        for chunk in parts:
            if isinstance(chunk, Exception):
                continue
            out.extend(chunk)
        return out

    @staticmethod
    def cache_expires_at() -> datetime:
        hours = int(get_settings().cache_ttl_hours)
        return datetime.utcnow() + timedelta(hours=hours)
