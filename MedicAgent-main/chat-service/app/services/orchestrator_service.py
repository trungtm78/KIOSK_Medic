"""
FSM-backed Orchestrator: feeds NLU results into the Sismic-based ConversationManager.
"""
import asyncio
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional
from uuid import uuid4

from ..core.db import get_session_factory, session_scope
from ..models import Conversation, Message
from ..schemas.dto import Intent
from ..servicelogs.servicelogger import logger
from .conversation_cache import ConversationCache, ConversationRuntime
from .conversation_manager import ConversationManager
from .nlu_service import NLUResult, NLUService, get_nlu_service
from .triage_service import TriageService, get_triage_service
from .intent_classifier import get_intent_classifier


@dataclass
class HandleResult:
    intent: Optional[Intent]
    status: Literal["success", "error"]
    message: Optional[str] = None


class OrchestratorService:
    def __init__(self, conversation_manager: Optional[ConversationManager] = None, *, ttl_seconds: int = 120):
        # Default in-memory CM for quick/local usage
        self.default_cm = conversation_manager or ConversationManager()
        self.cache = ConversationCache(ttl_seconds=ttl_seconds)

    def handle_user_message(
        self,
        *,
        # _db_session: Any,
        tenant_id: str,
        channel: str,
        client_conversation_id: str,
        role: str,
        content: str,
        idempotency_key: str,
        chart_path: Optional[str] = None,
        stream_service: Optional[Any] = None,
        lang: str = "vi",
    ) -> Dict[str, str]:
        """High-level handler: run NLU, drive FSM, manage cache, and optionally publish SSE.
        Returns an ack dict: { conversation_id (client), session_id (server), message_id, stream_url }
        """
        self._cleanup_expired_conversations()

        chart_path = chart_path or str(
            Path(__file__).resolve().parents[1]
            / "core"
            / "state_machine"
            / "statechart.sismic.yaml"
        )

        def factory(key: str) -> ConversationRuntime:
            session_id = str(uuid4())
            manager = ConversationManager(
                statechart_path=chart_path,
                tenant_id=tenant_id,
                session_id=session_id,
            )
            return ConversationRuntime(
                key=key,
                tenant_id=tenant_id,
                channel=channel,
                client_conversation_id=client_conversation_id,
                session_id=session_id,
                manager=manager,
            )
        # Lấy ConversationRuntime từ cache hoặc tạo mới nếu chưa tồn tại
        runtime, _created = self.cache.get_or_create(
            tenant_id=tenant_id,
            channel=channel,
            client_conversation_id=client_conversation_id,
            factory=factory,
        )

        nlu_svc: NLUService = get_nlu_service()
        triage_svc: TriageService = get_triage_service()
        intent_classifier = get_intent_classifier()
        logger.debug(f"Intent classifier loaded: {intent_classifier is not None}")
        
        # Lấy context hiện tại và trạng thái trước khi xử lý tin nhắn
        ctx = runtime.manager.ctx
        content = content.lower().strip()
        ctx.slots["last_user_message"] = content
        state_before = runtime.manager.active_leaf_state() or runtime.manager.snapshot()["state"]
        # in_confirm_state = state_before.endswith("FLOW_ISSUE_TICKET.CONFIRM")

        # Chuẩn bị meta và payload ban đầu
        # Event mặc định là USER_MESSAGE, có thể thay đổi tùy theo xử lý
        message_meta: Dict[str, Any] = {"idempotency_key": idempotency_key}
        event_name = "USER_MESSAGE"
        slots_payload: Dict[str, Any] = dict(ctx.slots)
        nlu_payload: Dict[str, Any] = {
            "intent": ctx.nlu.intent,
            "confidence": ctx.nlu.confidence,
            "ambiguous_entities": dict(getattr(ctx.nlu, "ambiguous_entities", {}) or {}),
        }

        ml_prediction = None
        def _resolve_hospital_id() -> Optional[str]:
            slot_value = ctx.slots.get("hospital_id")
            if slot_value not in (None, "", []):
                return str(slot_value)
            context_value = getattr(ctx, "hospital_id", None)
            if context_value not in (None, "", []):
                return str(context_value)
            if tenant_id not in (None, "", []):
                return str(tenant_id)
            return None
        
        # ----------------- Internal helper ---------------------- 
        def _ctx_nlu_payload() -> Dict[str, Any]:
            return {
                "intent": ctx.nlu.intent,
                "confidence": ctx.nlu.confidence,
                "ambiguous_entities": dict(getattr(ctx.nlu, "ambiguous_entities", {}) or {}),
            }
        # handled_slot = False

        state_handlers: Dict[str, Callable[[], None]] = {}

        def register_state(state: str) -> Callable[[Callable[[], None]], Callable[[], None]]:
            def decorator(func: Callable[[], None]) -> Callable[[], None]:
                state_handlers[state] = func
                return func
            return decorator

        def _handle_direct_slot(slot_name: str, *, threshold: float) -> None:
            nonlocal event_name, slots_payload, nlu_payload
            existing_value = ctx.slots.get(slot_name)
            if existing_value not in (None, "", []):
                logger.debug("Skip updating slot=%s because value already exists", slot_name)
                return
            extraction = nlu_svc.extract_slot(
                slot_name=slot_name,
                text=content,
                lang=lang,
                chat_context=ctx,
            )
            slot_value = extraction.value if extraction.value not in (None, "", []) else None
            slot_conf = extraction.confidence or 0.0
            if extraction.intent:
                ctx.nlu.intent = extraction.intent
                ctx.nlu.confidence = extraction.confidence
            if extraction.ambiguous_entities:
                ctx.nlu.ambiguous_entities = extraction.ambiguous_entities  # type: ignore[attr-defined]
            if slot_value is not None and slot_conf >= threshold:
                logger.debug(
                    "Slot filled slot=%s value=%s confidence=%.2f",
                    slot_name,
                    slot_value,
                    slot_conf,
                )
                ctx.slots[slot_name] = slot_value
                message_meta["slot"] = {"key": slot_name, "value": slot_value, "confidence": slot_conf}
                nlu_payload = _ctx_nlu_payload()
                slots_payload = dict(ctx.slots)
                event_name = "USER_MESSAGE"
            else:
                message_meta["slot_attempt"] = {
                    "key": slot_name,
                    "confidence": slot_conf,
                    "raw": content.lower().strip(),
                }
                nlu_payload = _ctx_nlu_payload()
                slots_payload = dict(ctx.slots)
        @register_state("FLOW_ISSUE_TICKET.ASK_HEALTH_BOOK.WARN_NO_HEALTH_BOOK")
        @register_state("FLOW_ISSUE_TICKET.CONFIRM")
        def _handle_confirmation_state() -> None:
            logger.debug("Handling confirmation state")
            nonlocal event_name, nlu_payload, slots_payload,ml_prediction
            
            if ml_prediction and ml_prediction.label == "confirm_yes":
                event_name = "CONFIRM_YES"
                message_meta["confirmation"] = "yes"
                ctx.waiting_confirm = False
            elif ml_prediction and ml_prediction.label == "confirm_no":
                event_name = "CONFIRM_NO"
                message_meta["confirmation"] = "no"
                ctx.waiting_confirm = False
            else:
                message_meta["confirmation"] = "unknown"
            nlu_payload = _ctx_nlu_payload()
            slots_payload = dict(ctx.slots)
            
            
        
        @register_state("FLOW_TRIAGE.ASK_EMERGENCY")
        def _handle_emergency_response() -> None:
            nonlocal event_name, nlu_payload, slots_payload
            # Init 
            if ctx.slots.get("is_emergency") not in {"yes", "no"}: ctx.slots["is_emergency"] = "unknown" 
            verdict = nlu_svc.classify_confirmation(content, lang=lang)
            if verdict == "yes":
                event_name = "USER_MESSAGE"
                message_meta["emergency_response"] = "yes"
                ctx.slots["is_emergency"] = "yes"
            elif verdict == "no":
                event_name = "USER_MESSAGE"
                message_meta["emergency_response"] = "no"
                ctx.slots["is_emergency"] = 'no'
            elif nlu_svc.is_emergency(content, lang=lang):
                event_name = "USER_MESSAGE"
                message_meta["emergency_response"] = "yes"
                ctx.slots["is_emergency"] = 'yes'
            nlu_payload = _ctx_nlu_payload()
            slots_payload = dict(ctx.slots)

        @register_state("FLOW_TRIAGE.ASK_SYMPTOM")
        def _handle_main_symptom() -> None:
            nonlocal nlu_payload, slots_payload
            # handled_slot = True
            ctx.nlu.intent = "triage"
            ctx.nlu.ambiguous_entities = {}

            symptom_candidates: List[Dict[str, Any]] = []
            ctx.nlu.confidence = 0.0
            ctx.slots.pop("triage_symptoms", None)
            ctx.slots.pop("main_symptom", None)
            message_meta["slot_attempt"] = {
                "key": "main_symptom",
                "confidence": ctx.nlu.confidence,
                "raw": content.strip(),
            }

            triage_suggestions: List[Dict[str, Any]] = [] # Suggested triage units
            syndrome_candidates_payload: List[Dict[str, Any]] = []
            hospital_id = _resolve_hospital_id()
            suggestion_result = triage_svc.suggest_units(
                symptom_candidates,
                hospital_id=hospital_id,
                top_n=1,
                text=content,
            )
            for candidate in suggestion_result.syndromes:
                matches_payload = [dict(match) for match in candidate.matches]
                syndrome_candidates_payload.append(
                    {
                        "syndrome_id": candidate.syndrome_id,
                        "name": candidate.name,
                        "score": candidate.score,
                        "matches": matches_payload,
                    }
                )
            if suggestion_result.syndromes:
                ctx.nlu.confidence = suggestion_result.syndromes[0].score
            triage_suggestions = [dict(item) for item in suggestion_result.triage_units]
            logger.debug(f"triage_suggestions: {type(triage_suggestions)} %s", triage_suggestions)

            if syndrome_candidates_payload:
                ctx.slots["triage_syndrome_candidates"] = syndrome_candidates_payload
                message_meta["triage_syndrome_candidates"] = syndrome_candidates_payload
            else:
                ctx.slots.pop("triage_syndrome_candidates", None)

            if triage_suggestions:
                ctx.slots["triage_suggestions"] = triage_suggestions
                ctx.slots["department_id"] = triage_suggestions[0].get("department_id")
                message_meta["triage_suggestions"] = triage_suggestions
            else:
                ctx.slots.pop("triage_suggestions", None)

            nlu_payload = {
                "intent": ctx.nlu.intent,
                "confidence": ctx.nlu.confidence,
                "ambiguous_entities": {},
            }
            slots_payload = dict(ctx.slots)
            
        @register_state("ORCHESTRATING")
        def _handle_orchestrating_state() -> None:
            nonlocal nlu_payload, slots_payload
            nlu: NLUResult = nlu_svc.infer_intent(
                content,
                lang=lang,
                chat_context=ctx,
            )
            ctx.nlu.intent = nlu.intent.value if hasattr(nlu.intent, "value") else str(nlu.intent)
            ctx.nlu.confidence = getattr(nlu, "confidence", 0.0)
            ctx.nlu.ambiguous_entities = getattr(nlu, "ambiguous", {}) or {}

            slots_from_nlu = getattr(nlu, "slots", {}) or {}
            if slots_from_nlu:
                ctx.slots.update(slots_from_nlu)
            if nlu.intent == Intent.FAQ:
                ctx.slots["info_question"] = content.strip()
                if nlu.entities:
                    topic_candidate = nlu.entities[0]
                    if topic_candidate:
                        ctx.slots["info_topic"] = topic_candidate

            nlu_payload = {
                "intent": ctx.nlu.intent,
                "confidence": ctx.nlu.confidence,
                "ambiguous_entities": dict(ctx.nlu.ambiguous_entities or {}),
            }
            slots_payload = dict(ctx.slots)
            
        if intent_classifier:
            try:
                ml_prediction = intent_classifier.predict(content.lower())
                logger.debug(f"Probabilites of intent: {ml_prediction.probabilities}")
                logger.debug("Info lookup topic ask - ML predicted intent: %s", ml_prediction.label)
            except Exception as exc:  # pragma: no cover
                logger.warning("Intent classifier prediction failed: %s", exc)
            
        @register_state("FLOW_INFO_LOOKUP.ASK_TOPIC")
        def _handle_info_lookup_topic_state() -> None:
            logger.debug("Handling info lookup topic ask state")
            nonlocal nlu_payload, slots_payload, event_name, ml_prediction
            if ml_prediction and (ml_prediction.label in {"confirm_no","conversation_end_reset"}):
                ctx.nlu.intent = "deny"
                logger.debug(f"nlu.intent set to: {ctx.nlu.intent}")
                ctx.nlu.confidence = 1.0
                ctx.nlu.ambiguous_entities = {}
                nlu_payload = _ctx_nlu_payload()
                slots_payload = dict(ctx.slots)
                event_name = "completion"
                return
            elif ml_prediction and ml_prediction.label in {"insurance_policy",
                                                           "service_price_lookup",
                                                           "kiosk_navigation",
                                                           "info_lookup_generic",
                                                           "hospital_workflow"}:
                ctx.nlu.intent = ml_prediction.label
                ctx.nlu.confidence = ml_prediction.score
                ctx.slots["info_topic"] = ml_prediction.label
                logger.debug(f'Slot filled info_topic: {ctx.slots["info_topic"]}')
                ctx.slots["info_question"] = content.lower().strip()
                if ml_prediction.label == "kiosk_navigation":
                    dest_slot = nlu_svc.extract_destination_slot(
                        text=content,
                        lang=lang,
                        chat_context=ctx,
                    )
                    if dest_slot.value:
                        ctx.slots["to_poi"] = dest_slot.value
                        message_meta["slot"] = {
                            "key": "to_poi",
                            "value": dest_slot.value,
                            "confidence": dest_slot.confidence,
                        }
                nlu_payload = {
                    "intent": ctx.nlu.intent,
                    "confidence": ctx.nlu.confidence,
                    # "ambiguous_entities": dict(ctx.nlu.ambiguous_entities or {}),
                }
                slots_payload = dict(ctx.slots)

        @register_state("FLOW_ISSUE_TICKET.GATHER.ASK_SERVICE_PACKAGE")
        def _state_ask_service_package() -> None:
            _handle_direct_slot("service_type", threshold=0.2)

        @register_state("FLOW_ISSUE_TICKET.GATHER.ASK_DEPARTMENT")
        def _state_ask_department() -> None:
            _handle_direct_slot("department_id", threshold=0.6)

        @register_state("FLOW_TRIAGE.SHOW_SUGGESTIONS")
        def _state_show_suggestions() -> None:
            _handle_direct_slot("department_id", threshold=0.6)

        @register_state("FLOW_ISSUE_TICKET.ASK_HEALTH_BOOK")
        def _state_ask_health_book() -> None:
            logger.debug("Handling health book confirmation state")
            nonlocal nlu_payload, slots_payload, ml_prediction
                    
            if ml_prediction and ml_prediction.label == "confirm_yes":
                message_meta["health_book_confirmation"] = "yes"
                nlu_payload = {"intent": "affirm", "confidence": 1.0, "ambiguous_entities": {}}
                ctx.nlu.intent = "yes"
            elif ml_prediction and ml_prediction.label == "confirm_no":
                message_meta["health_book_confirmation"] = "no"
                nlu_payload = {"intent": "deny", "confidence": 1.0, "ambiguous_entities": {}}
                ctx.nlu.intent = "no"
            else:
                message_meta["health_book_confirmation"] = "unknown"
                nlu: NLUResult = nlu_svc.infer_intent(
                    content,
                    lang=lang,
                    chat_context=ctx,
                )
                nlu_payload = {
                    "intent": nlu.intent.value if hasattr(nlu.intent, "value") else str(nlu.intent),
                    "confidence": getattr(nlu, "confidence", None),
                    "ambiguous_entities": getattr(nlu, "ambiguous", {}) or {},
                }
                slots_payload = getattr(nlu, "slots", {}) or {}
                if slots_payload:
                    ctx.slots.update(slots_payload)
                    slots_payload = dict(ctx.slots)
                else:
                    slots_payload = dict(ctx.slots)
            # if verdict in {"yes", "no"}:
            #     slots_payload = dict(ctx.slots)
        # ------------------ Main processing ----------------------
        if ml_prediction and ml_prediction.label == "conversation_end_reset":
            event_name = "RESET_CONVERSATION"
            message_meta["conversation_reset"] = "requested_by_user"
            nlu_payload = {"intent": "conversation_end_reset", 
                           "confidence": ml_prediction.score, 
                           "ambiguous_entities": {} }
        else:    
            handler = state_handlers.get(state_before)
            if handler is not None:
                handler()

        message_id = runtime.append_message(
            role=role,
            content=content,
            meta=message_meta,
            nlu={"intent": nlu_payload["intent"], "confidence": nlu_payload["confidence"]},
        )
        
        logger.debug("Dispatching event=%s to state=%s", event_name, state_before)
        runtime.manager.dispatch(
            event_name,
            payload={
                "nlu": nlu_payload,
                "slots": slots_payload,
            },
        )
        setattr(ctx, "last_prompted_slot", None)
        setattr(ctx, "last_prompted_identity", None)

        state_path = runtime.manager.active_leaf_state() or runtime.manager.snapshot()["state"]
        if state_path == "FLOW_ISSUE_TICKET.ASK_HEALTH_BOOK.WARN_NO_HEALTH_BOOK":
            runtime.manager.dispatch("completion")
            state_path = runtime.manager.active_leaf_state() or runtime.manager.snapshot()["state"]
        outbox_entries = list(runtime.manager.reply_outbox)
        runtime.manager.reply_outbox.clear()
        runtime.outbox.extend(outbox_entries)

        if stream_service is not None:
            publish_events = [
                ("message.completed", {"message_id": message_id, "content": content}),
                *[(entry["event"], entry["data"]) for entry in outbox_entries],
                ("state.updated", {"state": state_path}),
            ]
            publish_coroutines = [
                stream_service.publish(client_conversation_id, event, payload)
                for event, payload in publish_events
            ]
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                for coro in publish_coroutines:
                    asyncio.run(coro)
            else:
                for coro in publish_coroutines:
                    loop.create_task(coro)

        # Finalize if reached END state
        if state_path.split(".")[-1].upper() == "END":
            self._finalize_runtime(runtime, reason="completed")

        return {
            "conversation_id": client_conversation_id,
            "session_id": runtime.session_id,
            "message_id": message_id,
            "stream_url": f"/v1/chat/{client_conversation_id}/stream",
        }

    def _cleanup_expired_conversations(self) -> None:
        logger.info("Cleaning up expired conversations from cache")
        expired = self.cache.collect_expired()
        if not expired:
            return
        for runtime in expired:
            self._finalize_runtime(runtime, reason="timeout", removed_from_cache=True)

    def _finalize_runtime(self, runtime: ConversationRuntime, reason: str, *, removed_from_cache: bool = False) -> None:
        logger.info("Finalizing conversation runtime", extra={"conversation_id": runtime.client_conversation_id, "reason": reason})
        runtime.mark_closed(reason)
        if not removed_from_cache:
            self.cache.remove(runtime)
        try:
            self._persist_runtime(runtime)
        except Exception:
            logger.exception("Failed to persist conversation runtime", extra={"conversation_id": runtime.client_conversation_id})
        finally:
            runtime.manager.close()

    def _persist_runtime(self, runtime: ConversationRuntime) -> None:
        snapshot = runtime.snapshot()
        snapshot_memory = dict(snapshot["memory"])
        if runtime.ended_reason:
            snapshot_memory["ended_reason"] = runtime.ended_reason
        SessionFactory = get_session_factory()
        with session_scope(SessionFactory) as session:
            conversation = session.get(Conversation, runtime.session_id)
            if conversation is None:
                conversation = Conversation(
                    id=runtime.session_id,
                    tenant_id=runtime.tenant_id,
                    channel=runtime.channel,
                    client_conversation_id=runtime.client_conversation_id,
                    status=runtime.status,
                    fsm_id="chat_service@v1",
                    state=snapshot["state"],
                    memory=snapshot_memory,
                )
                session.add(conversation)
            else:
                conversation.tenant_id = runtime.tenant_id
                conversation.channel = runtime.channel
                conversation.client_conversation_id = runtime.client_conversation_id
                conversation.status = runtime.status
                conversation.state = snapshot["state"]
                conversation.memory = snapshot_memory

            for message in runtime.messages:
                existing_message = session.get(Message, message.id)
                if existing_message is None:
                    session.add(
                        Message(
                            id=message.id,
                            conversation_id=conversation.id,
                            role=message.role,
                            content=message.content,
                            meta={**message.meta, "nlu": message.nlu},
                        )
                    )

        logger.info(
            "Persisted conversation runtime",
            extra={
                "conversation_id": runtime.client_conversation_id,
                "session_id": runtime.session_id,
                "reason": runtime.ended_reason or "unknown",
                "state": snapshot["state"],
            },
        )

    def force_clear_conversation(
        self,
        client_conversation_id: str,
        *,
        tenant_id: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> bool:
        """Remove a cached conversation runtime, intended for debugging."""
        for runtime in self.cache.items():
            if runtime.client_conversation_id != client_conversation_id:
                continue
            if tenant_id and runtime.tenant_id != tenant_id:
                continue
            if channel and runtime.channel != channel:
                continue
            runtime.mark_closed("force-cleared")
            self.cache.remove(runtime)
            runtime.manager.close()
            return True
        return False

    def force_clear_all_conversations(self) -> int:
        """Clear all cached conversations, returning the number removed."""
        removed = 0
        for runtime in self.cache.items():
            runtime.mark_closed("force-cleared-all")
            self.cache.remove(runtime)
            runtime.manager.close()
            removed += 1
        return removed

    def list_cached_conversations(self) -> Dict[str, Any]:
        """Return summary data for cached conversations."""
        items = []
        for runtime in self.cache.items():
            items.append(
                {
                    "tenant_id": runtime.tenant_id,
                    "channel": runtime.channel,
                    "conversation_id": runtime.client_conversation_id,
                    "session_id": runtime.session_id,
                    "status": runtime.status,
                    "updated_at": datetime.fromtimestamp(runtime.updated_at).isoformat(),
                }
            )
        return {"count": len(items), "items": items}

def _build_default_orchestrator() -> OrchestratorService:
    return OrchestratorService()


@lru_cache(maxsize=1)
def get_orchestrator_service() -> OrchestratorService:
    """P2.1 - lru_cache replaces global singleton."""
    return _build_default_orchestrator()
