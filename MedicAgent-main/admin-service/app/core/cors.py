"""CORS origin parsing for admin-service.

Same pattern as chat-service and core-service. Reads CORS_ORIGINS env var
(comma-separated). Falls back to dev defaults if unset.
"""

import os

_DEV_DEFAULT_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


def parse_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if not raw:
        return list(_DEV_DEFAULT_ORIGINS)
    return [o.strip() for o in raw.split(",") if o.strip()]
