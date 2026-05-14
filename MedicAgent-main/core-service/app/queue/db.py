from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

QueueBase = declarative_base()

queue_engine = create_engine(
    settings.QUEUE_DATABASE_URL,
    pool_pre_ping=True,
)

import app.queue.models  # noqa: E402,F401

QueueBase.metadata.create_all(bind=queue_engine)

QueueSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=queue_engine)


def get_queue_db():
    db = QueueSessionLocal()
    try:
        yield db
    finally:
        db.close()