import pytest

from app.services.matching_service import ProductMatchingService


@pytest.mark.asyncio
async def test_match_by_gtin_groups() -> None:
    svc = ProductMatchingService()
    listings = [
        {
            "id": "1",
            "title": "A",
            "source_id": "X123",
            "gtin": None,
            "asin": None,
            "brand": "HP",
            "model": "M1",
        },
        {
            "id": "2",
            "title": "B",
            "source_id": "X123",
            "gtin": None,
            "asin": None,
            "brand": "HP",
            "model": "M1",
        },
    ]
    clusters = await svc.match_listings(listings)
    assert len(clusters) >= 1
    assert clusters[0]["matching_method"] == "gtin"
    assert len(clusters[0]["listings"]) == 2


@pytest.mark.asyncio
async def test_brand_model_groups() -> None:
    svc = ProductMatchingService()
    listings = [
        {"id": "1", "title": "t1", "brand": "Dell", "model": "E7470"},
        {"id": "2", "title": "t2", "brand": "DELL", "model": "e7470"},
    ]
    clusters = await svc.match_listings(listings)
    methods = {c["matching_method"] for c in clusters}
    assert "brand_model" in methods
