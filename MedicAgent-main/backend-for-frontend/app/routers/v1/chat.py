from typing import AsyncIterator, Optional

import httpx
from fastapi import APIRouter, Header, Path, Request
from fastapi.responses import JSONResponse, StreamingResponse

from ...core.config import get_settings


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{conversation_id}")
async def bff_send_message(
    request: Request,
    conversation_id: str = Path(..., description="Client-provided conversation id"),
    x_tenant_id: str = Header(..., alias="X-Tenant-Id"),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    settings = get_settings()
    url = f"{settings.chat_service_base_url}/v1/chat/{conversation_id}"

    payload = await request.json()

    headers = {
        "X-Tenant-Id": x_tenant_id,
        "Idempotency-Key": idempotency_key,
    }
    # Forward Authorization if present (optional)
    auth_header = request.headers.get("authorization")
    if auth_header:
        headers["Authorization"] = auth_header

    timeout = httpx.Timeout(settings.request_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload, headers=headers)
        content_type = resp.headers.get("content-type", "application/json")
        # Return raw JSON payload with status code from chat-service
        try:
            data = resp.json()
        except ValueError:
            data = {"error": "invalid_response", "details": resp.text}
        return JSONResponse(content=data, status_code=resp.status_code, media_type=content_type)


@router.get("/{conversation_id}/stream")
async def bff_stream(
    request: Request,
    conversation_id: str,
    cursor: Optional[str] = None,
):
    settings = get_settings()
    params = {}
    if cursor:
        params["cursor"] = cursor
    url = f"{settings.chat_service_base_url}/v1/chat/{conversation_id}/stream"

    # Forward Authorization if present (optional)
    headers = {}
    auth_header = request.headers.get("authorization")
    if auth_header:
        headers["Authorization"] = auth_header

    timeout = httpx.Timeout(connect=settings.request_timeout_seconds)

    async def iter_sse() -> AsyncIterator[bytes]:
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("GET", url, params=params, headers=headers) as resp:
                async for chunk in resp.aiter_bytes():
                    # Pass-through raw SSE bytes
                    yield chunk

    passthrough_headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(iter_sse(), media_type="text/event-stream", headers=passthrough_headers)

