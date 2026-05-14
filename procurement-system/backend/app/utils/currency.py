from decimal import Decimal
from typing import Any

_RATES_TO_USD: dict[str, Decimal] = {
    "USD": Decimal("1"),
    "TWD": Decimal("0.031"),
    "CNY": Decimal("0.14"),
    "EUR": Decimal("1.08"),
    "GBP": Decimal("1.27"),
}


def to_usd(amount: Decimal | float, currency: str) -> Decimal:
    cur = (currency or "USD").upper()
    rate = _RATES_TO_USD.get(cur, Decimal("1"))
    return (Decimal(str(amount)) * rate).quantize(Decimal("0.01"))
