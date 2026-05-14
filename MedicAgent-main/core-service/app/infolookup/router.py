from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.directory.db import get_db
from app.infolookup.schemas import (
    InfoLookupRequest,
    InfoLookupResponse,
    PriceLookupRequest,
    PriceLookupResponse,
)
from ..servicelogs.servicelogger import logger
from app.infolookup.service import (
    InfoLookupService,
    PriceLookupService,
    get_info_lookup_service,
    get_price_lookup_service,
)

router = APIRouter(tags=["Info Lookup"])


@router.post("/lookup", response_model=InfoLookupResponse)
def lookup_info(
    payload: InfoLookupRequest,
    svc: InfoLookupService = Depends(get_info_lookup_service),
) -> InfoLookupResponse:
    logger.debug(f"Received info lookup request: {payload}")
    if not payload.question.strip():
        raise HTTPException(status_code=422, detail="Question is required")
    response = svc.lookup(payload)
    logger.debug(f"Info lookup response: {response}")
    return response


@router.post("/prices/lookup", response_model=PriceLookupResponse)
def lookup_price(
    payload: PriceLookupRequest,
    db: Session = Depends(get_db),
    svc: PriceLookupService = Depends(get_price_lookup_service),
) -> PriceLookupResponse:
    logger.debug(f"Received price lookup request: {payload}")
    try:
        response = svc.lookup(payload, db)
        logger.debug(f"Price lookup response: {response}")
        return response
    except LookupError:
        raise HTTPException(status_code=404, detail="Hospital not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
