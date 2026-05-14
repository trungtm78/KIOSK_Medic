import os
from functools import lru_cache


class Settings:
    chat_service_base_url: str
    request_timeout_seconds: float

    def __init__(self) -> None:
        self.chat_service_base_url = os.getenv(
            "CHAT_SERVICE_BASE_URL",
            # Default suitable for docker-compose internal DNS or local dev
            "http://chat-service:8000",
        ).rstrip("/")
        self.request_timeout_seconds = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

