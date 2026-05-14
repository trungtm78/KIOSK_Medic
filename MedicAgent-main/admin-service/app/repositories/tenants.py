from typing import Optional
from sqlmodel import Session, select

from ..models import Tenant, TenantFeature, TenantQuota


def get_tenant_by_id(session: Session, tenant_id: int) -> Optional[Tenant]:
    return session.get(Tenant, tenant_id)


def get_tenant_by_code(session: Session, code: str) -> Optional[Tenant]:
    return session.exec(select(Tenant).where(Tenant.code == code)).first()


def get_tenant_by_ref(session: Session, ref: str) -> Optional[Tenant]:
    if ref.isdigit():
        return get_tenant_by_id(session, int(ref))
    return get_tenant_by_code(session, ref)


def list_features(session: Session, tenant_id: int) -> list[TenantFeature]:
    return session.exec(select(TenantFeature).where(TenantFeature.tenant_id == tenant_id)).all()


def list_quotas(session: Session, tenant_id: int) -> list[TenantQuota]:
    return session.exec(select(TenantQuota).where(TenantQuota.tenant_id == tenant_id)).all()

