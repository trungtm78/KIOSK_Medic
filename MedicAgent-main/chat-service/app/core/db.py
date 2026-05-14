from __future__ import annotations

import os
from typing import Generator, Optional
from sqlalchemy.orm import Session, sessionmaker

from ..repositories.base import create_mysql_engine, create_session_factory, session_scope
from ..models.base import Base


_SESSION_FACTORY: Optional[sessionmaker] = None


def get_session_factory() -> sessionmaker:
    """Return a SQLAlchemy Session factory bound to MySQL.

    Reads CHAT_DB_URL from environment, e.g.:
    mysql+pymysql://user:pass@host:3306/chat_service
    """
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        url = os.environ.get("CHAT_DB_URL")
        if not url:
            raise RuntimeError(
                "CHAT_DB_URL is not configured; set to a MySQL URL, e.g., "
                "mysql+pymysql://user:pass@host:3306/chat_service"
            )
        engine = create_mysql_engine(url)
        # Ensure database schema exists before sessions are handed out.
        Base.metadata.create_all(engine)
        _SESSION_FACTORY = create_session_factory(engine)
    return _SESSION_FACTORY


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session and handles commit/rollback."""
    SessionFactory = get_session_factory()
    db: Session = SessionFactory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

__all__ = ["get_session_factory", "session_scope", "get_db"]
