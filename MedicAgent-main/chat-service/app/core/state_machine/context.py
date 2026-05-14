from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class NLUContext:
    intent: Optional[str] = None
    confidence: Optional[float] = None
    ambiguous_entities: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowConfig:
    name: Optional[str] = None
    required_slots: List[str] = field(default_factory=list)


@dataclass
class ChatContext:
    tenant_id: Optional[str] = None
    session_id: Optional[str] = None
    state: str = "START"
    current_flow: Optional[str] = None
    waiting_confirm: bool = False
    awaiting_health_book_confirmation: bool = False
    last_user_message: Optional[str] = None
    suppress_hint_once: bool = False
    nlu: NLUContext = field(default_factory=NLUContext)
    flow: FlowConfig = field(default_factory=FlowConfig)
    slots: Dict[str, Any] = field(default_factory=dict)

    def start_flow(self, name: str):
        self.current_flow = name
        self.flow = FlowConfig(name=name)
        # required_slots should be set by the orchestrator/loader based on design metadata

    def reset(self):
        self.current_flow = None
        self.flow = FlowConfig()
        self.waiting_confirm = False
        self.awaiting_health_book_confirmation = False
        # Do not wipe slots entirely; keep as per product choice. Here, we reset minimal.

    def next_missing_slot(self) -> Tuple[str, str]:
        for key in self.flow.required_slots:
            if self.slots.get(key) in (None, "", []):
                # Basic prompt; in real implementation, fetch from prompt templates/i18n
                return key, f"Please provide '{key}'"
        return "", ""
