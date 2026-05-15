"""W4.7 - Admin endpoints to manage kiosk tokens (CSO Finding #2).

Endpoints:
  POST   /v1/tenants/{tenant_id}/kiosks   - create token, return raw ONCE
  GET    /v1/tenants/{tenant_id}/kiosks   - list tokens (metadata only)
  DELETE /v1/tenants/{tenant_id}/kiosks/{kiosk_id} - revoke (soft delete)

Admin-only auth: require X-Admin-API-Key header matching ADMIN_API_KEY env.
"""

import os
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from ..core.db import get_session
from ..core.kiosk_auth import (
    extract_prefix,
    generate_token,
    hash_token,
)
from ..models import KioskToken, Tenant


router = APIRouter()


def _verify_admin_api_key(
    x_admin_api_key: Annotated[Optional[str], Header()] = None,
) -> None:
    """Gate admin endpoints with shared API key from env."""
    expected = os.getenv("ADMIN_API_KEY", "").strip()
    if not expected:
        # Misconfiguration - in production, this MUST be set.
        # In dev, allow access but log warning.
        if os.getenv("APP_ENV", "development").lower() == "production":
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ADMIN_API_KEY not configured on server",
            )
        return
    if not x_admin_api_key or x_admin_api_key != expected:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid X-Admin-API-Key",
        )


class CreateKioskRequest(BaseModel):
    kiosk_name: str
    scopes: str = "chat,maps,info"
    expires_days: Optional[int] = None


class CreateKioskResponse(BaseModel):
    id: int
    kiosk_name: str
    token: str  # RAW token shown ONCE
    token_prefix: str
    created_at: datetime
    expires_at: Optional[datetime]
    note: str = "Save this token now - it cannot be retrieved later."


class KioskListItem(BaseModel):
    id: int
    kiosk_name: str
    token_prefix: str
    scopes: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    revoked_at: Optional[datetime]


@router.post(
    "/tenants/{tenant_id}/kiosks",
    response_model=CreateKioskResponse,
    dependencies=[Depends(_verify_admin_api_key)],
    status_code=status.HTTP_201_CREATED,
)
def create_kiosk_token(
    tenant_id: int,
    body: CreateKioskRequest,
    session: Session = Depends(get_session),
):
    tenant = session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    raw = generate_token()
    expires_at = None
    if body.expires_days is not None:
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(days=body.expires_days)

    token = KioskToken(
        tenant_id=tenant_id,
        kiosk_name=body.kiosk_name,
        token_hash=hash_token(raw),
        token_prefix=extract_prefix(raw),
        scopes=body.scopes,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
    )
    session.add(token)
    session.commit()
    session.refresh(token)

    return CreateKioskResponse(
        id=token.id,
        kiosk_name=token.kiosk_name,
        token=raw,  # RAW - shown once
        token_prefix=token.token_prefix,
        created_at=token.created_at,
        expires_at=token.expires_at,
    )


@router.get(
    "/tenants/{tenant_id}/kiosks",
    response_model=list[KioskListItem],
    dependencies=[Depends(_verify_admin_api_key)],
)
def list_kiosk_tokens(tenant_id: int, session: Session = Depends(get_session)):
    rows = session.exec(
        select(KioskToken).where(KioskToken.tenant_id == tenant_id)
    ).all()
    return [
        KioskListItem(
            id=r.id,
            kiosk_name=r.kiosk_name,
            token_prefix=r.token_prefix,
            scopes=r.scopes,
            created_at=r.created_at,
            expires_at=r.expires_at,
            last_used_at=r.last_used_at,
            revoked_at=r.revoked_at,
        )
        for r in rows
    ]


@router.delete(
    "/tenants/{tenant_id}/kiosks/{kiosk_id}",
    dependencies=[Depends(_verify_admin_api_key)],
    status_code=status.HTTP_200_OK,
)
def revoke_kiosk_token(
    tenant_id: int,
    kiosk_id: int,
    session: Session = Depends(get_session),
):
    row = session.exec(
        select(KioskToken).where(
            KioskToken.id == kiosk_id, KioskToken.tenant_id == tenant_id
        )
    ).first()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Token not found")
    if row.revoked_at is not None:
        return {"status": "already_revoked", "revoked_at": row.revoked_at.isoformat()}

    row.revoked_at = datetime.utcnow()
    session.add(row)
    session.commit()
    return {"status": "revoked", "kiosk_id": kiosk_id}
