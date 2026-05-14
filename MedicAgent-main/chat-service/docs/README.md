# Chat Service

FastAPI-based chat orchestrator for the medical assistant stack. It routes user messages through a Sismic state machine, runs NLU (rules + optional ML intent classifier), and calls downstream services (info lookup, directory, queue) to produce replies and server-sent events (SSE) for the frontend.

## Layout
- `app/main.py` – FastAPI app factory; routers under `/v1/chat` and `/v1/debug`.
- `app/routers/v1/chat.py` – POST chat entrypoint and SSE stream endpoint.
- `app/core/state_machine/statechart.sismic.yaml` – conversation FSM; helpers in `actions.py`, `guards.py`, `context.py`.
- `app/services/` – NLU (`nlu_service.py`, `nlu_constants.py`), triage, map/KB/queue/info lookup clients, stream service, intent classifier wrapper.
- `app/repositories/` – MySQL engine/session helpers, directory service client.
- `data/intent_training_examples.jsonl` – sample training data for the intent classifier.
- `models/intent_classifier/` – persisted classifier artifacts (`joblib`, `onnx`, `label_encoder.json`, `config.json`).
- `scripts/train_intent_classifier.py` – training + ONNX export script.
- `docs/` – OpenAPI (`api.yaml`), state diagram (`state_diagram.md`), frontend integration notes.
- `dockerfile` – container build for the service.

## Prerequisites
- Python 3.11
- Pip
- MySQL reachable via `CHAT_DB_URL` if you enable DB-backed persistence (SQLAlchemy will auto-create tables on startup).
- Internet access on first run to download the SentenceTransformer model.

## Configuration
Set environment variables before running (or via an `.env` loaded by your process manager):
- `CHAT_DB_URL` (required for DB usage): e.g. `mysql+pymysql://user:pass@host:3306/chat_service`
- `INFO_LOOKUP_SERVICE_URL` (optional): base URL for core-service info lookup; default `http://medicagent-core-service:8080`
- `QUEUE_SERVICE_URL` (optional): queue service base; default `http://medicagent-core-service:8080/v1`
- `DIRECTORY_SERVICE_URL` (optional): directory service base; defaults to core-service/gateway/localhost fallbacks
- `TF_ENABLE_ONEDNN_OPTS=0` (optional): silence oneDNN warnings from TensorFlow if present

## Run locally
```powershell
cd chat-service
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
$env:CHAT_DB_URL="mysql+pymysql://user:pass@host:3306/chat_service"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open Swagger UI at `http://localhost:8000/v1/chat/docs`.

## API quick start
- Send a message:
  ```powershell
  curl -X POST "http://localhost:8000/v1/chat/demo-conv" `
    -H "Content-Type: application/json" `
    -H "X-Tenant-Id: hospital_1" `
    -H "Idempotency-Key: 00000000-0000-0000-0000-000000000001" `
    -d "{\"role\":\"user\",\"content\":\"Xin chao\"}"
  ```
- Stream replies:
  ```powershell
  curl -N "http://localhost:8000/v1/chat/demo-conv/stream"
  ```
- Debug cache: `GET /v1/debug/conversations`, `DELETE /v1/debug/conversations/{conversation_id}`.

## Train the intent classifier
Uses SentenceTransformer embeddings + logistic regression and exports ONNX.
```powershell
python scripts/train_intent_classifier.py `
  --data chat-service/data/intent_training_examples.jsonl `
  --output-dir chat-service/models/intent_classifier `
  --model-name AITeamVN/Vietnamese_Embedding
```
The orchestrator loads artifacts from `models/intent_classifier` by default.

## State machine
Conversation flow is defined in `app/core/state_machine/statechart.sismic.yaml` (visualized in `docs/state_diagram.md`). Key flows: issue ticket, directions, procedure checklist, triage, smalltalk; supports intent switching and cancel/timeout handling.

## Docker
```bash
cd chat-service
docker build -t chat-service .
docker run -p 8000:8000 --env-file ../.env chat-service
```
Mount or bake updated `models/` if you retrain the classifier.
