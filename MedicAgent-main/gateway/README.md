Kong OSS Gateway — DB-less (Declarative)

This gateway config provides:
- Entrypoint at `/openapi/**`
- CORS enabled globally
- Request logging to file
- Global, per-tenant rate limiting
- Multi-tenant via per-tenant routes + ACLs
- API key auth for tenants

Structure
- `docker-compose.yml` — Runs Kong in DB-less mode
- `kong/kong.yaml` — Declarative config (services, routes, plugins, consumers)
- `logs/` — Kong writes request logs here (mounted into container)

Run
1) Start gateway
   - `docker compose -f projectplanning/gateway/docker-compose.yml up -d`
2) Verify Admin API (optional)
   - `curl http://localhost:8001/`  → should return Kong info
3) Call a tenant route (requires API key)
   - Tenant A example:
     - `curl -H "apikey: key-tenant-a-demo" http://localhost:8000/openapi/tenant-a/anything` 
   - Tenant B example:
     - `curl -H "apikey: key-tenant-b-demo" http://localhost:8000/openapi/tenant-b/anything`

Notes
- Upstreams in `kong.yaml` (`tenant-a-upstream`, `tenant-b-upstream`) are placeholders.
  Point them to your actual services that implement the OpenAPI endpoints.
- Multi-tenant is enforced by:
  - Path prefixes `/openapi/tenant-a/**`, `/openapi/tenant-b/**`
  - API key auth (header `apikey`)
  - ACL plugin requiring matching tenant group
  - Rate limiting with `limit_by: consumer` so each tenant gets its own quota
- CORS is applied globally. Adjust origins and headers for production.
- Logs are written to `projectplanning/gateway/logs/requests.log`.

Advanced
- If you want to generate Kong config directly from your OpenAPI specs (in `projectplanning/openapi/`),
  consider using `deck` or `kong-portal-cli` workflows. This repo includes a declarative example instead
  to avoid external tooling and network dependencies.

