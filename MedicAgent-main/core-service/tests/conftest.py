"""Test fixtures and env setup.

Note: core-service has eager imports (config.py:86 + directory/db.py:8-15)
that fail without DB env vars. We set safe defaults here so tests can import
the app. P1.2 will refactor this to lazy init.
"""

import os
import pytest


@pytest.fixture(autouse=True)
def _set_test_env_defaults(monkeypatch):
    """Set safe env defaults for tests that import app.main."""
    defaults = {
        "DB_USER": "test",
        "DB_PASSWORD": "test",
        "DB_HOST": "127.0.0.1",
        "DB_PORT": "3307",
        "DB_NAME": "test_db",
        "DIRECTORY_DB_NAME": "test_directory",
        "QUEUE_DB_NAME": "test_queue",
        "MONGODB_URI": "mongodb://test:test@localhost:27017/",
        "MONGODB_DB": "test_map",
        "QDRANT_HOST": "127.0.0.1",
        "QDRANT_PORT": "6337",
        "QDRANT_ENABLED": "false",
    }
    for k, v in defaults.items():
        if k not in os.environ:
            monkeypatch.setenv(k, v)
