"""CORS origin parsing for core-service.

Isolated from main.py so tests don't trigger eager DB init.
"""

import os

_DEV_DEFAULT_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


def parse_cors_origins() -> list[str]:
    """Parse CORS_ORIGINS env var into a list of origins.

    Returns dev defaults if env var is unset or empty.
    """
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if not raw:
        return list(_DEV_DEFAULT_ORIGINS)
    return [o.strip() for o in raw.split(",") if o.strip()]
