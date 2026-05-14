from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def create_mysql_engine(url: str, echo: bool = False) -> Engine:
    """Create a SQLAlchemy Engine for MySQL.

    Example URL: mysql+pymysql://user:pass@host:3306/chat_service
    """
    engine = create_engine(url, echo=echo, pool_pre_ping=True, future=True)
    return engine


def create_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine, class_=Session, autoflush=False, autocommit=False, expire_on_commit=False, future=True)


@contextmanager
def session_scope(SessionFactory: sessionmaker) -> Generator[Session, None, None]:
    session: Session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

