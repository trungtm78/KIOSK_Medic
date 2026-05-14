# Chat Service Database — Table Explanations

This document explains the tables modeled in `docs/db.md` (Mermaid ERD), their purpose, relationships, and practical guidance for queries and indexing.

Notes
- User and Tenant are external services. Only IDs are stored locally (e.g., `tenant_id`); validate existence via APIs or a local cache.
- Time fields use `timestamptz`. IDs are UUIDs unless stated otherwise.
- Suggested indexes and constraints are recommendations; adapt to your workload.

## Conversation
Purpose
- A conversation session for a given tenant and channel. Root entity for turns, messages, and FSM transitions.

Key Fields
- `id`: Primary key.
- `tenant_id`: External Admin/Tenant ID.
- `channel`: Channel identifier (e.g., kiosk, web, whatsapp...).
- `status`: Lifecycle state (e.g., active, paused, ended).
- `fsm_id`: Versioned FSM identifier (e.g., `chat_service@v1`).
- `state`: Current nested FSM state (dot-path, e.g., `FLOW_ISSUE_TICKET.GATHER`).
- `memory` (jsonb): Slot values / short context.
- `started_at`, `ended_at`.

Relationships
- 1 + N `Turn`, 1 + N `Message`, 1 + N `StateTransition`, 1 + N `HandoffSession`.

Indexes & Constraints
- Index `(tenant_id)`, `(tenant_id, status)`, `(started_at)` for reporting.
- Consider retention/partitioning by `tenant_id` and/or time windows.

## Turn
Purpose
- One alternation in a conversation (user+bot). Used to reconstruct timeline and associate operational tasks.

Key Fields
- `id`: Primary key.
- `conversation_id`: Parent conversation.
- `turn_no`: Sequence number within conversation.
- `user_msg_id`, `bot_msg_id`: Message linkage for this turn.
- `ctx_snapshot` (jsonb): Context snapshot before/after.
- `created_at`.

Relationships
- N + 1 `Conversation`; 1 + N `Task`.

Indexes & Constraints
- Unique `(conversation_id, turn_no)` to prevent duplicates.
- Index `(conversation_id, turn_no)` and `(conversation_id, created_at)`.

Typical Queries
- Fetch latest turn: filter by `conversation_id`, order by `turn_no` desc, limit 1.

## Message
Purpose
- Stores atomic chat messages associated with a conversation.

Key Fields
- `id`, `conversation_id`.
- `role`: `user | assistant | tool | system`.
- `content`: Text content.
- `meta` (jsonb): Token usage, model, tool name, etc.
- `created_at`.

Relationships
- 1 + N `NLUResult`, 1 + N `Citation`.

Indexes & Constraints
- Index `(conversation_id, created_at)`; optional `(role)` for filtering.

## Transcript
Purpose
- Optional append-only log for raw events (user_msg, bot_msg, tool_req/res, transition) for auditing or full-fidelity replay.

Key Fields
- `id` (bigserial), `conversation_id`.
- `kind`: Event type.
- `payload` (jsonb): Raw payload.
- `ts`: Event timestamp.

Indexes & Constraints
- Index `(conversation_id, ts)`.

## Task
Purpose
- Operational unit inside a turn, e.g., RAG retrieval, API call, slot validation, summarization.

Key Fields
- `id`, `turn_id`.
- `kind`: Task category.
- `status`: `pending | running | success | error | timeout | canceled`.
- `input` (jsonb), `output` (jsonb).
- `started_at`, `finished_at`.

Relationships
- N + 1 `Turn`.

Indexes & Constraints
- Index `(turn_id)`, `(status)`, `(started_at)`.

## StateTransition
Purpose
- Audit log for FSM transitions within a conversation.

