import pytest

from app.services.scoring_service import ScoringService


class TestScoringService:
    def test_same_input_same_output(self) -> None:
        service = ScoringService()
        listings = [
            {
                "id": "1",
                "price_normalized_usd": 30,
                "lead_time_days": 2,
                "rating": 4.5,
                "review_count": 500,
                "source": "amazon",
            },
            {
                "id": "2",
                "price_normalized_usd": 35,
                "lead_time_days": 3,
                "rating": 4.7,
                "review_count": 1200,
                "source": "amazon",
            },
        ]
        requirement = {"max_lead_time_days": 5}
        result1 = service.calculate_scores(listings, requirement)
        result2 = service.calculate_scores(listings, requirement)
        assert result1 == result2

    def test_score_reproducible_from_weights(self) -> None:
        service = ScoringService()
        listings = [
            {
                "id": "a",
                "price_normalized_usd": 10,
                "lead_time_days": 1,
                "rating": 5,
                "review_count": 2000,
                "source": "amazon",
            },
            {
                "id": "b",
                "price_normalized_usd": 10,
                "lead_time_days": 1,
                "rating": 5,
                "review_count": 2000,
                "source": "alibaba",
            },
        ]
        w1 = {"price": 1.0, "delivery": 0.0, "rating": 0.0, "trust": 0.0}
        w2 = {"price": 0.0, "delivery": 0.0, "rating": 0.0, "trust": 1.0}
        r1 = service.calculate_scores(listings, {"max_lead_time_days": 7}, weights=w1)
        r2 = service.calculate_scores(listings, {"max_lead_time_days": 7}, weights=w2)
        by_source = {str(x["listing_id"]): x["final_score"] for x in r2}
        assert by_source["a"] != by_source["b"]
        assert r1[0]["final_score"] == r1[1]["final_score"]

    def test_lowest_price_gets_max_price_score(self) -> None:
        service = ScoringService()
        listings = [
            {
                "id": "1",
                "price_normalized_usd": 10,
                "lead_time_days": 1,
                "rating": 4,
                "review_count": 50,
                "source": "amazon",
            },
            {
                "id": "2",
                "price_normalized_usd": 20,
                "lead_time_days": 1,
                "rating": 4,
                "review_count": 50,
                "source": "amazon",
            },
        ]
        out = service.calculate_scores(listings, {"max_lead_time_days": 7})
        by_id = {str(x["listing_id"]): x for x in out}
        assert by_id["1"]["price_score"] == 100.0
