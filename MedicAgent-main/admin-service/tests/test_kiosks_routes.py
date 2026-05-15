"""W4.7 - Admin endpoints for kiosk token management."""

import pytest
from sqlmodel import Session

from app.core.db import get_engine
from app.models import Tenant


@pytest.fixture
def tenant_id():
    """Insert a tenant to attach tokens to."""
    engine = get_engine()
    with Session(engine) as s:
        tenant = Tenant(code="t1", name="Tenant 1")
        s.add(tenant)
        s.commit()
        s.refresh(tenant)
        return tenant.id


def test_create_kiosk_requires_admin_api_key(app_client, tenant_id, monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "secret-admin-key")
    monkeypatch.setenv("APP_ENV", "production")  # force require

    response = app_client.post(
        f"/v1/tenants/{tenant_id}/kiosks",
        json={"kiosk_name": "reception-1"},
    )
    assert response.status_code == 401


def test_create_kiosk_returns_raw_token_once(app_client, tenant_id, monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "secret-admin-key")
    response = app_client.post(
        f"/v1/tenants/{tenant_id}/kiosks",
        json={"kiosk_name": "reception-1"},
        headers={"X-Admin-API-Key": "secret-admin-key"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["token"].startswith("kt_")
    assert len(data["token"]) >= 35
    assert data["kiosk_name"] == "reception-1"
    assert data["token_prefix"] == data["token"][:12]


def test_create_kiosk_for_unknown_tenant_returns_404(app_client, monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "k")
    response = app_client.post(
        "/v1/tenants/9999/kiosks",
        json={"kiosk_name": "x"},
        headers={"X-Admin-API-Key": "k"},
    )
    assert response.status_code == 404


def test_list_kiosks_returns_metadata_only_not_token(app_client, tenant_id, monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "k")
    # Create one
    app_client.post(
        f"/v1/tenants/{tenant_id}/kiosks",
        json={"kiosk_name": "reception-1"},
        headers={"X-Admin-API-Key": "k"},
    )

    response = app_client.get(
        f"/v1/tenants/{tenant_id}/kiosks",
        headers={"X-Admin-API-Key": "k"},
    )
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["kiosk_name"] == "reception-1"
    assert "token" not in items[0]  # raw token NEVER returned in list
    assert items[0]["token_prefix"].startswith("kt_")


def test_revoke_kiosk_marks_revoked_at(app_client, tenant_id, monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "k")
    created = app_client.post(
        f"/v1/tenants/{tenant_id}/kiosks",
        json={"kiosk_name": "reception-1"},
        headers={"X-Admin-API-Key": "k"},
    ).json()

    response = app_client.delete(
        f"/v1/tenants/{tenant_id}/kiosks/{created['id']}",
        headers={"X-Admin-API-Key": "k"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "revoked"

    # Subsequent list shows revoked_at
    items = app_client.get(
        f"/v1/tenants/{tenant_id}/kiosks",
        headers={"X-Admin-API-Key": "k"},
    ).json()
    assert items[0]["revoked_at"] is not None


def test_revoke_twice_is_idempotent(app_client, tenant_id, monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "k")
    created = app_client.post(
        f"/v1/tenants/{tenant_id}/kiosks",
        json={"kiosk_name": "reception-1"},
        headers={"X-Admin-API-Key": "k"},
    ).json()

    app_client.delete(
        f"/v1/tenants/{tenant_id}/kiosks/{created['id']}",
        headers={"X-Admin-API-Key": "k"},
    )
    response = app_client.delete(
        f"/v1/tenants/{tenant_id}/kiosks/{created['id']}",
        headers={"X-Admin-API-Key": "k"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "already_revoked"
