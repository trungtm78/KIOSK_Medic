"""P1.2 - Lazy DB engine init (Codex #4 fix).

Previously: `engine = _build_engine()` ran at module import. Test imports
without ADMIN_DB_URL would crash. Now: engine builds on first get_engine()
call, allowing tests to set env vars before triggering connection.
"""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from .settings import get_settings


@lru_cache
def get_engine() -> Engine:
    """Build (and cache) the SQLAlchemy engine on first call."""
    settings = get_settings()
    connect_args = {}
    if settings.ADMIN_DB_URL.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(
        settings.ADMIN_DB_URL,
        echo=False,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


def get_session():
    """FastAPI dependency yielding a session, with commit/rollback handling."""
    engine = get_engine()
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise


# Backwards-compat: many call sites still reference `engine` directly.
# This proxies to the lazy factory so old imports keep working without
# triggering eager init at module import.
class _LazyEngineProxy:
    def __getattr__(self, name):
        return getattr(get_engine(), name)


engine = _LazyEngineProxy()
