from fastapi import HTTPException
from sqlmodel import Session

from ..schemas.tenant import TenantMeta, FeatureFlag, QuotaItem
from ..repositories import tenants as repo


def get_meta(session: Session, tenant_ref: str) -> TenantMeta:
    t = repo.get_tenant_by_ref(session, tenant_ref)
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return TenantMeta(
        id=t.id,
        code=t.code,
        name=t.name,
        plan=t.plan,
        timezone=t.timezone,
        locale=t.locale,
        logo_url=t.logo_url,
    )


def get_features(session: Session, tenant_ref: str) -> list[FeatureFlag]:
    t = repo.get_tenant_by_ref(session, tenant_ref)
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")
    rows = repo.list_features(session, t.id)
    return [FeatureFlag(key=r.feature_key, enabled=r.enabled) for r in rows]


def get_quotas(session: Session, tenant_ref: str) -> list[QuotaItem]:
    t = repo.get_tenant_by_ref(session, tenant_ref)
    if not t:
        raise HTTPException(status_code=404, detail="Tenant not found")
    rows = repo.list_quotas(session, t.id)
    return [QuotaItem(key=r.quota_key, value=r.value_int, reset_policy=r.reset_policy) for r in rows]

