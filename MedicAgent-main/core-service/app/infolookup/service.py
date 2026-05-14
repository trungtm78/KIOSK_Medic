from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from app.directory.repository import repo as directory_repo
from app.embeddings.service_index import service_index
from app.infolookup.repository import KnowledgeEntry, KnowledgeRepository
from app.infolookup.schemas import (
    InfoLookupRequest,
    InfoLookupResponse,
    KnowledgeSnippet,
    PriceLookupRequest,
    PriceLookupResponse,
    ServicePriceLookupResult,
    ServiceSuggestion,
    PriceQuote,
)
from app.servicelogs.servicelogger import logger


class InfoLookupService:
    def __init__(self, repository: Optional[KnowledgeRepository] = None) -> None:
        self.repo = repository or KnowledgeRepository()

    def lookup(self, request: InfoLookupRequest) -> InfoLookupResponse:
        logger.info(
            "InfoLookupService.lookup question=%s topic=%s hospital=%s workflow_type=%s",
            request.question,
            request.topic,
            request.hospital_id,
            request.workflow_type,
        )
        matches = self.repo.search(
            request.question,
            topic=request.topic,
            hospital_id=request.hospital_id,
            workflow_type=request.workflow_type,
            limit=request.max_results,
        )
        snippets = [self._to_snippet(entry, score) for entry, score in matches]
        return InfoLookupResponse(
            question=request.question,
            topic=request.topic,
            hospital_id=request.hospital_id,
            results=snippets,
        )

    def _to_snippet(self, entry: KnowledgeEntry, score: float) -> KnowledgeSnippet:
        return KnowledgeSnippet(
            doc_id=entry.doc_id,
            doc_title=entry.doc_title,
            topic=entry.topic,
            source=entry.source,
            chapter_label=entry.chapter_label,
            chapter_title=entry.chapter_title,
            article_label=entry.article_label,
            article_title=entry.article_title,
            text=entry.text,
            keywords=entry.keywords,
            score=round(score, 3),
            flowchart=entry.flowchart,
        )


_INF_LOOKUP_SINGLETON: Optional[InfoLookupService] = None


def get_info_lookup_service() -> InfoLookupService:
    global _INF_LOOKUP_SINGLETON
    if _INF_LOOKUP_SINGLETON is None:
        _INF_LOOKUP_SINGLETON = InfoLookupService()
    return _INF_LOOKUP_SINGLETON


class PriceLookupService:
    def __init__(self):
        self.repo = directory_repo
        self.index = service_index

    def lookup(self, payload: PriceLookupRequest, db: Session) -> PriceLookupResponse:
        hospital = self.repo.get_hospital_by_id(db, hospital_id=payload.hospital_id)
        if not hospital:
            raise LookupError("Hospital not found")

        service = None
        suggestions: List[ServiceSuggestion] = []

        if payload.service_code:
            service = self.repo.get_service_by_code(
                db,
                hospital_id=payload.hospital_id,
                code=payload.service_code,
            )
            if not service:
                return PriceLookupResponse(suggestions=[])

        if not service:
            if not payload.q:
                raise ValueError("Missing service_code or q")
            candidates: List[int] = []
            try:
                results = self.index.search(
                    query=payload.q,
                    hospital_id=payload.hospital_id,
                    top_k=payload.top_k or 5,
                )
                candidates = [item["service_id"] for item in results]
            except Exception as exc:
                logger.warning("FAISS search failed, fallback to LIKE: %s", exc)

            services = []
            if candidates:
                services = [
                    self.repo.get_service_by_id(db, service_id=sid)
                    for sid in candidates
                ]
                services = [s for s in services if s]

            if not services:
                services = self.repo.search_services_by_keyword(
                    db,
                    hospital_id=payload.hospital_id,
                    keyword=payload.q,
                    limit=payload.top_k or 5,
                )

            if not services:
                return PriceLookupResponse(suggestions=[])

            if len(services) > 1:
                price_results = self._collect_prices(
                    db,
                    services,
                    payload,
                )
                if price_results:
                    return PriceLookupResponse(
                        result=price_results[0],
                        results=price_results,
                    )
                return PriceLookupResponse(
                    suggestions=[self._to_suggestion(s) for s in services]
                )
            service = services[0]

        price_results = self._collect_prices(
            db,
            [service],
            payload,
        )
        if not price_results:
            return PriceLookupResponse(suggestions=[])
        return PriceLookupResponse(result=price_results[0], results=price_results)

    def _collect_prices(
        self,
        db: Session,
        services,
        payload: PriceLookupRequest,
    ) -> List[ServicePriceLookupResult]:
        effective_date = payload.effective_date or date.today()
        results: List[ServicePriceLookupResult] = []
        for service in services:
            prices = self.repo.get_prices_effective(
                db,
                service_id=service.service_id,
                payer_type=payload.payer_type,
                area_tag=payload.area_tag,
                effective_date=effective_date,
            )
            if not prices:
                continue
            results.append(
                ServicePriceLookupResult(
                    service_id=service.service_id,
                    service_code=service.code,
                    service_name=service.name,
                    categories=[c.name for c in service.categories] if service.categories else [],
                    prices=[
                        PriceQuote(
                            payer_type=p.payer_type,
                            price=p.price,
                            currency=p.currency,
                            area_tag=p.area_tag,
                            effective_from=p.effective_from,
                            effective_to=p.effective_to,
                            notes=p.notes,
                        )
                        for p in prices
                    ],
                )
            )
        return results

    def _to_suggestion(self, service) -> ServiceSuggestion:
        categories = [c.name for c in service.categories] if service.categories else []
        return ServiceSuggestion(
            service_id=service.service_id,
            service_code=service.code,
            service_name=service.name,
            categories=categories,
        )


_PRICE_LOOKUP_SINGLETON: Optional[PriceLookupService] = None


def get_price_lookup_service() -> PriceLookupService:
    global _PRICE_LOOKUP_SINGLETON
    if _PRICE_LOOKUP_SINGLETON is None:
        _PRICE_LOOKUP_SINGLETON = PriceLookupService()
    return _PRICE_LOOKUP_SINGLETON
