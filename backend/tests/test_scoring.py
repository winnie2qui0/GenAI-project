import pytest
from app.services.scoring_service import ScoringService


@pytest.fixture
def service():
    return ScoringService()


@pytest.fixture
def sample_listings():
    return [
        {
            "id": "1",
            "price_normalized_usd": 30.0,
            "lead_time_days": 2,
            "rating": 4.5,
            "review_count": 500,
            "source": "amazon",
        },
        {
            "id": "2",
            "price_normalized_usd": 35.0,
            "lead_time_days": 3,
            "rating": 4.7,
            "review_count": 1200,
            "source": "amazon",
        },
        {
            "id": "3",
            "price_normalized_usd": 25.0,
            "lead_time_days": 7,
            "rating": 3.8,
            "review_count": 45,
            "source": "alibaba",
        },
    ]


def test_same_input_same_output(service, sample_listings):
    """Scoring must be deterministic: same input → same output."""
    req = {"max_lead_time_days": 5}
    result1 = service.calculate_scores(sample_listings, req)
    result2 = service.calculate_scores(sample_listings, req)
    assert result1 == result2


def test_lowest_price_gets_max_price_score(service):
    """Lowest priced listing should receive price_score = 100."""
    listings = [
        {"id": "cheap", "price_normalized_usd": 10.0, "lead_time_days": 3, "rating": 4.0, "review_count": 100, "source": "amazon"},
        {"id": "expensive", "price_normalized_usd": 50.0, "lead_time_days": 3, "rating": 4.0, "review_count": 100, "source": "amazon"},
    ]
    result = service.calculate_scores(listings, {"max_lead_time_days": 5})
    cheap = next(r for r in result if r["listing_id"] == "cheap")
    assert cheap["price_score"] == 100.0


def test_highest_price_gets_zero_price_score(service):
    """Highest priced listing should receive price_score = 0."""
    listings = [
        {"id": "cheap", "price_normalized_usd": 10.0, "lead_time_days": 3, "rating": 4.0, "review_count": 100, "source": "amazon"},
        {"id": "expensive", "price_normalized_usd": 50.0, "lead_time_days": 3, "rating": 4.0, "review_count": 100, "source": "amazon"},
    ]
    result = service.calculate_scores(listings, {"max_lead_time_days": 5})
    expensive = next(r for r in result if r["listing_id"] == "expensive")
    assert expensive["price_score"] == 0.0


def test_delivery_within_limit_scores_100(service):
    """Listing delivering within user's deadline scores 100 on delivery."""
    listings = [
        {"id": "fast", "price_normalized_usd": 30.0, "lead_time_days": 2, "rating": 4.0, "review_count": 100, "source": "amazon"},
    ]
    result = service.calculate_scores(listings, {"max_lead_time_days": 5})
    assert result[0]["delivery_score"] == 100.0


def test_delivery_over_limit_deducted(service):
    """Listing 3 days late should lose 30 delivery score points."""
    listings = [
        {"id": "slow", "price_normalized_usd": 30.0, "lead_time_days": 8, "rating": 4.0, "review_count": 100, "source": "amazon"},
    ]
    result = service.calculate_scores(listings, {"max_lead_time_days": 5})
    assert result[0]["delivery_score"] == 70.0


def test_ranks_assigned_correctly(service, sample_listings):
    """Ranks start at 1 and are contiguous."""
    result = service.calculate_scores(sample_listings, {"max_lead_time_days": 5})
    ranks = sorted(r["rank"] for r in result)
    assert ranks == list(range(1, len(sample_listings) + 1))


def test_rank_1_has_highest_score(service, sample_listings):
    """Rank 1 listing must have the highest final score."""
    result = service.calculate_scores(sample_listings, {"max_lead_time_days": 5})
    rank1 = next(r for r in result if r["rank"] == 1)
    assert rank1["final_score"] == max(r["final_score"] for r in result)


def test_custom_weights_applied(service):
    """Custom weights must produce different but predictable scores."""
    listings = [
        {"id": "a", "price_normalized_usd": 10.0, "lead_time_days": 1, "rating": 5.0, "review_count": 1000, "source": "amazon"},
        {"id": "b", "price_normalized_usd": 50.0, "lead_time_days": 1, "rating": 5.0, "review_count": 1000, "source": "amazon"},
    ]
    # Price-heavy weights: cheapest should rank 1
    price_weights = {"price": 0.90, "delivery": 0.05, "rating": 0.03, "trust": 0.02}
    result = service.calculate_scores(listings, {}, weights=price_weights)
    assert result[0]["listing_id"] == "a"


def test_empty_listings_returns_empty(service):
    result = service.calculate_scores([], {})
    assert result == []


def test_single_listing_scores_100_on_price(service):
    """With one listing, price_range = 1, so it gets max price score."""
    listings = [
        {"id": "solo", "price_normalized_usd": 99.0, "lead_time_days": 2, "rating": 4.0, "review_count": 100, "source": "amazon"},
    ]
    result = service.calculate_scores(listings, {"max_lead_time_days": 5})
    assert result[0]["rank"] == 1
    assert result[0]["price_score"] == 100.0


def test_trust_score_reflects_platform(service):
    """Platform trust scores are applied from the lookup table."""
    listings = [
        {"id": "amz", "price_normalized_usd": 30.0, "lead_time_days": 2, "rating": 4.0, "review_count": 100, "source": "amazon"},
        {"id": "ali", "price_normalized_usd": 30.0, "lead_time_days": 2, "rating": 4.0, "review_count": 100, "source": "alibaba"},
    ]
    result = service.calculate_scores(listings, {"max_lead_time_days": 5})
    amz = next(r for r in result if r["listing_id"] == "amz")
    ali = next(r for r in result if r["listing_id"] == "ali")
    assert amz["trust_score"] > ali["trust_score"]
