import pytest
from app.services.anomaly_service import AnomalyDetectionService


@pytest.fixture
def service():
    return AnomalyDetectionService()


def make_listing(id_: str, price: float, moq: int = 1, lead: int = 3, rating: float = 4.0, reviews: int = 100, seller: str = "Acme"):
    return {
        "id": id_,
        "price_normalized_usd": price,
        "moq": moq,
        "lead_time_days": lead,
        "rating": rating,
        "review_count": reviews,
        "seller_name": seller,
    }


def test_high_price_outlier_flagged(service):
    listings = [
        make_listing("a", 30.0),
        make_listing("b", 32.0),
        make_listing("c", 29.0),
        make_listing("d", 31.0),
        make_listing("outlier", 999.0),
    ]
    result = service.detect_anomalies(listings, {"quantity": 10, "max_lead_time_days": 5})
    outlier = next(l for l in result if l["id"] == "outlier")
    types = [a["type"] for a in outlier["anomalies"]]
    assert "price_high" in types


def test_moq_exceeds_quantity_flagged(service):
    listings = [make_listing("a", 30.0, moq=500)]
    result = service.detect_anomalies(listings, {"quantity": 10, "max_lead_time_days": 5})
    types = [a["type"] for a in result[0]["anomalies"]]
    assert "moq_too_high" in types


def test_long_lead_time_flagged(service):
    listings = [make_listing("a", 30.0, lead=60)]
    result = service.detect_anomalies(listings, {"quantity": 10, "max_lead_time_days": 5})
    types = [a["type"] for a in result[0]["anomalies"]]
    assert "lead_time_too_long" in types


def test_missing_reviews_flagged(service):
    listings = [{"id": "a", "price_normalized_usd": 30.0, "moq": 1, "lead_time_days": 2, "rating": None, "review_count": None, "seller_name": "X"}]
    result = service.detect_anomalies(listings, {"quantity": 5, "max_lead_time_days": 5})
    types = [a["type"] for a in result[0]["anomalies"]]
    assert "missing_reviews" in types


def test_normal_listing_no_anomalies(service):
    listings = [
        make_listing("a", 30.0),
        make_listing("b", 31.0),
        make_listing("c", 29.0),
        make_listing("d", 32.0),
    ]
    result = service.detect_anomalies(listings, {"quantity": 10, "max_lead_time_days": 7})
    normal = next(l for l in result if l["id"] == "a")
    assert normal["anomalies"] == []
