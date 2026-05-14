# app/core/state_machine/guards.py
INFO_LOOKUP_TOPIC_LABELS = {
    "insurance_policy",
    "service_pricing",  # backward compatibility with rule-based classifier
    "service_price_lookup",
    "info_lookup_generic",
    "kiosk_navigation",
    "hospital_workflow",
}


class Guards:
    def __init__(self, ctx):
        self.ctx = ctx

    def intent_is(self, name: str) -> bool:
        return self.ctx.nlu.intent == name

    def confidence_gte(self, threshold: float) -> bool:
        return (self.ctx.nlu.confidence or 0) >= threshold

    def all_required_slots_ready(self) -> bool:
        required = self.ctx.flow.required_slots
        return all(self.ctx.slots.get(k) not in (None, "", []) for k in required)

    def slot_filled(self, slot: str) -> bool:
        value = self.ctx.slots.get(slot)
        return value not in (None, "", [])

    def ambiguous_entity_detected(self) -> bool:
        return bool(self.ctx.nlu.ambiguous_entities)

    def allow_intent_switch(self, target_intent: str) -> bool:
        # tránh switch khi đang đợi confirm
        if self.ctx.state.endswith(".CONFIRM"):
            return False
        return self.ctx.current_flow != target_intent

    def is_affirm(self) -> bool:
        intent = (self.ctx.nlu.intent or "").lower()
        return intent in {"affirm", "yes", "confirm_yes", "positive"}
    
    def is_emergency(self, expect: str) -> bool:
        value = self.ctx.slots.get("is_emergency") or "unknown"
        return value == expect

    def is_deny(self) -> bool:
        intent = (self.ctx.nlu.intent or "").lower()
        return intent in {"deny", "no", "confirm_no", "negative"}

    def triage_confident_gte(self, threshold: float) -> bool:
        intent = (self.ctx.nlu.intent or "").lower()
        if intent != "triage":
            return False
        return (self.ctx.nlu.confidence or 0.0) >= threshold

    def is_triage_suggest(self) -> bool:
        value = self.ctx.slots.get("main_symptom")
        return value not in (None, "", [])

    def has_triage_suggestions(self) -> bool:
        suggestions = self.ctx.slots.get("triage_suggestions")
        if isinstance(suggestions, (list, tuple)):
            return len(suggestions) > 0
        return suggestions not in (None, "", [])

    def info_topic_known(self) -> bool:
        value = self.ctx.slots.get("info_topic")
        if value not in (None, "", []):
            return True
        intent = (self.ctx.nlu.intent or "").lower()
        return intent in INFO_LOOKUP_TOPIC_LABELS
    
    # def has_deparment(self) -> bool:
    #     value = self.ctx.slots.get("department_id")
    #     return value not in (None, "", [])
