"""Test fixtures for admin-service.

Use SQLite file-based shared in-memory so multiple engine instances
within one test all see the same tables. (`:memory:` alone gives each
engine its own isolated DB - breaks dependencies that build their own
engine via `get_engine()`.)
"""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _set_test_env_defaults(monkeypatch, tmp_path):
    # Temp file SQLite, fresh per test. Persists across multiple engine
    # instances in the same test (unlike `:memory:`).
    db_file = tmp_path / "admin_test.db"
    monkeypatch.setenv("ADMIN_DB_URL", f"sqlite:///{db_file}")
    monkeypatch.setenv("ENV", "test")

    # Drop cached settings + engine so they pick up the new ADMIN_DB_URL
    from app.core import settings as _settings_mod
    from app.core import db as _db_mod
    _settings_mod.get_settings.cache_clear()
    _db_mod.get_engine.cache_clear()

    # Pre-create all tables on the fresh engine so any test (even those that
    # don't use the db_session fixture) finds tables when the auth dependency
    # queries them. Avoids 500 errors when an unauthenticated request hits
    # an endpoint that builds its own DB session.
    from sqlmodel import SQLModel
    from app import models  # noqa: F401 - register model classes with metadata
    SQLModel.metadata.create_all(_db_mod.get_engine())


@pytest.fixture
def app_client():
    """FastAPI TestClient. Imports app fresh to honour env.

    NOTE: We only reload `app.main`, NOT `app.core.db`. Deleting `app.core.db`
    from sys.modules creates a NEW `get_engine` function on re-import, breaking
    the cache invariant that the auth dependency relies on (it imports the
    function from `app.core.db` lazily and expects the same cached engine the
    test setup used).
    """
    import importlib
    import sys

    # Reload only app.main and its submodules that capture engine references.
    # Leave app.core.db alone - we use get_engine.cache_clear() instead.
    for mod in list(sys.modules):
        if mod == "app.main" or mod.startswith("app.routers") or mod.startswith("app.seed"):
            del sys.modules[mod]

    from fastapi.testclient import TestClient
    main = importlib.import_module("app.main")
    return TestClient(main.app)
