"""P3.1 - admin-service smoke tests.

Pin existing behavior: docs, openapi, route registration.
"""


def test_docs_endpoint_returns_200(app_client):
    response = app_client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema_endpoint_returns_200(app_client):
    response = app_client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Admin Service"


def test_app_registers_v1_tenant_routes(app_client):
    schema = app_client.get("/openapi.json").json()
    paths = schema.get("paths", {})
    v1_tenant_paths = [p for p in paths if p.startswith("/v1/tenants")]
    assert len(v1_tenant_paths) >= 3, (
        f"expected at least 3 /v1/tenants routes, got {v1_tenant_paths}"
    )


def test_unknown_route_returns_404(app_client):
    response = app_client.get("/this-route-does-not-exist")
    assert response.status_code == 404
