"""P0.3 - core-service CORS must come from CORS_ORIGINS env, not wildcard.

We test the parser in isolation (app/core/cors.py) since importing app.main
triggers eager DB init (config.py:86 + directory/db.py:8-15). P1.2 will fix
the eager init; until then, test the parser directly.
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
