from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..schemas.tenant import TenantMeta, FeatureFlag, QuotaItem
from ..core.db import get_session
from ..services import tenant_service


router = APIRouter()


@router.get("/tenants/{tenant_ref}/meta", response_model=TenantMeta)
def get_meta(tenant_ref: str, session: Session = Depends(get_session)):
    return tenant_service.get_meta(session, tenant_ref)


@router.get("/tenants/{tenant_ref}/features", response_model=list[FeatureFlag])
def list_features(tenant_ref: str, session: Session = Depends(get_session)):
    return tenant_service.get_features(session, tenant_ref)


@router.get("/tenants/{tenant_ref}/quotas", response_model=list[QuotaItem])
def list_quotas(tenant_ref: str, session: Session = Depends(get_session)):
    return tenant_service.get_quotas(session, tenant_ref)
