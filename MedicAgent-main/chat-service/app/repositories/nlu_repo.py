from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import NLUResult


class NLURepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        message_id: str,
        intent: str,
        confidence: Optional[float],
        entities: Optional[Dict[str, Any]] = None,
        features: Optional[Dict[str, Any]] = None,
    ) -> NLUResult:
        row = NLUResult(
            message_id=message_id,
            intent=intent,
            confidence=confidence,
            entities=entities or {},
            features=features or {},
        )
        self.session.add(row)
        return row

    def list_for_message(self, message_id: str) -> List[NLUResult]:
        stmt = select(NLUResult).where(NLUResult.message_id == message_id).order_by(NLUResult.created_at.asc())
        return list(self.session.execute(stmt).scalars())

