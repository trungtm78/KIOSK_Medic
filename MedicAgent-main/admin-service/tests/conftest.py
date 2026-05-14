"""Test fixtures for admin-service.

Use SQLite in-memory for fast smoke tests. P3 will add testcontainers MySQL
for MySQL-specific semantics (Codex #12).
"""

import os
import pytest


@pytest.fixture(autouse=True)
def _set_test_env_defaults(monkeypatch):
    # SQLite in-memory: fast smoke tests for app structure only.
    # NOT a substitute for MySQL integration tests (which P3 will add).
    monkeypatch.setenv("ADMIN_DB_URL", "sqlite:///:memory:")
    monkeypatch.setenv("ENV", "test")


@pytest.fixture
def app_client():
    """FastAPI TestClient. Imports app fresh to honour env."""
    import importlib
    import sys

    # Drop cached modules so engine rebuilds from new ADMIN_DB_URL
    for mod in list(sys.modules):
        if mod.startswith("app.core.db") or mod.startswith("app.main"):
            del sys.modules[mod]

    from fastapi.testclient import TestClient
    main = importlib.import_module("app.main")
    return TestClient(main.app)
