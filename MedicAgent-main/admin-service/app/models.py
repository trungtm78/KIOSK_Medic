from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Tenant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    name: str
    status: str = "active"  # active|suspended
    plan: str = "FREE"  # FREE|STANDARD|ENTERPRISE
    timezone: str = "Asia/Ho_Chi_Minh"
    locale: str = "vi-VN"
    logo_url: Optional[str] = None


class TenantFeature(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    feature_key: str
    enabled: bool = True


class TenantQuota(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    quota_key: str
    value_int: Optional[int] = None
    value_text: Optional[str] = None
    reset_policy: str = "monthly"  # none|daily|monthly


class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    name: str


class Permission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    description: str


class RolePermission(SQLModel, table=True):
    role_id: int = Field(foreign_key="role.id", primary_key=True)
    permission_id: int = Field(foreign_key="permission.id", primary_key=True)


class KioskToken(SQLModel, table=True):
    """CSO Finding #2 fix - per-kiosk authentication token.

    Tokens are stored as bcrypt hashes; raw token shown to admin once on creation.
    `token_prefix` (first 8 chars) enables fast lookup before bcrypt.checkpw.
    Lifecycle: created -> active -> revoked (soft delete via revoked_at).
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    kiosk_name: str = Field(max_length=100)  # 'reception-1', 'pharmacy-3'
    token_hash: str = Field(max_length=255)  # bcrypt hash, NEVER raw token
    token_prefix: str = Field(max_length=12, index=True)  # 'kt_a1b2c3de'
    scopes: str = Field(default="chat,maps,info")  # comma-separated
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # None = never expires
    last_used_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None  # soft delete


