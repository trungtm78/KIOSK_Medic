from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

Base = declarative_base()

engine = create_engine(
    settings.DIRECTORY_DATABASE_URL,
    pool_pre_ping=True,
)

# Ensure SQLAlchemy metadata knows about all models before creating tables
import app.directory.models  # noqa: E402,F401

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()