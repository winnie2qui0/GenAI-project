from abc import ABC, abstractmethod
import asyncio
import random
from typing import Any

from app.config import get_settings


class BaseCrawler(ABC):
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    ]

    @property
    def delay_range(self) -> tuple[float, float]:
        s = get_settings()
        return (float(s.crawler_delay_min), float(s.crawler_delay_max))

    @abstractmethod
    async def search(self, query: str, filters: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError

    async def random_delay(self) -> None:
        lo, hi = self.delay_range
        await asyncio.sleep(random.uniform(lo, hi))

    def get_random_user_agent(self) -> str:
        return random.choice(self.USER_AGENTS)