Key Fields
- `id`, `conversation_id`.
- `fsm_id`: Versioned FSM id (e.g., `chat_service@v1`).
- `from_state`, `to_state`: Dot-path nested states (e.g., `FLOW_PROCEDURE.SHOW_CHECKLIST`).
- `event`: Event name (e.g., `USER_MESSAGE`, `SLOT_FILLED`, `CONFIRM_YES`, `CONFIRM_NO`, `CANCEL_FLOW`, `TIMEOUT`).
- `guard_eval` (jsonb): Condition evaluation details. Suggested: `{ cond: string, results: { guard_name: boolean, ... } }`.
- `created_at`.

Relationships
- N + 1 `Conversation`.

Indexes & Constraints
- Index `(conversation_id, created_at)`; optional `(conversation_id, event)` and `(fsm_id)`.

## HandoffSession
Purpose
- Track human handoff sessions associated with a conversation.

Key Fields
- `id`, `conversation_id`.
- `channel_id`: External operator channel/session id.
- `status`: `open | closed`.
- `created_at`, `closed_at`.

Relationships
- N + 1 `Conversation`.

Indexes & Constraints
- Index `(conversation_id, created_at)`; optional `(status)`.

## NLUResult
Purpose
- Stores NLU outputs for a message: intent, confidence, entities, features.

Key Fields
- `id`, `message_id`.
- `intent`, `confidence`.
- `entities` (jsonb): Extracted slots.
- `features` (jsonb): Embedding IDs, logits, etc.
- `created_at`.

Relationships
- N + 1 `Message`.

Indexes & Constraints
- Index `(message_id)`; optional `(intent)` for analytics.

## Citation
Purpose
- RAG explainability: which KB chunks supported generating a response.

Key Fields
- `id`, `message_id`, `kb_chunk_id`.
- `score`: Relevance/weight.

Relationships
- N + 1 `Message`; N + 1 `KB_Chunk`.

Indexes & Constraints
- Index `(message_id, score desc)`, and `(kb_chunk_id)`.
- Consider ON DELETE CASCADE from `Message` and `KB_Chunk`.

## KB_Doc
Purpose
- Top-level knowledge item for a tenant.

Key Fields
- `id`.
- `tenant_id`: External Admin/Tenant ID.
- `kind`: `procedure | navigation | faq | general | policy`.
- `title`, `source`.
- `meta` (jsonb): Tags, department, audience, locale, etc.
- `created_at`.

Relationships
- 1 + N `KB_Chunk`.

Indexes & Constraints
- Index `(tenant_id, kind)`, `(created_at)`.

## KB_Chunk
Purpose
- Splits a KB document into addressable content units.

Key Fields
- `id`, `kb_doc_id`.
- `ordinal`: Position within document.
- `content`: Text chunk.

Relationships
- N + 1 `KB_Doc`; 1 + 1 `KB_Embedding`.

Indexes & Constraints
- Index `(kb_doc_id, ordinal)`.

## KB_Embedding
Purpose
- Vector representation (pgvector) for a KB chunk to enable similarity search.

Key Fields
- `kb_chunk_id` (PK, 1:1 with `KB_Chunk`).
- `embedding` (vector), `created_at`.

Relationships
- 1 + 1 `KB_Chunk`.

Indexes & Constraints
- Add pgvector index (e.g., ivfflat/hnsw) on `embedding` for retrieval.

---

Operational Notes
- Deletion/Cascade: Consider cascading Conversation + Turn + Task/Message + NLUResult/Citation to avoid orphaned rows.
- Multi-Tenancy: Always filter by `tenant_id`; consider RLS or schema-level isolation if required.
- Performance: Use covering indexes for common filters; consider partitioning by time for large Transcript/Message tables.

Statechart Integration Notes
- Persist `Conversation.fsm_id` and `StateTransition.fsm_id` as `chat_service@v1`.
- Persist nested state paths (dot-path) to align with hierarchical states in the Sismic statechart.
- Log `guard_eval` with the textual condition and per-guard boolean outcomes for better analytics and debugging.

