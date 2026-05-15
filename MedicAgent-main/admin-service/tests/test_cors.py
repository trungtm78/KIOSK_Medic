"""Finding #3 - admin-service CORS must come from CORS_ORIGINS env, not missing/wildcard.

Tests parse_cors_origins() in isolation (app/core/cors.py) to avoid eager DB init
on import. Then verifies main.py wires it into CORSMiddleware.
"""

from app.core.cors import parse_cors_origins


def test_cors_origins_loaded_from_env(monkeypatch):
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    origins = parse_cors_origins()
    assert origins == ["http://localhost:3000", "http://127.0.0.1:3000"]
    assert "*" not in origins


def test_cors_origins_default_when_env_missing(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    origins = parse_cors_origins()
    assert origins == ["http://localhost:3000", "http://127.0.0.1:3000"]


def test_cors_origins_default_when_env_empty(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "")
    origins = parse_cors_origins()
    assert origins == ["http://localhost:3000", "http://127.0.0.1:3000"]


def test_cors_origins_strips_whitespace(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", " http://a.com , http://b.com ")
    origins = parse_cors_origins()
    assert origins == ["http://a.com", "http://b.com"]


def test_cors_origins_drops_empty_entries(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://a.com,,http://b.com,")
    origins = parse_cors_origins()
    assert origins == ["http://a.com", "http://b.com"]


def test_admin_app_registers_cors_middleware(app_client):
    """Smoke check: admin-service has CORSMiddleware wired up (not missing)."""
    app = app_client.app
    cors_mw = next(
        (m for m in app.user_middleware if m.cls.__name__ == "CORSMiddleware"),
        None,
    )
    assert cors_mw is not None, (
        "admin-service is missing CORSMiddleware - Finding #3 not yet fixed"
    )
    assert "*" not in cors_mw.kwargs.get("allow_origins", []), (
        "admin-service still uses wildcard origin"
    )
