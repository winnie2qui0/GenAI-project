from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://procurement:procurement@localhost:5432/procurement_db"

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    llm_provider: str = "openai"  # openai | anthropic
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

    demo_user_id: str = "demo-user"


@lru_cache
def get_settings() -> Settings:
    return Settings()
