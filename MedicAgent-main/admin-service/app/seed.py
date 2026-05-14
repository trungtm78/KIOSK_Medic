from typing import Iterable
from sqlmodel import Session, select

from .models import Tenant, TenantFeature, TenantQuota, Role, Permission, RolePermission


DEFAULT_FEATURES = [
    "chat.enabled",
    "payment.enabled",
    "queue.enabled",
    "ekyc.enabled",
]

DEFAULT_QUOTAS = {
    "queue.max_tickets_per_day": 2000,
    "chat.max_tokens_per_day": 2_000_000,
}

PERMISSIONS = [
    ("TENANT.READ", "Read tenant metadata"),
    ("TENANT.WRITE", "Update tenant metadata"),
    ("FEATURE.READ", "Read feature flags"),
    ("FEATURE.WRITE", "Update feature flags"),
    ("QUOTA.READ", "Read quotas"),
    ("QUOTA.WRITE", "Update quotas"),
    ("USER.READ", "Read tenant users"),
    ("USER.WRITE", "Manage tenant users"),
]

ROLES = {
    "ADMIN": [p[0] for p in PERMISSIONS],
    "OPERATOR": ["TENANT.READ", "FEATURE.READ", "QUOTA.READ"],
    "VIEWER": ["TENANT.READ", "FEATURE.READ"],
}


def _ensure(session: Session, model, where: dict, defaults: dict | None = None):
    stmt = select(model)
    for k, v in where.items():
        stmt = stmt.where(getattr(model, k) == v)
    obj = session.exec(stmt).first()
    if obj:
        return obj
    params = {**where}
    if defaults:
        params.update(defaults)
    obj = model(**params)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


def seed_initial_data(session: Session) -> None:
    # Roles and permissions
    perm_objs: list[Permission] = []
    for code, desc in PERMISSIONS:
        perm_objs.append(_ensure(session, Permission, {"code": code}, {"description": desc}))

    role_objs: dict[str, Role] = {}
    for code, perms in ROLES.items():
        role = _ensure(session, Role, {"code": code}, {"name": code.title()})
        role_objs[code] = role

    # RolePermissions mapping
    for role_code, perm_codes in ROLES.items():
        role = role_objs[role_code]
        for pc in perm_codes:
            perm = session.exec(select(Permission).where(Permission.code == pc)).first()
            if not perm:
                continue
            exists = session.exec(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == perm.id,
                )
            ).first()
            if not exists:
                session.add(RolePermission(role_id=role.id, permission_id=perm.id))
    session.commit()

    # Tenants
    t1 = _ensure(
        session,
        Tenant,
        {"code": "HOSP_A"},
        {
            "name": "Hospital A",
            "plan": "STANDARD",
            "timezone": "Asia/Ho_Chi_Minh",
            "locale": "vi-VN",
        },
    )
    t2 = _ensure(
        session,
        Tenant,
        {"code": "HOSP_B"},
        {
            "name": "Hospital B",
            "plan": "ENTERPRISE",
            "timezone": "Asia/Ho_Chi_Minh",
            "locale": "vi-VN",
        },
    )

    for tenant in (t1, t2):
        for f in DEFAULT_FEATURES:
            _ensure(session, TenantFeature, {"tenant_id": tenant.id, "feature_key": f}, {"enabled": True})
        for qk, val in DEFAULT_QUOTAS.items():
            _ensure(
                session,
                TenantQuota,
                {"tenant_id": tenant.id, "quota_key": qk},
                {"value_int": val, "reset_policy": "monthly"},
            )

