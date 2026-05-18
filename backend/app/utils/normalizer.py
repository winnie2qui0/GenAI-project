import re
from typing import Optional


def normalize_brand(brand: Optional[str]) -> Optional[str]:
    if not brand:
        return None
    return brand.strip().upper()


def normalize_model(model: Optional[str]) -> Optional[str]:
    if not model:
        return None
    return re.sub(r"\s+", "", model.strip().upper())


def extract_gtin(text: str) -> Optional[str]:
    patterns = [
        r"\b(\d{13})\b",   # EAN-13
        r"\b(\d{12})\b",   # UPC-A
        r"\b(\d{8})\b",    # EAN-8
        r"\b(B0[A-Z0-9]{8})\b",  # ASIN
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def parse_lead_time(text: str) -> Optional[int]:
    patterns = [
        (r"(\d+)\s*-\s*(\d+)\s*(business\s*)?days?", "range"),
        (r"(\d+)\s*(business\s*)?days?", "single"),
        (r"(\d+)\s*weeks?", "weeks"),
    ]
    for pattern, kind in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if kind == "range":
                return int(match.group(2))  # use upper bound
            elif kind == "single":
                return int(match.group(1))
            elif kind == "weeks":
                return int(match.group(1)) * 7
    return None


def parse_rating(text: str) -> Optional[float]:
    match = re.search(r"(\d+\.?\d*)\s*(?:out\s*of\s*5|/\s*5|★)", text, re.IGNORECASE)
    if match:
        return min(5.0, float(match.group(1)))
    return None
