
 **DRAFT**  
 _This document is a work in progress and subject to change._
---
---

# Kiến trúc trong 1 service

- Routers (public export): `/v1/interpret`, `/v1/confirm`, `/v1/device/state`, sessions, health.  
- Modules nội bộ (function layer): `routing_service`, `rag_service`, `nlu_service`, `kb_repo`.  
- Ports/Adapters đã cài sẵn nhưng **config = local** (sau này tách service chỉ cần đổi config).

---

# Endpoint public (Android chỉ gọi lớp này)

- `POST /v1/interpret` → hiểu lệnh, tự quyết định `route | procedure | clarify`  
- `POST /v1/confirm` → xác nhận lựa chọn khi mơ hồ  
- `POST /v1/device/state` → cập nhật vị trí hiện tại của robot  
- `POST /v1/sessions/start | /v1/sessions/reset`  
- `GET /v1/health` | `GET /v1/version`

> Giữ thêm các endpoint **debug** (tắt trên prod bằng flag):  
> `/v1/routing/plan`, `/v1/routing/match-poi`, `/v1/kb/*`, `/v1/rag/search`.

---

# Schema phản hồi thống nhất

```json
{
  "intent": "route|procedure|clarify|smalltalk|unknown",
  "confidence": 0.0,
  "entities": { "to_poi": "LAB01", "procedure_code": null },
  "reply": "…",
  "actions": [
    {
      "type":"show_route",
      "payload":{"from":"LOBBY_A","to":"LAB01","path":[...],"edges":[...]}
    },
    {
      "type":"speak",
      "payload":{"text":"…"}
    }
  ],
  "need_confirmation": false,
  "session_id": "uuid",
  "trace_id": "…"
}
```

---

# Folder layout (đề xuất)

```
app/
  main.py
  core/
    config.py         # flags, env
    sessions.py       # Redis/in-memory
    nlu.py            # intent & entity resolver (rule + small model)
  routers/
    public.py         # /v1/interpret, /v1/confirm, sessions, device
    debug.py          # /v1/routing/*, /v1/rag/*, /v1/kb/*
  services/
    routing_service.py   # A* + constraints
    rag_service.py       # passages, FAISS/Annoy (optional mock)
    kb_repository.py     # load poi.csv, map_edges.csv, procedures.json
    llm_client.py        # OpenAI-compatible (vLLM/Ollama) caller
  data/
    poi.csv
    map_edges.csv
    procedures.json
    index/
  utils/
    text.py
    graph.py
```

---

# Config (phase này = local)

```ini
API_KEY=changeme
SESSION_BACKEND=memory      # later: redis
ROUTING_BACKEND=local       # later: http/grpc
RAG_BACKEND=local           # later: http
LLM_API_BASE=http://localhost:8001/v1
LLM_API_KEY=changeme
ENABLE_DEBUG_ENDPOINTS=true
```

---

# Luồng xử lý trong `/v1/interpret`

1. Nhận `{text, context{session_id, locale, user}, device{robot_id, current_poi}}`.  
2. NLU:  
   - classify intent (`route/procedure/clarify/unknown`)  
   - resolve entities (POI, procedure) bằng alias + fuzzy + bias theo `current_poi`.  
3. Nếu `route`: `routing_service.plan(from=current_poi, to=to_poi, accessible=user.wheelchair)`.  
4. Nếu `procedure`: `rag_service.search(query)` → chọn doc → tóm tắt bằng `llm_client`.  
5. Nếu mơ hồ: trả `clarify` + `suggestions[]`, `need_confirmation=true`.  
6. Gói `reply + actions[]` theo schema thống nhất, ghi `session_id`.

---

# Checklist “Code xong chạy ngay”

- Loader: validate `poi.csv`, `map_edges.csv` (POI tồn tại, edge hợp lệ).  
- A*: heuristic theo lat/lon + phạt đổi tầng/tòa; filter stairs nếu `wheelchair=true`.  
- RAG: tạm thời có thể **mock** bằng keyword search + snippets (FAISS thêm sau).  
- LLM client: OpenAI-compat (vLLM/Ollama) – timeout, retry=1.  
- Session: `X-Session-Id` + `X-User-Changed:true` (reset context).  
- Logging + `trace_id` per request.  
- Flag `ENABLE_DEBUG_ENDPOINTS` để bật/tắt router debug.

---

# Test nhanh (happy paths)

- **Route**: “Dẫn mình tới xét nghiệm máu” → intent=route, path trả về có elevator nếu wheelchair.  
- **Procedure**: “Thủ tục khám BHYT” → intent=procedure, trả steps + `open_procedure`.  
- **Clarify**: “Tới phòng xét nghiệm” (nhiều phòng) → `clarify` + 2–3 gợi ý.
