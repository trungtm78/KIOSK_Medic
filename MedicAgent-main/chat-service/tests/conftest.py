"""Test fixtures for chat-service.

Sets minimal env so app imports cleanly without external DB/LLM.
"""

import os

import pytest


@pytest.fixture(autouse=True)
def _set_test_env_defaults(monkeypatch):
    defaults = {
        "CHAT_DB_URL": "sqlite:///:memory:",
        "INTENT_MODEL_DIR": "./models/intent_classifier",
        "LLM_API_BASE": "http://127.0.0.1:8084/v1",
        "LLM_MODEL": "test-model",
    }
    for k, v in defaults.items():
        if k not in os.environ:
            monkeypatch.setenv(k, v)


@pytest.fixture
def app_client():
    """FastAPI TestClient for happy-path smoke tests.

    Imports app lazily so each test can reload with custom env.
    """
    from fastapi.testclient import TestClient
    from app.main import create_app

    return TestClient(create_app())
