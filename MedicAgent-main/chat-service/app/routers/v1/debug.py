from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ...services.orchestrator_service import OrchestratorService, get_orchestrator_service


router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/conversations")
def list_cached_conversations(
    orchestrator: OrchestratorService = Depends(get_orchestrator_service),
) -> dict:
    return orchestrator.list_cached_conversations()


@router.delete("/conversations/{conversation_id}")
def delete_cached_conversation(
    conversation_id: str,
    tenant_id: Optional[str] = Query(None, description="Filter by tenant id if provided"),
    channel: Optional[str] = Query(None, description="Filter by channel if provided"),
    orchestrator: OrchestratorService = Depends(get_orchestrator_service),
) -> dict:
    removed = orchestrator.force_clear_conversation(
        conversation_id,
        tenant_id=tenant_id,
        channel=channel,
    )
    if not removed:
        raise HTTPException(status_code=404, detail="Conversation not found in cache")
    return {"status": "cleared", "conversation_id": conversation_id}


@router.delete("/conversations")
def delete_all_cached_conversations(
    orchestrator: OrchestratorService = Depends(get_orchestrator_service),
) -> dict:
    removed = orchestrator.force_clear_all_conversations()
    return {"status": "cleared_all", "removed": removed}
