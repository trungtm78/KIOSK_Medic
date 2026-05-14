# chatservice/app/routers/v1/chat.py

from fastapi import APIRouter, Depends, Header, Path, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
from pathlib import Path as pathlibPath

from ...services.nlu_service import NLUService, get_nlu_service, NLUResult
from ...services.orchestrator_service import OrchestratorService, get_orchestrator_service, HandleResult
from ...core.db import get_session_factory, session_scope, get_db
from sqlalchemy.orm import Session
from ...services.reply_service import ReplyService
from ...services.metrics_service import MetricsService
from ...services.session_service import SessionService
from ...services.queue_service import QueueService
from ...services.map_service import MapService
from ...services.kb_service import KBService
from ...services.handoff_service import HandoffService
from ...services.stream_service import get_stream_service
from ...schemas.chat import NLURequest, OrchestrateRequest, SendMessage, SendAck


router = APIRouter(prefix="/chat", tags=["chat"])


# @router.post("/nlu/infer")
# def nlu_infer(req: NLURequest, svc: NLUService = Depends(get_nlu_service)) -> dict:
#     res: NLUResult = svc.infer_intent(req.text, req.lang)
#     return {
#         "intent": res.intent.value,
#         "confidence": res.confidence,
#         "entities": res.entities,
#         "raw_text": res.raw_text,
#         "language": res.language,
#         "model_version": res.model_version,
#     }


# @router.post("/orchestrate/handle")
# def orchestrate(req: OrchestrateRequest, svc: OrchestratorService = Depends(get_orchestrator_service)) -> dict:
#     result: HandleResult = svc.handle(req.text, req.lang)
#     return {
#         "intent": result.intent.value,
#         "status": result.status,
#         "message": result.message,
#     }


# @router.get("/healthz")
# def healthz() -> dict:
#     return {"status": "ok"}


# API based on docs/api.yaml


@router.post("/{conversation_id}", response_model=SendAck, status_code=202)
def chat_send_message(
    conversation_id: str = Path(..., description="Client-provided conversation id"),
    payload: SendMessage = ...,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id"),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    orchestrator: OrchestratorService = Depends(get_orchestrator_service),
    db: Session = Depends(get_db),
):
    # Ensure conversation mapping (client -> server id)
    chart_path = str(pathlibPath(__file__).resolve().parents[2] / 'core' / 'state_machine' / 'statechart.sismic.yaml')
    stream = get_stream_service()
    ack = orchestrator.handle_user_message(
        # db_session=db,
        tenant_id=x_tenant_id,
        channel="api",
        client_conversation_id=conversation_id,
        role=payload.role,
        content=payload.content,
        idempotency_key=idempotency_key,
        chart_path=chart_path,
        stream_service=stream,
    )
    return SendAck(**ack)


@router.get("/{conversation_id}/stream")
async def chat_stream(conversation_id: str, cursor: Optional[str] = None):
    stream = get_stream_service()
    generator = stream.subscribe(conversation_id)
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(generator, media_type="text/event-stream", headers=headers)
