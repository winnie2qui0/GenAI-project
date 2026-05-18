import statistics
from typing import Any


class AnomalyDetectionService:
    """Detect anomalies and flag them — never exclude listings."""

    def detect_anomalies(
        self,
        listings: list[dict[str, Any]],
        user_requirement: dict[str, Any],
    ) -> list[dict[str, Any]]:
        prices = [float(l["price_normalized_usd"] or 0) for l in listings]

        if not prices:
            return listings

        median_price = statistics.median(prices)

        if len(prices) >= 4:
            q1 = statistics.quantiles(prices, n=4)[0]
            q3 = statistics.quantiles(prices, n=4)[2]
            iqr = q3 - q1
            upper_bound = q3 + 1.5 * iqr
            lower_bound = max(0, q1 - 1.5 * iqr)
        else:
            upper_bound = max(prices) * 1.5
            lower_bound = min(prices) * 0.5

        for listing in listings:
            anomalies: list[dict[str, Any]] = []
            price = float(listing["price_normalized_usd"] or 0)

            if price > upper_bound:
                anomalies.append({
                    "type": "price_high",
                    "severity": "warning",
                    "message": f"Price ${price:.2f} is unusually high (median: ${median_price:.2f})",
                })
            elif price < lower_bound and price > 0:
                anomalies.append({
                    "type": "price_low",
                    "severity": "warning",
                    "message": f"Price ${price:.2f} is suspiciously low — possible counterfeit",
                })

            user_qty = user_requirement.get("quantity", 1) or 1
            listing_moq = int(listing.get("moq") or 1)
            if listing_moq > user_qty:
                anomalies.append({
                    "type": "moq_too_high",
                    "severity": "error",
                    "message": f"MOQ {listing_moq} exceeds your needed quantity {user_qty}",
                })

            user_max_days = user_requirement.get("max_lead_time_days") or 7
            actual_days = listing.get("lead_time_days") or 0
            if actual_days and actual_days > user_max_days * 3:
                anomalies.append({
                    "type": "lead_time_too_long",
                    "severity": "warning",
                    "message": f"Lead time {actual_days}d far exceeds your {user_max_days}d requirement",
                })

            if not listing.get("rating") and not listing.get("review_count"):
                anomalies.append({
                    "type": "missing_reviews",
                    "severity": "info",
                    "message": "No customer reviews — limited social proof",
                })

            if not listing.get("seller_name"):
                anomalies.append({
                    "type": "missing_seller",
                    "severity": "warning",
                    "message": "Seller information not available",
                })

            listing["anomalies"] = anomalies

        return listings
