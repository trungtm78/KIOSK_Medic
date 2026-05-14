```
[User]
   │ (voice)
┌──▼──────────────────────────┐
│  Robot Android App          │
│  - Voice UX, UI             │
│  - State Machine            │
│  - Local ASR (edge)         │
│  - Robot SDK Adapter        │
└──┬───────────────┬──────────┘
   │HTTP/gRPC      │Realtime (WebSocket/QUIC)
┌──▼──────────────┐│
│ API Gateway     ││
└──┬──────────────┘│
   │                │
┌──▼──────────────┐ │   ┌──────────────────┐
│ NLU Service     │ │   │ Policy Guard     │  (PHI/PII filter, consent, motion policy)
│ (intent/slots)  │ │   └──────────────────┘
└──┬──────────────┘ │             │
   │                 │             │
┌──▼──────────────┐  │   ┌────────▼────────┐
│ Skill Router    │──┼──▶│ Tool/Skill layer│ (Nav, Results, Procedure, FAQ)
└──┬──────────────┘  │   └────────┬────────┘
   │                  │            │
   │          ┌───────▼───────┐   │
   │          │ Message Bus   │◀──┘  (jobs: HIS query, summary)
   │          └───────┬───────┘
   │                  │
┌──▼──────────────┐   │   ┌───────────────┐
│ HIS/LIS Adapter │◀──┘   │ Map/POI Svc   │ (graph, ETA, geofence)
└──┬──────────────┘       └─────┬─────────┘
   │                              │
┌──▼──────────────┐         ┌─────▼─────────┐
│ Consent Svc     │         │ Safety Guard  │ (final veto for motion)
└──┬──────────────┘         └─────┬─────────┘
   │                              │
┌──▼──────────────┐         ┌─────▼─────────┐
│ Secrets/KMS     │         │ Observability │ (metrics, tracing, audit)
└─────────────────┘         └───────────────┘
```