from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ConversationRecord:
    id: str
    tenant_id: Optional[str]
    fsm_id: str
    state: str
    memory: Dict[str, Any]

