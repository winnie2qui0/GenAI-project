from typing import Optional

# Static fallback rates (USD base). In production, fetch from an exchange-rate API.
EXCHANGE_RATES_TO_USD: dict[str, float] = {
    "USD": 1.0,
    "EUR": 1.08,
    "GBP": 1.27,
    "JPY": 0.0067,
    "CNY": 0.14,
    "TWD": 0.031,
    "KRW": 0.00075,
    "HKD": 0.128,
    "SGD": 0.74,
    "AUD": 0.65,
    "CAD": 0.74,
    "INR": 0.012,
}


def convert_to_usd(amount: float, currency: str) -> Optional[float]:
    rate = EXCHANGE_RATES_TO_USD.get(currency.upper())
    if rate is None:
        return None
    return round(amount * rate, 4)


def format_currency(amount: float, currency: str = "USD") -> str:
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CNY": "¥", "TWD": "NT$"}
    symbol = symbols.get(currency.upper(), currency + " ")
    return f"{symbol}{amount:,.2f}"
