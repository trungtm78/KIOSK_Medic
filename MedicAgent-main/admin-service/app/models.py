from typing import Optional
from sqlmodel import SQLModel, Field


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

