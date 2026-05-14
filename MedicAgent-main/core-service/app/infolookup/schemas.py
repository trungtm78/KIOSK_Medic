from __future__ import annotations

from decimal import Decimal
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class KnowledgeSnippet(BaseModel):
    doc_id: str
    doc_title: Optional[str] = None
    topic: str
    source: str
    chapter_label: Optional[str] = None
    chapter_title: Optional[str] = None
    article_label: Optional[str] = None
    article_title: Optional[str] = None
    text: str
    keywords: List[str] = Field(default_factory=list)
    score: float
    flowchart: Optional[dict] = None


class InfoLookupRequest(BaseModel):
    question: str = Field(..., min_length=2, description="User question in natural language")
    topic: Optional[str] = Field(None, description="Optional topic filter, e.g. 'insurance_policy'")
    hospital_id: Optional[str] = Field(
        None,
        description="Optional hospital identifier for hospital-specific knowledge base entries",
    )
    max_results: int = Field(3, ge=1, le=10, description="Number of matches to return")
    workflow_type: Optional[str] = Field(
        None,
        description="Optional workflow type filter such as 'bhyt' or 'service'",
    )


class InfoLookupResponse(BaseModel):
    question: str
    topic: Optional[str] = None
    hospital_id: Optional[str] = None
    results: List[KnowledgeSnippet] = Field(default_factory=list)


# === Price lookup ===
class ServiceSuggestion(BaseModel):
    service_id: int
    service_code: str
    service_name: str
    categories: List[str] = Field(default_factory=list)


class PriceQuote(BaseModel):
    payer_type: Optional[str] = None
    price: Decimal
    currency: str
    area_tag: Optional[str] = None
    effective_from: date
    effective_to: Optional[date] = None
    notes: Optional[str] = None


class ServicePriceLookupResult(BaseModel):
    service_id: int
    service_code: str
    service_name: str
    categories: List[str] = Field(default_factory=list)
    prices: List[PriceQuote] = Field(default_factory=list)


class PriceLookupResponse(BaseModel):
    result: Optional[ServicePriceLookupResult] = None
    results: List[ServicePriceLookupResult] = Field(default_factory=list)
    suggestions: List[ServiceSuggestion] = Field(default_factory=list)


class PriceLookupRequest(BaseModel):
    hospital_id: int
    service_code: Optional[str] = None
    q: Optional[str] = None
    payer_type: Optional[str] = None
    area_tag: Optional[str] = None
    effective_date: Optional[date] = None
    top_k: Optional[int] = 5
