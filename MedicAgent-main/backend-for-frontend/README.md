# Backend For Frontend (BFF)

A lightweight FastAPI-based BFF that fronts `chat-service` and exposes stable endpoints for the API Gateway / clients.

## Endpoints

- `POST /v1/chat/{conversation_id}`
  - Forwards to `chat-service /v1/chat/{conversation_id}`
  - Headers: `X-Tenant-Id`, `Idempotency-Key`
- `GET /v1/chat/{conversation_id}/stream`
  - Proxies SSE stream from `chat-service`

## Configuration

- `CHAT_SERVICE_BASE_URL` (default: `http://chat-service:8000`)
- `REQUEST_TIMEOUT_SECONDS` (default: `30`)

## Run locally

```bash
pip install -r backend-for-frontend/requirements.txt
uvicorn app.main:app --reload --port 8081 --app-dir backend-for-frontend
```

## Notes

- Authorization header is forwarded if present.
- BFF is stateless; suitable to sit behind Kong.
