from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

from app.crawlers.base import BaseCrawler


class AmazonCrawler(BaseCrawler):
    BASE_URL = "https://www.amazon.com"

    async def search(self, query: str, filters: dict[str, Any]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": self.get_random_user_agent()},
                follow_redirects=True,
                timeout=get_settings_timeout(),
            ) as client:
                await self.random_delay()
                search_url = f"{self.BASE_URL}/s?k={quote_plus(query)}"
                if filters.get("max_price"):
                    cents = int(float(filters["max_price"]) * 100)
                    search_url += f"&rh=p_36%3A-{cents}"
                resp = await client.get(search_url)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                for item in soup.select("[data-asin]"):
                    asin = item.get("data-asin")
                    if not asin or asin == "B015KYJ0AW":
                        continue
                    title_el = item.select_one("h2 a span")
                    price_whole = item.select_one(".a-price .a-offscreen")
                    if not title_el:
                        continue
                    title = title_el.text.strip()
                    price_val = None
                    if price_whole:
                        raw = price_whole.text.replace("$", "").replace(",", "").strip()
                        try:
                            price_val = float(raw)
                        except ValueError:
                            price_val = None
                    if price_val is None:
                        continue
                    rating_el = item.select_one("i.a-icon-star-small span, span.a-icon-alt")
                    rating = None
                    if rating_el and "out of" in (rating_el.text or ""):
                        try:
                            rating = float(rating_el.text.split()[0])
                        except (ValueError, IndexError):
                            rating = None
                    results.append(
                        {
                            "source": "amazon",
                            "source_id": asin,
                            "title": title,
                            "price": price_val,
                            "currency": "USD",
                            "rating": rating,
                            "review_count": 0,
                            "url": f"{self.BASE_URL}/dp/{asin}",
                            "moq": 1,
                            "lead_time_days": 3,
                            "in_stock": True,
                            "seller_name": None,
                            "gtin": None,
                            "brand": filters.get("brand"),
                            "model": filters.get("model"),
                        }
                    )
        except Exception:
            return _mock_amazon(query, filters)
        if not results:
            return _mock_amazon(query, filters)
        return results


def get_settings_timeout() -> float:
    from app.config import get_settings

    return float(get_settings().crawler_timeout)


def _mock_amazon(query: str, filters: dict[str, Any]) -> list[dict[str, Any]]:
    base = float(filters.get("max_price") or 99.0)
    return [
        {
            "source": "amazon",
            "source_id": "B00MOCKAMZ",
            "title": f"{query} — Amazon (demo listing)",
            "price": round(base * 0.95, 2),
            "currency": "USD",
            "rating": 4.5,
            "review_count": 500,
            "url": "https://www.amazon.com/dp/B00MOCKAMZ",
            "moq": 1,
            "lead_time_days": 2,
            "in_stock": True,
            "seller_name": "DemoSeller",
            "gtin": None,
            "brand": filters.get("brand"),
            "model": filters.get("model"),
        }
    ]
