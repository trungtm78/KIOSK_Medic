"""Wedge 4.2 - FastAPI dependency to verify X-Kiosk-Token header.

These tests use a TestClient with mounted endpoint that exercises the
dependency, simulating what chat/core services will do.
"""

from datetime import datetime, timedelta

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.kiosk_auth import (
    extract_prefix,
    generate_token,
    hash_token,
    verify_kiosk_token_dependency,
)
from app.core.db import get_engine
from app.models import KioskToken, Tenant


@pytest.fixture
def app_with_protected_route():
    """Minimal FastAPI app with one endpoint guarded by token dependency."""
    app = FastAPI()

    @app.get("/protected")
    def protected_endpoint(principal=Depends(verify_kiosk_token_dependency)):
        return {"tenant_id": principal.tenant_id, "kiosk_name": principal.kiosk_name}

    return app


@pytest.fixture
def db_session():
    """SQLite file-based DB (from conftest autouse fixture) with tables created.

    Yields a session for setup, then closes it. Tests can also use this fixture
    just to ensure tables exist.
    """
    from sqlmodel import SQLModel
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def valid_token_and_tenant():
    """Insert tenant + token via an isolated session, commit + close so the
    auth dependency (running in TestClient worker thread) sees the data.

    Returns (raw_token, tenant_id).
    """
    from sqlmodel import SQLModel
    engine = get_engine()
    SQLModel.metadata.create_all(engine)

    raw = generate_token()
    with Session(engine) as session:
        tenant = Tenant(code="t1", name="Tenant 1")
        session.add(tenant)
        session.commit()
        session.refresh(tenant)

        token_row = KioskToken(
            tenant_id=tenant.id,
            kiosk_name="reception-1",
            token_hash=hash_token(raw),
            token_prefix=extract_prefix(raw),
        )
        session.add(token_row)
        session.commit()
        return raw, tenant.id


def test_request_without_token_returns_401(app_with_protected_route):
    client = TestClient(app_with_protected_route)
    response = client.get("/protected")
    assert response.status_code == 401
    assert "token" in response.json().get("detail", "").lower()


def test_request_with_malformed_token_returns_401(app_with_protected_route):
    client = TestClient(app_with_protected_route)
    response = client.get("/protected", headers={"X-Kiosk-Token": "not-a-real-token"})
    assert response.status_code == 401


def test_request_with_unknown_token_returns_401(app_with_protected_route, db_session):
    """Tables exist (db_session fixture) but token isn't stored."""
    client = TestClient(app_with_protected_route)
    response = client.get(
        "/protected",
        headers={"X-Kiosk-Token": "kt_unknown_token_that_isnt_in_db_xxxx"},
    )
    assert response.status_code == 401


def test_request_with_valid_token_returns_200_with_principal(
    app_with_protected_route, valid_token_and_tenant
):
    raw, tenant_id = valid_token_and_tenant
    client = TestClient(app_with_protected_route)
    response = client.get("/protected", headers={"X-Kiosk-Token": raw})
    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == tenant_id
    assert data["kiosk_name"] == "reception-1"


def test_request_with_revoked_token_returns_401(
    app_with_protected_route, valid_token_and_tenant
):
    raw, _ = valid_token_and_tenant
    # Revoke via fresh session
    from sqlmodel import select
    engine = get_engine()
    with Session(engine) as session:
        row = session.exec(
            select(KioskToken).where(KioskToken.token_prefix == extract_prefix(raw))
        ).first()
        row.revoked_at = datetime.utcnow()
        session.add(row)
        session.commit()

    client = TestClient(app_with_protected_route)
    response = client.get("/protected", headers={"X-Kiosk-Token": raw})
    assert response.status_code == 401
    detail = response.json().get("detail", "").lower()
    assert "revoked" in detail or "expired" in detail


def test_request_with_expired_token_returns_401(
    app_with_protected_route, valid_token_and_tenant
):
    raw, _ = valid_token_and_tenant
    from sqlmodel import select
    engine = get_engine()
    with Session(engine) as session:
        row = session.exec(
            select(KioskToken).where(KioskToken.token_prefix == extract_prefix(raw))
        ).first()
        row.expires_at = datetime.utcnow() - timedelta(hours=1)
        session.add(row)
        session.commit()

    client = TestClient(app_with_protected_route)
    response = client.get("/protected", headers={"X-Kiosk-Token": raw})
    assert response.status_code == 401
