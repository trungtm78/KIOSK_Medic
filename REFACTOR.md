# Kiosk Medic — Refactor Progress

Theo plan tại `~/.claude/plans/h-y-ph-n-t-ch-v-async-fairy.md`. Execution order: P0 → P1 → P3 → P2.

## P0 — Security (in progress)

### ✅ P0.1 — Secrets excluded from git

All `.env` files (5 files including MongoDB Atlas creds) are gitignored.
Initial commit `52f45b4` verified clean: no `.env` in tracked files.

### ✅ P0.2-P0.3 — CORS hardening (TDD)

Replaced `allow_origins=["*"]` with env-driven `CORS_ORIGINS` parser in both
chat-service and core-service.

- **Tests**: `chat-service/tests/test_cors.py` (3 tests), `core-service/tests/test_cors.py` (5 tests)
- **Behavior**: empty/unset env → dev defaults `[localhost:3000, 127.0.0.1:3000]`. Set `CORS_ORIGINS=https://prod.example.com` for production.
- **Run**: `cd <service>; .venv/Scripts/python -m pytest tests/test_cors.py -v`

### ✅ P0.4 — `.env.example` templates

Created for: root MedicAgent-main, chat-service, core-service, admin-service, FE-Kiosk-Medical.
Each template uses placeholder values like `change_me_password`. Real `.env` stays gitignored.

### ⚠️ P0.5 — MongoDB Atlas credentials rotation (USER ACTION REQUIRED)

The connection string `mongodb+srv://REDACTED-rotated-2026-05-14@cluster0.is2nllo.mongodb.net/...`
in `core-service/.env` (now gitignored) was previously sitting in a committable file. Even
though it's not in this repo's git history (verified clean), the credentials may have been
exposed earlier elsewhere.

**Action required by user (cannot automate):**

1. Log in to https://cloud.mongodb.com
2. Database Access → find user `REDACTED-USER`
3. Edit password → generate new strong password
4. Update `core-service/.env` line 10 with new connection string
5. (Optional) Delete the old database user `REDACTED-USER` and create a new one with least-privilege role
6. Restart core-service: kill running uvicorn + relaunch

**Rollback safety:** keep old credentials active for 24h while you verify new ones work.

## P1 — High ROI refactor (pending)

Items P1.1 through P1.6 per plan. Not started yet.

## P3 — Test foundation (pending, before P2)

Per Codex finding #12: use `testcontainers-python` MySQL 8 (not SQLite in-memory) to catch
MySQL-specific behaviors (Boolean defaults, NULL unique, decimal precision, queue concurrency).

## P2 — Architecture refactor (pending, last)

Per Codex findings #5-7: must mandate `app.state` for expensive model singletons.
Per Codex finding #16: must fix stale `conversationId` bug in `KioskProvider.startSession` BEFORE refactor.

## Test commands

```powershell
# Backend
cd MedicAgent-main\chat-service; .\.venv\Scripts\python -m pytest tests/ -v
cd MedicAgent-main\core-service; .\.venv\Scripts\python -m pytest tests/ -v
cd MedicAgent-main\admin-service; .\.venv\Scripts\python -m pytest tests/ -v

# Frontend (after P3.2)
cd FE-Kiosk-Medical; npm test
```

## Behavior-changing items (NOT pure structural refactor)

Per Codex #22, these items DO change behavior — flagged for explicit user review:

1. **CORS tightening** (P0.2-3): Production deployment with wildcard origin will now be rejected. User must set `CORS_ORIGINS` env var.
2. **Lazy DB init** (P1.2, planned): Services no longer fail at import if DB env missing — fail at first request instead.
3. **Logger replaces console.log** (P1.5, planned): Production builds will silence dev logging.
4. **Pinned dependencies** (P1.3, planned): Reproducible builds but may diverge from "latest" floating versions.
5. **Transaction boundaries** (P2.2, planned): Repository no longer commits — service layer or `get_db()` does.

All other refactors preserve observable behavior.
