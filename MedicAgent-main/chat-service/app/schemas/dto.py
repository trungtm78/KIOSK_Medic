from enum import StrEnum
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class Intent(StrEnum):
    DIRECTION = "directions"  # align with statechart guards
    PROCEDURE = "procedure"
    ISSUE_TICKET = "issue_ticket"
    TRIAGE = "triage"
    SMALLTALK = "smalltalk"
    EMR = "emr"
    FAQ = "faq"
    UNKNOWN = "unknown"


class EntityPOI(BaseModel):
    poi_name: Optional[str] = None
    conf_poi: float = Field(default=0.0, ge=0.0, le=1.0)


class NLUEnvelope(BaseModel):
    intent: Intent
    conf_intent: float = Field(ge=0.0, le=1.0)
    entities: EntityPOI = Field(default_factory=EntityPOI)


ResolvedVia = Literal["nlu", "disambiguation", "none"]


class InterpretRequest(BaseModel):
    text: str
    lang: Optional[str] = "vi"
    user_id: Optional[str] = None


class CandidateOption(BaseModel):
    poi_id: str
    score: int = Field(ge=0, le=100)
    name_vi: Optional[str] = None
    name_en: Optional[str] = None
    category: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    zone: Optional[str] = None


class NextAction(BaseModel):
    action: Literal["route"] = "route"
    from_poi_id: str
    to_poi_id: str


class EntityResolved(BaseModel):
    poi_id: str
    score: int = Field(ge=0, le=100)
    label: Optional[str] = None
    name_vi: Optional[str] = None
    name_en: Optional[str] = None
    category: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    zone: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    open_hours: Optional[str] = None


class InterpretResponse(BaseModel):
    intent: Intent
    resolved_via: ResolvedVia = "none"
    confidence: float = Field(ge=0.0, le=1.0)
    entity: Optional[EntityResolved] = None
    next: Optional[NextAction] = None
    disambiguation: Optional[str] = None
    options: Optional[List[CandidateOption]] = None
