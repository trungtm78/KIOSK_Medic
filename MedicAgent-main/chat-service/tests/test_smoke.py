"""P3.1 - chat-service smoke tests.

Pin existing behavior: docs/openapi endpoints + route registration.
Goal: catch regression after P2 refactor.
"""


def test_docs_endpoint_returns_200(app_client):
    response = app_client.get("/v1/chat/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "openapi" in response.text.lower()


def test_openapi_schema_endpoint_returns_200(app_client):
    response = app_client.get("/v1/chat/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Chat Service"
    assert "paths" in schema


def test_app_registers_chat_routes(app_client):
    schema = app_client.get("/v1/chat/openapi.json").json()
    paths = schema.get("paths", {})
    chat_paths = [p for p in paths if p.startswith("/v1/chat/")]
    assert len(chat_paths) > 0, "no /v1/chat/ routes registered"


def test_app_registers_debug_routes(app_client):
    schema = app_client.get("/v1/chat/openapi.json").json()
    paths = schema.get("paths", {})
    debug_paths = [p for p in paths if p.startswith("/v1/debug/")]
    assert len(debug_paths) > 0, "no /v1/debug/ routes registered"


def test_unknown_route_returns_404(app_client):
    response = app_client.get("/this-route-does-not-exist")
    assert response.status_code == 404
