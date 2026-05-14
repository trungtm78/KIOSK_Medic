# Admin Service

The Admin Service powers the operational tooling for MedicAgent.

## Overview
The service exposes REST endpoints for managing clinics, providers, patient accounts, and platform configuration. It handles authentication using JWT tokens and enforces RBAC roles (viewer, operator, super-admin) across every endpoint. All write operations pass through validation layers to prevent invalid configuration reaching downstream services.

## Key Capabilities
- Provision and update clinics, departments, and provider rosters.
- Moderate patient accounts, including manual verification and emergency deactivation workflows.
- Manage reference data (care pathways, treatment templates) consumed by downstream AI agents.
- Schedule platform-wide maintenance windows with automatic notifications to dependent services.
- Aggregate audit events and push them to the analytics pipeline for compliance reporting.

## Architecture
- **API Layer:** FastAPI application exposing synchronous admin endpoints and asynchronous background tasks for larger batch jobs.
- **Data Layer:** MySQL (configured via `ADMIN_DB_URL`) stores tenant metadata, feature flags, and quotas. SQLModel manages schema creation at startup.
- **Messaging:** Publishes configuration changes to the platform event bus (Kafka) so other services stay in sync.
- **Authentication:** Integrates with the Auth service for JWT issuance and validates scopes locally; secrets are rotated via Vault.

## Operational Notes
- Deploys as a container via the shared Helm chart; horizontal pod autoscaling is enabled based on request latency.
- Health checks cover DB connectivity, event bus reachability, and background worker status.
- SLOs: p95 latency under 200ms for CRUD endpoints and successful audit fan-out within 30 seconds.

## Configuration
- `ADMIN_DB_URL` (required): SQLAlchemy connection string for the admin database. Example for docker-compose: `mysql+pymysql://medicagent:medicagent_password@medicagent-db:3306/medicagent-admin-db`.
- `ENV`: Deployment environment flag propagated from docker-compose.

## Database migrations
Alembic manages schema changes for this service. Common commands:

```bash
cd admin-service
ADMIN_DB_URL=mysql+pymysql://user:pass@host:3306/medicagent-admin-db alembic upgrade head
ADMIN_DB_URL=... alembic revision --autogenerate -m "describe change"
```

Ensure the target database is reachable before running migrations. The generated scripts live under `alembic/versions/`.
