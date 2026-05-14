from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Message


class MessageRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, conversation_id: str, role: str, content: str, meta: Optional[Dict[str, Any]] = None) -> Message:
        msg = Message(conversation_id=conversation_id, role=role, content=content, meta=meta or {})
        self.session.add(msg)
        return msg

    def list_for_conversation(self, conversation_id: str, limit: int = 50, offset: int = 0) -> List[Message]:
        stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars())

