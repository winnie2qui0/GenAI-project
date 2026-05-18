from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/procurement_db"

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_provider: str = "openai"
    llm_model: str = "gpt-4-turbo"

    crawler_delay_min: float = 1.0
    crawler_delay_max: float = 5.0
    crawler_timeout: int = 30
    use_proxy_pool: bool = False

    cache_ttl_hours: int = 48

    scoring_weight_price: float = 0.30
    scoring_weight_delivery: float = 0.30
    scoring_weight_rating: float = 0.20
    scoring_weight_trust: float = 0.20

    app_env: str = "development"
    log_level: str = "INFO"
    secret_key: str = "change-me-in-production"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
