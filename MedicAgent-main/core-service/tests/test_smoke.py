"""P3.1 - core-service smoke tests.

Pin app structure + route registration. Uses module-level app import.

Note: full integration tests (queue concurrency, ilike, decimal precision per
Codex #12-13) require testcontainers MySQL. They are TODO until P1.2 fixes
eager DB init - currently `app/directory/db.py` calls `create_all()` at import.

Until then, smoke tests rely on conftest.py setting MySQL env defaults.
"""

import pytest


@pytest.fixture
def app_client():
    """Lazy import to honor env from conftest."""
    import importlib
    import sys
    for mod in list(sys.modules):
        if mod == "app.main":
            del sys.modules[mod]

    from fastapi.testclient import TestClient
    main = importlib.import_module("app.main")
    return TestClient(main.app)


@pytest.mark.skip(reason="requires live MySQL - core eager imports DB at module load. "
                         "Will enable after P1.2 lazy-init refactor.")
def test_docs_endpoint_returns_200(app_client):
    response = app_client.get("/v1/core/docs")
    assert response.status_code == 200


@pytest.mark.skip(reason="requires live MySQL (eager import). After P1.2.")
def test_openapi_schema(app_client):
    response = app_client.get("/v1/core/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Core Service"


@pytest.mark.skip(reason="requires live MySQL + Qdrant. After P1.2.")
def test_directory_routes_registered(app_client):
    schema = app_client.get("/v1/core/openapi.json").json()
    paths = schema.get("paths", {})
    assert any(p.startswith("/v1/directory") for p in paths)
    assert any(p.startswith("/v1/queue") for p in paths)
    assert any(p.startswith("/v1/info") for p in paths)
    assert any(p.startswith("/v1/maps") for p in paths)
