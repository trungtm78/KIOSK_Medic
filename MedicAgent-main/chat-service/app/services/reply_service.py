from typing import Any, Dict, List, Optional
from ..servicelogs.servicelogger import logger


class ReplyService:
    def __init__(self) -> None:
        self._outbox: Optional[List[Dict[str, Any]]] = None

    def bind_outbox(self, outbox: List[Dict[str, Any]]) -> None:
        self._outbox = outbox

    def _emit(self, event: str, payload: Dict[str, Any]) -> None:
        if self._outbox is not None:
            self._outbox.append({"event": event, "data": payload})

    def say(self, text: str) -> None:
        logger.info(f"BOT: {text}")
        self._emit("bot.message", {"role": "assistant", "content": text})

    def ask(
        self,
        prompt: str,
        *,
        slot: Optional[str] = None,
        state_hint: Optional[str] = None,
        required: bool = True,
        options: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        logger.info(f"BOT ASK: {prompt} (slot={slot}, state={state_hint})")
        payload: Dict[str, Any] = {"prompt": prompt}
        if slot:
            payload["slot"] = slot
        if state_hint:
            payload["state"] = state_hint
        if required is not None:
            payload["required"] = required
        if options is not None:
            payload["options"] = options
        self._emit("bot.ask", payload)
    
    def static_ask(self, payload: Dict[str, Any]) -> None:
        logger.info(f"BOT STATIC ASK: {payload}")
        self._emit("bot.ask", payload)

    def summarize(self, slots: Dict[str, Any]) -> None:
        logger.info(f"BOT SUMMARY: {slots}")
        self._emit("bot.summary", {"slots": slots})

    def ticket_done(self, ticket: Dict[str, Any]) -> None:
        logger.info(f"TICKET CREATED: {ticket}")
        self._emit("bot.ticket", {"ticket": ticket})

    def show_route(self, route: Dict[str, Any]) -> None:
        logger.info(f"ROUTE: {route}")
        self._emit("bot.route", {"route": route})

    def show_checklist(self, info: Dict[str, Any]) -> None:
        logger.info(f"CHECKLIST: {info}")
        self._emit("bot.checklist", {"info": info})

    def show_triage_suggestions(self, suggestions: Optional[Any]) -> None:
        logger.info(f"TRIAGE SUGGESTIONS: {suggestions}")
        self._emit("bot.triage", {"suggestions": suggestions})

    def smalltalk(self) -> None:
        logger.info("SMALLTALK: (placeholder response)")
        self._emit("bot.smalltalk", {})

    def suggest(self, items: List[str]) -> None:
        logger.info(f"SUGGEST: {items}")
        self._emit("bot.suggest", {"items": items})
        
    def show_info(self, info: Dict[str, Any]) -> None:
        logger.info(f"INFO: {info}")
        self._emit("bot.info", {"info": info})
