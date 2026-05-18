import pytest
from app.services.matching_service import ProductMatchingService


@pytest.fixture
def service():
    return ProductMatchingService()


@pytest.mark.asyncio
async def test_gtin_match_creates_high_confidence_cluster(service):
    listings = [
        {"title": "HP Toner A", "source": "amazon", "gtin": "12345678", "price": 30},
        {"title": "HP Toner B", "source": "alibaba", "gtin": "12345678", "price": 28},
    ]
    clusters = await service.match_listings(listings)
    assert len(clusters) == 1
    assert clusters[0]["confidence_level"] == "HIGH"
    assert clusters[0]["matching_method"] == "gtin"
    assert len(clusters[0]["listings"]) == 2


@pytest.mark.asyncio
async def test_brand_model_match_creates_medium_confidence(service):
    listings = [
        {"title": "HP CF410A toner", "source": "amazon", "brand": "HP", "model": "CF410A", "price": 30},
        {"title": "HP CF410A cartridge", "source": "pchome", "brand": "HP", "model": "CF410A", "price": 32},
    ]
    clusters = await service.match_listings(listings)
    assert len(clusters) == 1
    assert clusters[0]["confidence_level"] == "MEDIUM"


@pytest.mark.asyncio
async def test_different_products_form_separate_clusters(service):
    listings = [
        {"title": "HP Toner", "source": "amazon", "brand": "HP", "model": "CF410A", "price": 30},
        {"title": "Canon Ink", "source": "amazon", "brand": "Canon", "model": "PG-245", "price": 15},
    ]
    clusters = await service.match_listings(listings)
    assert len(clusters) == 2


@pytest.mark.asyncio
async def test_gtin_takes_priority_over_brand_model(service):
    listings = [
        {"title": "Prod A", "source": "amazon", "gtin": "999", "brand": "HP", "model": "X1", "price": 30},
        {"title": "Prod B", "source": "alibaba", "gtin": "999", "brand": "HP", "model": "X1", "price": 28},
    ]
    clusters = await service.match_listings(listings)
    # GTIN match should group them; brand_model won't create additional cluster
    assert len(clusters) == 1
    assert clusters[0]["matching_method"] == "gtin"


@pytest.mark.asyncio
async def test_empty_listings_returns_empty(service):
    clusters = await service.match_listings([])
    assert clusters == []
