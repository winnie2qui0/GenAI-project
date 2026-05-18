from abc import ABC, abstractmethod
from typing import Any
import asyncio
import random

from app.config import get_settings

settings = get_settings()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]


class BaseCrawler(ABC):
    DELAY_RANGE = (settings.crawler_delay_min, settings.crawler_delay_max)
    TIMEOUT = settings.crawler_timeout

    @abstractmethod
    async def search(self, query: str, filters: dict[str, Any]) -> list[dict[str, Any]]:
        pass

    async def random_delay(self):
        await asyncio.sleep(random.uniform(*self.DELAY_RANGE))

    def get_random_user_agent(self) -> str:
        return random.choice(USER_AGENTS)

    def _make_headers(self) -> dict[str, str]:
        return {
            "User-Agent": self.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
