import os

from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine


def _build_engine() -> Engine:
    """Create the SQLModel engine for the Admin DB."""
    url = os.getenv("ADMIN_DB_URL")
    if not url:
        raise RuntimeError(
            "ADMIN_DB_URL is not configured. Set it to a MySQL URL, e.g. "
            "mysql+pymysql://user:pass@host:3306/medicagent_admin_db"
        )
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, echo=False, pool_pre_ping=True, connect_args=connect_args)


engine = _build_engine()


def get_session():
    with Session(engine) as session:
        yield session
