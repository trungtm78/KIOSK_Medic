from pathlib import Path
from typing import Any, Dict, Optional
from ..servicelogs.servicelogger import logger
from .reply_service import ReplyService
from .metrics_service import MetricsService
from .session_service import SessionService
from .queue_service import QueueService
from .map_service import MapService
from .kb_service import KBService
from .handoff_service import HandoffService
from .info_lookup_service import InfoLookupService, get_info_lookup_service
from ..core.state_machine.context import ChatContext
from ..core.state_machine.actions import Actions
from ..core.state_machine.guards import Guards


class ConversationManager:
    """Service wrapper that wires Core FSM ConversationManager with default services.

    Supports two modes:
    - In-memory (default): useful for local/dev without DB.
    - SQL mode: if tenant/channel/client_conversation_id provided and DB is configured.
    """

    def __init__(
        self,
        statechart_path: Optional[str] = None,
        *,
        tenant_id: Optional[str] = None,
        session_id: Optional[str] = None,
        initial_state: Optional[str] = None,
        initial_memory: Optional[Dict[str, Any]] = None,
    ):
        chart_path = statechart_path or str(Path(__file__).resolve().parents[1] / 'core' / 'state_machine' / 'statechart.sismic.yaml')

        self._chart_path = chart_path
        self._tenant_id = tenant_id
        self._session_id = session_id or "inmem"
        self._transition_history: list[Dict[str, Any]] = []

        reply = ReplyService()
        self.reply = reply
        metrics = MetricsService()
        session_svc = SessionService()
        queue = QueueService() # Adapter to queue service
        maps = MapService()
        kb = KBService()
        handoff = HandoffService()
        info = get_info_lookup_service()

        self._convo_state = initial_state or "START"
        self._convo_memory = initial_memory or {}

        # Build runtime context
        self.ctx = ChatContext(tenant_id=tenant_id, session_id=self._session_id)
        self.ctx.state = self._convo_state
        if self._convo_memory.get("slots"):
            self.ctx.slots.update(self._convo_memory.get("slots", {}))
        if self._convo_memory.get("current_flow"):
            self.ctx.current_flow = self._convo_memory.get("current_flow")
        if self._convo_memory.get("flow_required_slots"):
            self.ctx.flow.required_slots = list(self._convo_memory.get("flow_required_slots", []))
        if self._convo_memory.get("waiting_confirm"):
            self.ctx.waiting_confirm = bool(self._convo_memory.get("waiting_confirm"))

        self.guards = Guards(self.ctx)
        self.actions = Actions(
            self.ctx,
            queue_svc=queue,
            map_svc=maps,
            kb_svc=kb,
            info_svc=info,
            reply=reply,
            metrics=metrics,
        )
        self.reply_outbox: list[dict[str, Any]] = []
        self.reply.bind_outbox(self.reply_outbox)

        # Load Sismic
        from sismic.io import import_from_yaml
        from sismic.interpreter import Interpreter

        chart = import_from_yaml(filepath=chart_path)
        env = {
            'guards': self.guards,
            'actions': self.actions,
            'reply': reply,
            'metrics': metrics,
            'session': session_svc,
            'handoff': handoff,
        }
        self._interpreter = Interpreter(chart, initial_context=env)
        self._interpreter.execute_once()
        self._sync_state()
        logger.info(f"FSM ConversationManager initialized with chart: {chart_path}")

    """
    Dispatch an event to the FSM, optionally with payload (e.g., NLU results, slots).
    """
    def dispatch(self, event: str, payload: Optional[Dict[str, Any]] = None) -> None:
        # capture from_state for transition logging
        from_state = self.active_leaf_state() or self.ctx.state
        if payload:
            nlu = payload.get('nlu') if isinstance(payload, dict) else None
            if nlu:
                self.ctx.nlu.intent = nlu.get('intent')
                self.ctx.nlu.confidence = nlu.get('confidence')
                self.ctx.nlu.ambiguous_entities = nlu.get('ambiguous_entities', {})
            slots = payload.get('slots') if isinstance(payload, dict) else None
            if slots:
                self.ctx.slots.update(slots)
        event_kwargs: Dict[str, Any] = payload if isinstance(payload, dict) else {}
        logger.debug(
            "FSM dispatch start conversation_id=%s event=%s from_state=%s payload=%s",
            self._session_id,
            event,
            from_state,
            payload,
        )
        self._interpreter.queue(event, **event_kwargs)
        self._interpreter.execute()
        self._sync_state()
        logger.debug(
            "FSM dispatch state updated conversation_id=%s state=%s",
            self._session_id,
            self.ctx.state,
        )
        # log transition if repo supports it
        to_state = self.active_leaf_state() or self.ctx.state
        logger.debug(
            "FSM dispatch completed conversation_id=%s event=%s from_state=%s to_state=%s",
            self._session_id,
            event,
            from_state,
            to_state,
        )
        self._transition_history.append(
            {
                "from_state": from_state,
                "event": event,
                "to_state": to_state,
            }
        )

    def close(self) -> None:
        """Placeholder for interface parity; no persistent resources to release."""
        return None

    def active_leaf_state(self) -> Optional[str]:
        try:
            config = [name for name in self._interpreter.configuration if name not in ("ROOT", None)]
            if not config:
                return None
            return max(config, key=lambda name: (name.count("."), len(name)))
        except Exception:
            return None

    def _sync_state(self) -> None:
        state_path = self.active_leaf_state() or self.ctx.state
        if state_path:
            self.ctx.state = state_path
            self._convo_state = state_path
        self._convo_memory = {
            "slots": dict(self.ctx.slots),
            "current_flow": self.ctx.current_flow,
            "flow_required_slots": list(self.ctx.flow.required_slots),
            "waiting_confirm": self.ctx.waiting_confirm,
        }

    def snapshot(self) -> Dict[str, Any]:
        return {
            "state": self._convo_state,
            "memory": dict(self._convo_memory),
        }

    def transition_history(self) -> list[Dict[str, Any]]:
        return list(self._transition_history)
