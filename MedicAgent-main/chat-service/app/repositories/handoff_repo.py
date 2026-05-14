from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from ..models import HandoffSession


class HandoffRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def open(self, conversation_id: str, channel_id: Optional[str] = None) -> HandoffSession:
        row = HandoffSession(conversation_id=conversation_id, channel_id=channel_id, status="open")
        self.session.add(row)
        return row

    def close(self, handoff_id: str) -> Optional[HandoffSession]:
        row = self.session.get(HandoffSession, handoff_id)
        if not row:
            return None
        row.status = "closed"
        self.session.add(row)
        return row

