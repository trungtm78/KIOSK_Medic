from typing import Optional
from sqlmodel import SQLModel


class TenantMeta(SQLModel):
    id: int
    code: str
    name: str
    plan: str
    timezone: str
    locale: str
    logo_url: Optional[str] = None


class FeatureFlag(SQLModel):
    key: str
    enabled: bool


class QuotaItem(SQLModel):
    key: str
    value: Optional[int] = None
    reset_policy: str = "monthly"

