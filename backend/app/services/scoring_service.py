from typing import Any
from app.config import get_settings

settings = get_settings()


class ScoringService:
    """
    Deterministic scoring — same input always yields same output.
    No LLM, no randomness, fully auditable.
    """

    DEFAULT_WEIGHTS = {
        "price": settings.scoring_weight_price,
        "delivery": settings.scoring_weight_delivery,
        "rating": settings.scoring_weight_rating,
        "trust": settings.scoring_weight_trust,
    }

    PLATFORM_TRUST_SCORES: dict[str, float] = {
        "amazon": 95,
        "amazon_business": 95,
        "alibaba": 70,
        "pchome": 85,
        "local_b2b": 75,
        "ebay": 60,
        "unknown": 50,
    }

    def calculate_scores(
        self,
        listings: list[dict[str, Any]],
        user_requirement: dict[str, Any],
        weights: dict[str, float] | None = None,
    ) -> list[dict[str, Any]]:
        weights = weights or self.DEFAULT_WEIGHTS

        if not listings:
            return []

        prices = [float(l["price_normalized_usd"] or 0) for l in listings]
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price if max_price != min_price else 1.0

        scored = []
        for listing in listings:
            price_val = float(listing["price_normalized_usd"] or 0)
            price_score = ((max_price - price_val) / price_range) * 100

            user_max_days = user_requirement.get("max_lead_time_days") or 7
            actual_days = listing.get("lead_time_days") or 999
            if actual_days <= user_max_days:
                delivery_score = 100.0
            else:
                delivery_score = max(0.0, 100.0 - (actual_days - user_max_days) * 10)

            rating = float(listing.get("rating") or 0)
            review_count = int(listing.get("review_count") or 0)
            base_rating_score = (rating / 5.0) * 100
            if review_count > 1000:
                review_weight = 1.1
            elif review_count > 100:
                review_weight = 1.0
            elif review_count > 10:
                review_weight = 0.9
            else:
                review_weight = 0.8
            rating_score = min(100.0, base_rating_score * review_weight)

            source = listing.get("source", "unknown")
            trust_score = float(self.PLATFORM_TRUST_SCORES.get(source, 50))

            final_score = (
                weights["price"] * price_score
                + weights["delivery"] * delivery_score
                + weights["rating"] * rating_score
                + weights["trust"] * trust_score
            )

            scored.append({
                "listing_id": listing["id"],
                "price_score": round(price_score, 2),
                "delivery_score": round(delivery_score, 2),
                "rating_score": round(rating_score, 2),
                "trust_score": round(trust_score, 2),
                "final_score": round(final_score, 2),
                "weights_used": weights,
            })

        scored.sort(key=lambda x: x["final_score"], reverse=True)
        for i, item in enumerate(scored):
            item["rank"] = i + 1

        return scored
