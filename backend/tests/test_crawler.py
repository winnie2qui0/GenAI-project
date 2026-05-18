import pytest
from app.crawlers.amazon import AmazonCrawler
from app.crawlers.alibaba import AlibabaCrawler
from app.crawlers.pchome import PChomeCrawler
from app.crawlers.local_b2b import LocalB2BCrawler


@pytest.mark.asyncio
async def test_amazon_mock_returns_results():
    crawler = AmazonCrawler()
    results = crawler._mock_results("HP toner CF410A")
    assert len(results) > 0
    for r in results:
        assert r["source"] == "amazon"
        assert r["price"] > 0
        assert r["currency"] == "USD"
        assert r["url"].startswith("https://")


@pytest.mark.asyncio
async def test_alibaba_mock_returns_results():
    crawler = AlibabaCrawler()
    results = crawler._mock_results("HP toner CF410A")
    assert len(results) > 0
    for r in results:
        assert r["source"] == "alibaba"
        assert r["price"] > 0


@pytest.mark.asyncio
async def test_pchome_mock_returns_results():
    crawler = PChomeCrawler()
    results = crawler._mock_results("HP toner")
    assert len(results) > 0
    for r in results:
        assert r["source"] == "pchome"
        assert r["currency"] == "TWD"


@pytest.mark.asyncio
async def test_local_b2b_returns_results():
    crawler = LocalB2BCrawler()
    results = await crawler.search("HP toner", {})
    assert len(results) > 0
    for r in results:
        assert r["source"] == "local_b2b"


@pytest.mark.asyncio
async def test_all_crawlers_have_required_fields():
    crawlers = [AmazonCrawler(), AlibabaCrawler(), PChomeCrawler(), LocalB2BCrawler()]
    required = {"source", "title", "price", "currency", "url"}
    for crawler in crawlers:
        results = await crawler.search("test product", {})
        for r in results:
            missing = required - set(r.keys())
            assert not missing, f"{crawler.__class__.__name__} missing fields: {missing}"
