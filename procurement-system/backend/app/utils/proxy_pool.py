"""Optional proxy rotation for crawlers (MVP stub)."""

from app.config import get_settings


def next_proxy() -> str | None:
    if not get_settings().use_proxy_pool:
        return None
    return None
