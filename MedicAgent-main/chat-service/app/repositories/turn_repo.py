from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Turn


class TurnRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def next_turn_no(self, conversation_id: str) -> int:
        stmt = select(func.coalesce(func.max(Turn.turn_no), 0)).where(Turn.conversation_id == conversation_id)
        current_max = self.session.execute(stmt).scalar_one()
        return int(current_max) + 1

    def create(
        self,
        conversation_id: str,
        turn_no: int,
        user_msg_id: Optional[str] = None,
        bot_msg_id: Optional[str] = None,
        ctx_snapshot: Optional[Dict[str, Any]] = None,
    ) -> Turn:
        row = Turn(
            conversation_id=conversation_id,
            turn_no=turn_no,
            user_msg_id=user_msg_id,
            bot_msg_id=bot_msg_id,
            ctx_snapshot=ctx_snapshot or {},
        )
        self.session.add(row)
        return row

