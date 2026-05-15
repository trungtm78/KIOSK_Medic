"""Finding #7 - debug.py router must be env-gated.

In development (default), debug endpoints exist for testing.
In production, they MUST 404 - never allow anonymous cache wipe.
"""

import importlib
import sys

import pytest
from fastapi.testclient import TestClient


def _reload_app():
    """Drop cached modules so create_app picks up current APP_ENV."""
    for mod in list(sys.modules):
        if mod.startswith("app.main") or mod.startswith("app.routers"):
            del sys.modules[mod]
    return importlib.import_module("app.main").create_app()


def test_debug_routes_present_in_development(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    app = _reload_app()
    client = TestClient(app)
    # GET /v1/debug/conversations should exist (200 or 404 on data, but route registered)
    response = client.get("/v1/debug/conversations")
    assert response.status_code != 404 or "conversation" in response.text.lower(), (
        "debug route should be registered in development"
    )

    paths = client.get("/v1/chat/openapi.json").json().get("paths", {})
    assert any(p.startswith("/v1/debug/") for p in paths), (
        "debug routes missing from OpenAPI schema in development"
    )


def test_debug_routes_absent_in_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    app = _reload_app()
    client = TestClient(app)

    # GET /v1/debug/conversations should 404 (route not registered)
    response = client.get("/v1/debug/conversations")
    assert response.status_code == 404, (
        f"debug endpoint exposed in production - got {response.status_code}"
    )

    # OpenAPI schema should not list debug routes
    paths = client.get("/v1/chat/openapi.json").json().get("paths", {})
    debug_paths = [p for p in paths if p.startswith("/v1/debug/")]
    assert not debug_paths, (
        f"debug routes leaking into production OpenAPI: {debug_paths}"
    )


def test_debug_delete_all_returns_404_in_production(monkeypatch):
    """The most dangerous endpoint: DELETE /v1/debug/conversations wipes all cache.
    MUST be unreachable in production.
    """
    monkeypatch.setenv("APP_ENV", "production")
    app = _reload_app()
    client = TestClient(app)

    response = client.delete("/v1/debug/conversations")
    assert response.status_code == 404, (
        f"DESTRUCTIVE debug endpoint reachable in production - got {response.status_code}"
    )


def test_default_env_treats_as_development(monkeypatch):
    """No APP_ENV set -> default to development (backwards compat)."""
    monkeypatch.delenv("APP_ENV", raising=False)
    app = _reload_app()
    client = TestClient(app)

    paths = client.get("/v1/chat/openapi.json").json().get("paths", {})
    assert any(p.startswith("/v1/debug/") for p in paths), (
        "default env should expose debug routes for local dev"
    )
