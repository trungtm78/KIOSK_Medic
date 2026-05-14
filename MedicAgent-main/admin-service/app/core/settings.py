"""P1.2 - Centralized pydantic-settings config for admin-service.

Pydantic BaseSettings validates env vars at startup with type checking.
Loaded lazily so tests can override env without import-time side effects.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ADMIN_DB_URL: str = "sqlite:///./admin.db"
    ENV: str = "development"


@lru_cache
def get_settings() -> Settings:
    """Cached accessor - tests can call get_settings.cache_clear() to reload."""
    return Settings()
