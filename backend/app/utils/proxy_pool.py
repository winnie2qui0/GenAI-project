import random
from typing import Optional
from app.config import get_settings

settings = get_settings()

# In production, populate from a proxy provider API
PROXY_LIST: list[str] = []


def get_proxy() -> Optional[str]:
    if not settings.use_proxy_pool or not PROXY_LIST:
        return None
    return random.choice(PROXY_LIST)


def get_proxy_dict() -> Optional[dict]:
    proxy = get_proxy()
    if not proxy:
        return None
    return {"http://": proxy, "https://": proxy}
