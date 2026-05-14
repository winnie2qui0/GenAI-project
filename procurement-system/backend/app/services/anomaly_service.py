import statistics
from typing import Any


class AnomalyDetectionService:
    """Flag suspicious listings; never drop rows."""

    def detect_anomalies(self, listings: list[dict[str, Any]], user_requirement: dict[str, Any]) -> list[dict[str, Any]]:
        prices = [float(l["price_normalized_usd"]) for l in listings]
        median_price = statistics.median(prices)

        if len(prices) > 3:
            qs = statistics.quantiles(prices, n=4)
            q1, q3 = qs[0], qs[2]
            iqr = q3 - q1
            upper_bound = q3 + 1.5 * iqr
            lower_bound = q1 - 1.5 * iqr
        else:
            upper_bound = max(prices) * 1.5
            lower_bound = min(prices) * 0.5

        user_qty = int(user_requirement.get("quantity") or 1)
        user_max_days = user_requirement.get("max_lead_time_days")
        if user_max_days is None:
            user_max_days = 7

        for listing in listings:
            anomalies: list[dict[str, Any]] = []
            p = float(listing["price_normalized_usd"])

            if p > upper_bound:
                anomalies.append(
                    {
                        "type": "price_high",
                        "severity": "warning",
                        "message": f"Price ${p:.2f} is unusually high (median: ${median_price:.2f})",
                    }
                )
            elif p < lower_bound:
                anomalies.append(
                    {
                        "type": "price_low",
                        "severity": "warning",
                        "message": f"Price ${p:.2f} is suspiciously low (possible fake)",
                    }
                )

            listing_moq = int(listing.get("moq") or 1)
            if listing_moq > user_qty:
                anomalies.append(
                    {
                        "type": "moq_too_high",
                        "severity": "error",
                        "message": f"MOQ {listing_moq} exceeds your needed quantity {user_qty}",
                    }
                )

            actual_days = listing.get("lead_time_days")
            if actual_days is None:
                actual_days = 999
            if actual_days > user_max_days * 3:
                anomalies.append(
                    {
                        "type": "lead_time_too_long",
                        "severity": "warning",
                        "message": f"Lead time {actual_days} days far exceeds your {user_max_days} day requirement",
                    }
                )

            if not listing.get("rating") and not listing.get("review_count"):
                anomalies.append(
                    {
                        "type": "missing_reviews",
                        "severity": "info",
                        "message": "No customer reviews available — limited social proof",
                    }
                )

            if not listing.get("seller_name"):
                anomalies.append(
                    {
                        "type": "missing_seller",
                        "severity": "warning",
                        "message": "Seller information not available",
                    }
                )

            listing["anomalies"] = anomalies

        return listings
