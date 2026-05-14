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

## ✅ P1 — High ROI refactor (mostly complete)

### P1.1 — Centralized FE API client (TDD)
- `src/lib/api.ts`: typed fetch wrapper, ApiError class, configureApi()
- `src/types/index.ts`: consolidated Ticket/ChatMessage/MapData types
  (replaces 4 Ticket duplicates audit found)
- 7 tests in `src/__tests__/api.test.ts`

### P1.2 — Pydantic-settings + lazy DB init
- admin-service: `app/core/settings.py` + lazy `get_engine()` (Codex #4 fix)
- chat-service: existing lazy pattern in db.py kept as-is
- core-service: deferred (bigger eager-init refactor — separate commit)

### P1.3 — Pin dependencies
- admin-service: 6 deps pinned
- core-service: 18 deps pinned (transformers/sentence-transformers/huggingface-hub
  locked to working trio after v5 breakage discovered)

### P1.4 — `.dockerignore` for 6 services
- admin, chat, core, sttphowhisper, stt-zipformer, llm-agent
- Excludes .venv, .git, tests/docs, .env, __pycache__

### P1.5 — Centralized logger (partial)
- `src/lib/logger.ts`: debug/info silent in production
- 4 tests verify behavior
- Existing 27 console.log call sites migrate later (when components split)

### P1.6 — CI lint gate (gradual rollout, Codex #21)

Configuration files created. **User must install pre-commit:**

```powershell
# One-time setup:
py -m pip install --user pre-commit
cd c:\Kiosk\Medic
pre-commit install
pre-commit run --all-files  # initial cleanup of existing code
```

Files:
- `.pre-commit-config.yaml` (root): trailing-whitespace, end-of-file-fixer,
  yaml/json validity, large-file blocker, secrets detector, ruff (Python),
  prettier (TS/TSX/JSON/MD)
- `MedicAgent-main/pyproject.toml`: ruff rules E/F/I/UP (safe auto-fix only)

**Gradual rollout (per Codex #21):**
- Phase 1 (current): E, F, I, UP — safe auto-fix rules
- Phase 2 (after P2.3 component split): add B (bugbear) + SIM (simplify)
- Phase 3 (after callsites clean): enable `no-explicit-any`, `no-console` in ESLint

This prevents enabling 100+ unrelated lint errors before refactor is done.

## ⚠️ P2 — Architecture refactor (in progress)

### ✅ P2.1 — Kill global singletons (Codex #5-7)

6 singletons in chat-service replaced with `@lru_cache(maxsize=1)`:
- `nlu_service.py:get_nlu_service()` — directory hint cache preserved (Codex #7)
- `orchestrator_service.py:get_orchestrator_service()`
- `stream_service.py:get_stream_service()` — subscriber queues stay attached
- `triage_service.py:get_triage_service()`
- `intent_classifier.py:get_intent_classifier()` — negative caching preserved (Codex #6)
- `syndrome_classifier.py:get_syndrome_classifier()` — negative caching preserved

Tests can call `get_X.cache_clear()` to reset between test cases.
Same singleton semantics (one instance per process), now testable.

### ✅ P2.3 (partial) — Fix stale conversationId bug (Codex #16)

`KioskProvider.tsx:startSession` previously called `sendChatMessage("xin chào")`
in a setTimeout. `sendChatMessage` closed over `conversationId` from React state
which was `null` at the moment of closure. The 500ms delay was a hack hoping
React would re-render in time.

**Fix:** setTimeout now POSTs directly with `newConvId` instead of relying on
stale closure.

Larger P2.3 work (split cai_dat_bang_do/page.tsx 985 LOC + KioskProvider useReducer
+ side-effect extraction per Codex #18-19) deferred — separate dedicated session.

### ⏳ P2.2 — Move transaction control (Codex #8-11)

Deferred. Order per Codex:
1. First refactor `get_db()` to commit-on-exit + rollback-on-exception
2. Audit each router endpoint for service-vs-repo direct usage
3. Then remove `db.commit()` from repository methods (keep `flush()` + `refresh()` for serialization)
4. Special handling for `queue/repository.py:93-98, 111+` already mixing patterns

### ⏳ P2.4 — Split backend mega-files

Deferred. Items:
- `nlu_service.py` 1072 LOC → `nlu/` package
- `actions.py` 820 LOC → `actions/` package by intent
- `triage_symptoms_data.py` 750 LOC → JSON/YAML data file

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
