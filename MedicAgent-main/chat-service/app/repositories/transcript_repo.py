from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.orm import Session

from ..models import Transcript


class TranscriptRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def append(self, conversation_id: str, kind: str, payload: Dict[str, Any]) -> Transcript:
        row = Transcript(conversation_id=conversation_id, kind=kind, payload=payload)
        self.session.add(row)
        return row

