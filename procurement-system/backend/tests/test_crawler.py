import pytest

from app.crawlers.amazon import AmazonCrawler


@pytest.mark.asyncio
async def test_amazon_returns_listings() -> None:
    c = AmazonCrawler()
    rows = await c.search("HP toner", {"max_price": 100.0, "brand": "HP", "model": "CF410A"})
    assert isinstance(rows, list)
    assert rows[0]["source"] == "amazon"
