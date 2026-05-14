"""P0.2 - CORS configuration must come from CORS_ORIGINS env var, not wildcard."""

import importlib
import os
import sys


def _reload_app():
    """Force re-import of app.main after env vars change."""
    for mod in list(sys.modules):
        if mod.startswith("app.main"):
            del sys.modules[mod]
    return importlib.import_module("app.main").app


def test_cors_origins_loaded_from_env(monkeypatch):
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    app = _reload_app()

    cors_mw = next(
        (m for m in app.user_middleware if m.cls.__name__ == "CORSMiddleware"),
        None,
    )
    assert cors_mw is not None, "CORSMiddleware not registered"

    origins = cors_mw.kwargs.get("allow_origins", [])
    assert "http://localhost:3000" in origins
    assert "http://127.0.0.1:3000" in origins
    assert "*" not in origins, "wildcard origin must not be present when CORS_ORIGINS set"


def test_cors_origins_default_when_env_missing(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    app = _reload_app()

    cors_mw = next(
        (m for m in app.user_middleware if m.cls.__name__ == "CORSMiddleware"),
        None,
    )
    assert cors_mw is not None

    origins = cors_mw.kwargs.get("allow_origins", [])
    # Default for dev: localhost only, not wildcard
    assert origins == ["http://localhost:3000", "http://127.0.0.1:3000"], (
        f"expected dev defaults, got {origins}"
    )


def test_cors_origins_strips_whitespace(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", " http://a.com , http://b.com ")
    app = _reload_app()

    cors_mw = next(
        (m for m in app.user_middleware if m.cls.__name__ == "CORSMiddleware"),
        None,
    )
    origins = cors_mw.kwargs.get("allow_origins", [])
    assert origins == ["http://a.com", "http://b.com"]
