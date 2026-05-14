from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from ..models import Task


class TaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        turn_id: str,
        kind: str,
        status: str = "pending",
        input: Optional[Dict[str, Any]] = None,
    ) -> Task:
        row = Task(turn_id=turn_id, kind=kind, status=status, input=input or {})
        self.session.add(row)
        return row

    def update_status(self, task_id: str, status: str, output: Optional[Dict[str, Any]] = None) -> Optional[Task]:
        row = self.session.get(Task, task_id)
        if not row:
            return None
        row.status = status
        if output is not None:
            row.output = output
        self.session.add(row)
        return row

