from typing import Any

from app.config import get_settings


class ScoringService:
    """Deterministic scoring: same normalized inputs produce identical ranks."""

    DEFAULT_WEIGHTS = {
        "price": 0.30,
        "delivery": 0.30,
        "rating": 0.20,
        "trust": 0.20,
    }

    PLATFORM_TRUST_SCORES = {
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
        weights = weights or dict(self.DEFAULT_WEIGHTS)

        prices = [float(l["price_normalized_usd"]) for l in listings]
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price if max_price != min_price else 1.0

        scored: list[dict[str, Any]] = []
        for listing in listings:
            p = float(listing["price_normalized_usd"])
            price_score = ((max_price - p) / price_range) * 100

            user_max_days = user_requirement.get("max_lead_time_days")
            if user_max_days is None:
                user_max_days = 7
            actual_days = listing.get("lead_time_days")
            if actual_days is None:
                actual_days = 999
            if actual_days <= user_max_days:
                delivery_score = 100.0
            else:
                delivery_score = max(0.0, 100.0 - (actual_days - user_max_days) * 10)

            rating = float(listing.get("rating") or 0)
            review_count = int(listing.get("review_count") or 0)
            base_rating_score = (rating / 5.0) * 100.0 if rating else 0.0

            if review_count > 1000:
                review_weight = 1.1
            elif review_count > 100:
                review_weight = 1.0
            elif review_count > 10:
                review_weight = 0.9
            else:
                review_weight = 0.8

            rating_score = min(100.0, base_rating_score * review_weight)

            source = listing.get("source") or "unknown"
            trust_score = float(self.PLATFORM_TRUST_SCORES.get(source, 50))

            final_score = (
                weights["price"] * price_score
                + weights["delivery"] * delivery_score
                + weights["rating"] * rating_score
                + weights["trust"] * trust_score
            )

            lid = listing["id"]
            scored.append(
                {
                    "listing_id": lid,
                    "price_score": round(price_score, 2),
                    "delivery_score": round(delivery_score, 2),
                    "rating_score": round(rating_score, 2),
                    "trust_score": round(trust_score, 2),
                    "final_score": round(final_score, 2),
                    "weights_used": weights,
                    "_sort_price": p,
                }
            )

        scored.sort(
            key=lambda x: (
                -x["final_score"],
                -x["price_score"],
                x["_sort_price"],
                str(x["listing_id"]),
            )
        )
        for i, item in enumerate(scored):
            item["rank"] = i + 1
            item.pop("_sort_price", None)

        return scored

    @staticmethod
    def weights_from_settings() -> dict[str, float]:
        s = get_settings()
        return {
            "price": float(s.scoring_weight_price),
            "delivery": float(s.scoring_weight_delivery),
            "rating": float(s.scoring_weight_rating),
            "trust": float(s.scoring_weight_trust),
        }
