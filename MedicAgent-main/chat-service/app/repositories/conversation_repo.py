from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Conversation, StateTransition


class ConversationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # Basic CRUD
    def get(self, conversation_id: str) -> Optional[Conversation]:
        return self.session.get(Conversation, conversation_id)

    def create(self, conversation_id: str, tenant_id: Optional[str], fsm_id: str, *, channel: Optional[str] = None, client_conversation_id: Optional[str] = None) -> Conversation:
        conv = Conversation(id=conversation_id, tenant_id=tenant_id, fsm_id=fsm_id, status="active", channel=channel, client_conversation_id=client_conversation_id)
        self.session.add(conv)
        return conv

    def ensure(self, conversation_id: str, tenant_id: Optional[str], fsm_id: str, *, channel: Optional[str] = None, client_conversation_id: Optional[str] = None) -> Conversation:
        conv = self.get(conversation_id)
        if conv is None:
            conv = self.create(conversation_id, tenant_id, fsm_id, channel=channel, client_conversation_id=client_conversation_id)
        return conv

    # Look up by client mapping key
    def get_by_client_key(self, tenant_id: Optional[str], channel: Optional[str], client_conversation_id: str) -> Optional[Conversation]:
        stmt = select(Conversation).where(
            Conversation.tenant_id == tenant_id,
            Conversation.channel == channel,
            Conversation.client_conversation_id == client_conversation_id,
        ).limit(1)
        return self.session.execute(stmt).scalars().first()
    
    
    """
    Ensure conversation by client mapping key; create if not exists.
    """
    def ensure_by_client_key(self, 
                             tenant_id: Optional[str], 
                             channel: Optional[str], 
                             client_conversation_id: str, 
                             *, 
                             fsm_id: str, 
                             conversation_id: Optional[str] = None
                             ) -> Conversation:
        conv = self.get_by_client_key(tenant_id, channel, client_conversation_id)
        if conv:
            return conv
        # Create new conversation using provided server id or let DB default
        if conversation_id is None:
            # Create without explicit id; SQLAlchemy default/gen handled by model if configured, else require caller to pass
            conv = Conversation(tenant_id=tenant_id, channel=channel, client_conversation_id=client_conversation_id, fsm_id=fsm_id, status="active")
            self.session.add(conv)
            return conv
        return self.create(conversation_id, tenant_id, fsm_id, channel=channel, client_conversation_id=client_conversation_id)

    # FSM-specific helpers
    def save_state(self, conversation_id: str, fsm_id: str, state: str, memory: Dict[str, Any]) -> None:
        conv = self.ensure(conversation_id, tenant_id=conv.tenant_id if (conv := self.get(conversation_id)) else None, fsm_id=fsm_id)
        conv.fsm_id = fsm_id
        conv.state = state
        conv.memory = memory
        self.session.add(conv)

    def bind_client_conversation(self, conversation_id: str, tenant_id: Optional[str], channel: Optional[str], client_conversation_id: str) -> Conversation:
        conv = self.ensure(conversation_id, tenant_id=tenant_id, fsm_id="chat_service@v1", channel=channel)
        conv.tenant_id = tenant_id
        conv.channel = channel
        conv.client_conversation_id = client_conversation_id
        self.session.add(conv)
        return conv

    def log_transition(
        self,
        conversation_id: str,
        fsm_id: str,
        from_state: str,
        event: str,
        to_state: str,
        guard_eval: Optional[Dict[str, Any]] = None,
    ) -> StateTransition:
        row = StateTransition(
            conversation_id=conversation_id,
            fsm_id=fsm_id,
            from_state=from_state,
            event=event,
            to_state=to_state,
            guard_eval=guard_eval or {},
        )
        self.session.add(row)
        return row
