# app/services/nlu_service.py (cloned and adapted)
from __future__ import annotations

import ast
import csv
import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from .textnorm import normalize_vi
from .nlu_constants import (
    CONFIRM_NO_PHRASES,
    CONFIRM_YES_PHRASES,
    DIRECTION_TRIGGERS,
    EMERGENCY_KEYWORDS,
    EMERGENCY_SELECTION_TOKENS,
    ISSUE_TICKET_TRIGGERS,
    LEADING_FILLERS,
    PLACE_HINTS,
    PROCEDURE_TRIGGERS,
    INFO_LOOKUP_TRIGGERS,
    RE_BEFORE_ODAU,
    RE_EN,
    RE_SIMPLE_TO,
    RE_TAIL_AFTER_VERB,
    SMALLTALK_TRIGGERS,
    STOP_TAIL,
    TRIAGE_SYMPTOM_RULES,
    TRIAGE_TRIGGERS,
)
from ..repositories.directory_repository import (
    DirectoryRepository,
    get_directory_repository,
)
from ..servicelogs.servicelogger import logger
from ..schemas.dto import Intent

if TYPE_CHECKING:
    from ..core.state_machine.context import ChatContext


@dataclass(frozen=True)
class NLUResult:
    intent: Intent
    confidence: float
    entities: List[str]
    raw_text: str
    language: str = "vi"
    model_version: Optional[str] = None


@dataclass(frozen=True)
class SlotExtractionResult:
    value: Optional[str]
    confidence: float
    intent: Optional[str] = None
    ambiguous_entities: Dict[str, List[str]] | None = None


@dataclass(frozen=True)
class DirectoryDestinationMatch:
    value: str
    place_type: str
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class SymptomExtractionResult:
    symptoms: Tuple[Dict[str, Any], ...] = ()


@dataclass(frozen=True)
class NLUConfig:
    direction_triggers: tuple[str, ...] = tuple(DIRECTION_TRIGGERS)
    place_hints: tuple[str, ...] = tuple(PLACE_HINTS)
    dir_threshold: float = 0.5
    procedure_triggers: tuple[str, ...] = tuple(PROCEDURE_TRIGGERS)
    proc_threshold: float = 0.5
    issue_triggers: tuple[str, ...] = tuple(ISSUE_TICKET_TRIGGERS)
    issue_threshold: float = 0.5
    triage_triggers: tuple[str, ...] = tuple(TRIAGE_TRIGGERS)
    triage_threshold: float = 0.5
    smalltalk_triggers: tuple[str, ...] = tuple(SMALLTALK_TRIGGERS)
    smalltalk_threshold: float = 0.5
    info_triggers: tuple[str, ...] = tuple(INFO_LOOKUP_TRIGGERS)
    info_threshold: float = 0.45


class NLUService:
    def __init__(
        self,
        config: NLUConfig | None = None,
        normalizer: Callable[[str], str] = normalize_vi,
        *,
        directory_repo: DirectoryRepository | None = None,
        hospital_id: Optional[str] = None,
    ) -> None:
        self.cfg = config or NLUConfig()
        self.normalize = normalizer
        self._directory_repo: DirectoryRepository = directory_repo or get_directory_repository()
        self._directory_default_hospital_id: Optional[str] = (
            hospital_id
            or os.getenv("DIRECTORY_DEFAULT_HOSPITAL_ID")
            or os.getenv("HOSPITAL_ID")
        )
        self._directory_hints_cache: Dict[str, List[Tuple[str, str]]] = {}
        self._service_package_hints_cache: Dict[str, List[Tuple[str, str]]] = {}
        self._place_hints_cache: Dict[Optional[str], Tuple[str, ...]] = {}
        self._department_aliases_cache: Dict[Optional[str], Dict[str, str]] = {}
        self._service_package_aliases_cache: Dict[Optional[str], Dict[str, str]] = {}
        self._lexicon_department_aliases: Optional[Dict[str, str]] = None
        self._directory_destination_aliases: Dict[
            Optional[str], Dict[str, DirectoryDestinationMatch]
        ] = {}

    def infer_intent(
        self,
        text: str,
        lang: str = "vi",
        *,
        chat_context: ChatContext | None = None,
        hospital_id: Optional[str] = None,
    ) -> NLUResult:
        logger.info(f"NLU input: lang={lang}, text={text}")

        if not text or not text.strip():
            return NLUResult(intent=Intent.UNKNOWN, confidence=0.0, entities=[], raw_text=text, language=lang)

        norm = self.normalize(text)
        logger.debug(f"NLU normalized: {norm}")

        resolved_hospital_id = self._resolve_hospital_id(chat_context=chat_context, hospital_id=hospital_id)
        place_hints = self._get_place_hints(resolved_hospital_id)

        dir_conf = self._score_direction_intent(norm, place_hints)
        proc_conf = self._score_procedure_intent(norm)
        issue_conf = self._score_issue_intent(norm)
        triage_conf = self._score_triage_intent(norm)
        small_conf = self._score_smalltalk_intent(norm)
        info_conf = self._score_info_intent(norm)
        scores = {
            Intent.DIRECTION: dir_conf,
            Intent.PROCEDURE: proc_conf,
            Intent.ISSUE_TICKET: issue_conf,
            Intent.TRIAGE: triage_conf,
            Intent.SMALLTALK: small_conf,
            Intent.FAQ: info_conf,
        }
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]

        if best_intent == Intent.DIRECTION and best_score >= self.cfg.dir_threshold:
            return self._handle_direction_intent(norm, lang, best_score, place_hints)
        if best_intent == Intent.PROCEDURE and best_score >= self.cfg.proc_threshold:
            return self._handle_procedure_intent(norm, lang, best_score)
        if best_intent == Intent.ISSUE_TICKET and best_score >= self.cfg.issue_threshold:
            return NLUResult(intent=Intent.ISSUE_TICKET, confidence=best_score, entities=[], raw_text=norm, language=lang)
        if best_intent == Intent.TRIAGE and best_score >= self.cfg.triage_threshold:
            # naive symptom capture: pick any keyword present
            symptom = self._extract_triage_symptom(norm)
            ents: List[str] = [symptom] if symptom else []
            return NLUResult(intent=Intent.TRIAGE, confidence=best_score, entities=ents, raw_text=norm, language=lang)
        if best_intent == Intent.SMALLTALK and best_score >= self.cfg.smalltalk_threshold:
            return NLUResult(intent=Intent.SMALLTALK, confidence=best_score, entities=[], raw_text=norm, language=lang)
        if best_intent == Intent.FAQ and best_score >= self.cfg.info_threshold:
            topic = self._classify_info_topic(norm)
            entities: List[str] = [topic] if topic else []
            return NLUResult(intent=Intent.FAQ, confidence=best_score, entities=entities, raw_text=norm, language=lang)

        return NLUResult(intent=Intent.UNKNOWN, confidence=best_score, entities=[], raw_text=norm, language=lang)

    def _score_direction_intent(self, norm: str, place_hints: Sequence[str]) -> float:
        score = 0.0
        if any(k in norm for k in self.cfg.direction_triggers):
            score += 0.55
        if any(k in norm for k in ["o dau", "nam o dau", "o cho nao", "cho nao", "di den", "di toi"]):
            score += 0.25
        if any(h in norm for h in place_hints):
            score += 0.15
        if len(norm.split()) >= 3:
            score += 0.05
        return min(score, 1.0)

    def _score_procedure_intent(self, norm: str) -> float:
        score = 0.0
        if any(k in norm for k in self.cfg.procedure_triggers):
            score += 0.55
        if any(k in norm for k in [
            "huong dan", "can gi", "can nhung gi", "can gi de", "dang ky", "dat lich", "lam sao",
            "how to", "how do i", "how to register"
        ]):
            score += 0.25
        if any(k in norm for k in [
            "giay to", "ho so", "le phi", "vien phi", "don", "phieu", "dang ky", "dat lich"
        ]):
            score += 0.15
        if len(norm.split()) >= 3:
            score += 0.05
        logger.debug(f"Procedure intent score: {score} for text: {norm}")
        return min(score, 1.0)

    def _score_issue_intent(self, norm: str) -> float:
        score = 0.0
        if any(k in norm for k in self.cfg.issue_triggers):
            score += 0.6
        if any(k in norm for k in ["dang ky kham", "xep hang", "lay so", "boc so", "so thu tu"]):
            score += 0.2
        if len(norm.split()) >= 2:
            score += 0.05
        return min(score, 1.0)

    def _score_triage_intent(self, norm: str) -> float:
        score = 0.0
        if any(k in norm for k in self.cfg.triage_triggers):
            score += 0.55
        # symptom-like words
        if any(k in norm for k in ["dau", "sot", "ho", "kho tho", "chong mat", "non", "tieu chay"]):
            score += 0.25
        if len(norm.split()) >= 2:
            score += 0.05
        return min(score, 1.0)

    def _score_smalltalk_intent(self, norm: str) -> float:
        score = 0.0
        if any(k in norm for k in self.cfg.smalltalk_triggers):
            score += 0.6
        return min(score, 1.0)

    def _score_info_intent(self, norm: str) -> float:
        score = 0.0
        if any(k in norm for k in self.cfg.info_triggers):
            score += 0.55
        if any(k in norm for k in ["bao nhieu", "%", "phan tram", "chi phi", "gia", "price", "fee"]):
            score += 0.2
        if any(k in norm for k in ["bhyt", "bao hiem", "bao hiem y te", "insurance", "coverage"]):
            score += 0.15
        if any(k in norm for k in ["quy trinh", "thu tuc", "workflow", "process", "cac buoc", "ho so"]):
            score += 0.25
        if len(norm.split()) >= 3:
            score += 0.05
        return min(score, 1.0)

    def _handle_direction_intent(
        self,
        norm: str,
        lang: str,
        confidence_score: float,
        place_hints: Sequence[str],
    ) -> NLUResult:
        poi_phrase: Optional[str] = None
        poi_conf: float = 0.0
        if lang.lower().startswith("vi"):
            poi_phrase = self._extract_poi_phrase_vi(norm)
        if poi_phrase:
            n_tok = len(poi_phrase.split())
            poi_conf = 0.6 if n_tok >= 1 else 0.0
            if n_tok >= 2:
                poi_conf = 0.72
            if any(h in poi_phrase for h in place_hints):
                poi_conf = max(poi_conf, 0.8)
        return NLUResult(
            intent=Intent.DIRECTION,
            confidence=confidence_score,
            entities=[poi_phrase] if poi_phrase else [],
            raw_text=norm,
            language="vi",
        )

    def extract_destination_slot(
        self,
        text: str,
        lang: str = "vi",
        *,
        chat_context: ChatContext | None = None,
        hospital_id: Optional[str] = None,
    ) -> SlotExtractionResult:
        if not text or not text.strip():
            return SlotExtractionResult(value=None, confidence=0.0)
        norm = self.normalize(text)
        resolved_hospital_id = self._resolve_hospital_id(chat_context=chat_context, hospital_id=hospital_id)
        if resolved_hospital_id:
            directory_match = self._match_directory_destination(norm, resolved_hospital_id)
            if directory_match and directory_match.value:
                logger.debug(f"Matched directory destination: {directory_match}")
                return directory_match
        place_hints = self._get_place_hints(resolved_hospital_id)
        poi_phrase: Optional[str] = None
        if lang.lower().startswith("vi"):
            poi_phrase = self._extract_poi_phrase_vi(norm)
        else:
            poi_phrase = self._extract_poi_phrase_en(norm)
        poi_conf = 0.0
        if poi_phrase:
            n_tok = len(poi_phrase.split())
            if n_tok >= 1:
                poi_conf = 0.6
            if n_tok >= 2:
                poi_conf = 0.72
            if any(h in poi_phrase for h in place_hints):
                poi_conf = max(poi_conf, 0.8)
        return SlotExtractionResult(value=poi_phrase, confidence=poi_conf)

    def _handle_procedure_intent(self, norm: str, lang: str, confidence_score: float) -> NLUResult:
        topic = self._extract_procedure_topic(norm)
        logger.debug(f"Extracted procedure topic: {topic}")
        entities: List[str] = [norm]
        if topic:
            entities.append(topic)
        return NLUResult(
            intent=Intent.PROCEDURE,
            confidence=confidence_score,
            entities=entities,
            raw_text=norm,
            language="vi",
        )

    def _classify_info_topic(self, norm: str) -> Optional[str]:
        workflow_keywords = [
            "quy trinh",
            "quy trinh kham",
            "quy trinh benh vien",
            "thu tuc",
            "ho so",
            "cac buoc",
            "quy dinh quy trinh",
            "process",
            "workflow",
        ]
        if any(k in norm for k in workflow_keywords):
            return "hospital_workflow"
        if any(k in norm for k in [
            "gia", "chi phi", "bao nhieu tien", "gia dich vu", "price", "fee", "bang gia", "bao nhieu mot lan",
            "bao nhieu tien mot lan", "bao nhieu tien 1 lan"
        ]):
            return "service_pricing"
        if any(k in norm for k in [
            "bhyt", "bao hiem", "bao hiem y te", "chi tra", "phan tram", "muc huong", "coverage",
            "thanh toan", "tra bao nhieu", "chi tra the nao", "duoc bao nhieu"
        ]):
            return "insurance_policy"
        return None

    def extract_slot(
        self,
        slot_name: str,
        text: str,
        lang: str = "vi",
        *,
        chat_context: ChatContext | None = None,
        hospital_id: Optional[str] = None,
    ) -> SlotExtractionResult:
        norm = self.normalize(text)
        resolved_hospital_id = self._resolve_hospital_id(chat_context=chat_context, hospital_id=hospital_id)
        handler = getattr(self, f"_extract_slot_{slot_name}", None)
        logger.info(f"Handling slot extraction for slot: {slot_name} with text: {norm}")
        if callable(handler):
            result: SlotExtractionResult = handler(
                norm,
                text,
                lang,
                hospital_id=resolved_hospital_id,
            )
            if result.value:
                return result
            if slot_name in {"department_id", "service_type"}:
                return SlotExtractionResult(value=None, confidence=0.0)
        fallback_value = text.strip() or None
        return SlotExtractionResult(value=fallback_value, confidence=0.4)

    def extract_symtom_info(
        self,
        text: str,
        lang: str = "vi",
        *,
        chat_context: ChatContext | None = None,
        hospital_id: Optional[str] = None,
    ) -> SymptomExtractionResult:
        """Extract top symptom candidates within the triage flow."""
        if not text or not text.strip():
            return SymptomExtractionResult()

        norm = self.normalize(text)
        resolved_hospital_id = self._resolve_hospital_id(chat_context=chat_context, hospital_id=hospital_id)
        logger.debug(
            "Extracting triage symptoms: norm=%s, lang=%s, hospital_id=%s",
            norm,
            lang,
            resolved_hospital_id,
        )

        candidates: List[Dict[str, Any]] = []

        for rule in TRIAGE_SYMPTOM_RULES:
            score, matches = self._score_symptom_rule(norm, rule)
            if score <= 0.0 or not matches:
                continue
            candidate = {
                "symptom_id": rule.get("symptom_id"),
                "symptom_name": rule.get("symptom_name"),
                "symptom": rule.get("symptom_name"),
                "confidence": round(score, 3),
                "matches": tuple(dict(match) for match in matches),
            }
            candidates.append(candidate)
            logger.debug(
                "Symptom candidate matched id=%s score=%.3f matches=%s",
                rule.get("symptom_id"),
                score,
                matches,
            )

        candidates.sort(key=lambda item: item["confidence"], reverse=True)
        filtered = [item for item in candidates if item["confidence"] >= 0.5][:3]

        if filtered:
            logger.info(
                "Extracted triage symptoms: %s",
                [(item["symptom"], item["confidence"]) for item in filtered],
            )
            return SymptomExtractionResult(symptoms=tuple(filtered))

        fallback_keyword = self._extract_triage_symptom(norm)
        if fallback_keyword:
            logger.info(
                "Fallback triage extraction keyword=%s",
                fallback_keyword,
            )
            fallback_candidate = {
                "symptom_id": "fallback",
                "symptom_name": text.strip() or fallback_keyword,
                "symptom": text.strip() or fallback_keyword,
                "confidence": 0.45,
                "matches": ({"hint": fallback_keyword},),
            }
            return SymptomExtractionResult(symptoms=(fallback_candidate,))
        return SymptomExtractionResult()

    def _score_symptom_rule(
        self,
        norm: str,
        rule: Dict[str, Any],
    ) -> Tuple[float, Tuple[Dict[str, Any], ...]]:
        matches: List[Dict[str, Any]] = []

        for hint in rule.get("hints", ()):
            normalized_hint = self.normalize(str(hint))
            if not normalized_hint or normalized_hint not in norm:
                continue
            logger.debug(
                "Matched symptom hint id=%s hint=%s",
                rule.get("symptom_id"),
                hint,
            )
            matches.append({"hint": str(hint)})

        if not matches:
            return 0.0, ()

        base = float(rule.get("base_confidence", 0.55))
        boost = 0.08 * (len(matches) - 1)
        score = min(1.0, base + max(0.0, boost))
        logger.debug(
            "Final symptom score id=%s base=%.2f matches=%d score=%.3f",
            rule.get("symptom_id"),
            base,
            len(matches),
            score,
        )
        return score, tuple(matches)

    def _clean_phrase(self, p: str) -> str:
        p = re.sub(r"[?!.,:;]+$", "", p.strip())
        toks = [t for t in p.split() if t]
        while toks and toks[0] in LEADING_FILLERS:
            toks.pop(0)
        tail = " ".join(toks)
        for s in STOP_TAIL:
            if tail.endswith(" " + s):
                tail = tail[: -(len(s) + 1)]
        return tail.strip()

    def _extract_poi_phrase_vi(self, norm: str) -> Optional[str]:
        logger.debug(f"Extracting POI phrase from VI text: {norm}")
        m = RE_TAIL_AFTER_VERB.search(norm)
        if m:
            cand = self._clean_phrase(m.group(1))
            if cand:
                logger.debug(f"Matched RE_TAIL_AFTER_VERB: {cand}")
                return cand
        m = RE_BEFORE_ODAU.match(norm)
        if m:
            cand = self._clean_phrase(m.group(1))
            if cand:
                logger.debug(f"Matched RE_BEFORE_ODAU: {cand}")
                return cand
        m = RE_SIMPLE_TO.search(norm)
        if m:
            cand = self._clean_phrase(m.group(1))
            if cand:
                logger.debug(f"Candidate: {cand}")
                return cand
        logger.debug("No POI phrase matched")
        return None

    def _extract_poi_phrase_en(self, norm: str) -> Optional[str]:
        m = RE_EN.search(norm)
        if m:
            cand = self._clean_phrase(m.group(1))
            if cand:
                return cand
        return None

    def _extract_procedure_topic(self, norm: str) -> Optional[str]:
        logger.info(f"Extracting procedure topic from text: {norm}")
        # Minimal placeholder: try common tokens to return a coarse topic.
        for key in [
            "dang ky", "dat lich", "bhyt", "bao hiem", "giay to", "ho so", "thanh toan", "vien phi",
        ]:
            if key in norm:
                return key
        return None

    def _extract_triage_symptom(self, norm: str) -> Optional[str]:
        for key in ["dau", "nhuc", "sot", "ho", "kho tho", "chong mat", "non", "tieu chay"]:
            if key in norm:
                return key
        return None

    def _extract_slot_department_id(
        self,
        norm: str,
        original_text: str,
        lang: str,
        *,
        hospital_id: Optional[str] = None,
    ) -> SlotExtractionResult:
        logger.info(f"Extracting department_id slot from text: {norm} for hospital_id={hospital_id}")
        aliases = self._get_department_aliases(hospital_id)
        for phrase, dept_id in aliases.items():
            if phrase in norm:
                return SlotExtractionResult(value=dept_id, confidence=0.85)
        direct_match = aliases.get(norm)
        if direct_match:
            return SlotExtractionResult(value=direct_match, confidence=0.9)
        return SlotExtractionResult(value=None, confidence=0.0)

    def _extract_slot_service_type(
        self,
        norm: str,
        original_text: str,
        lang: str,
        *,
        hospital_id: Optional[str] = None,
    ) -> SlotExtractionResult:
        logger.info(f"Extracting service_type slot from text: {norm} for hospital_id={hospital_id}")
        aliases = self._get_service_type_aliases(hospital_id)
        matches: Dict[str, List[Tuple[int, int, bool]]] = {}
        for phrase, service_code in aliases.items():
            if not phrase:
                continue
            is_exact = norm == phrase
            if is_exact or phrase in norm:
                tokens = len([token for token in phrase.split() if token])
                if tokens == 0:
                    continue
                matches.setdefault(service_code, []).append((tokens, len(phrase), is_exact))
        if matches:
            best_key: Optional[Tuple[int, int, int, int]] = None
            best_service: Optional[str] = None
            best_confidence: float = 0.0
            for service_code, entries in matches.items():
                total_tokens = sum(item[0] for item in entries)
                has_exact = any(item[2] for item in entries)
                strongest_entry = max(entries, key=lambda item: (item[2], item[0], item[1]))
                candidate_key = (
                    1 if has_exact else 0,
                    total_tokens,
                    strongest_entry[0],
                    strongest_entry[1],
                )
                if best_key is None or candidate_key > best_key:
                    best_key = candidate_key
                    base_confidence = 0.7 + 0.05 * total_tokens
                    if has_exact:
                        best_confidence = min(0.95, max(0.9, base_confidence))
                    else:
                        best_confidence = min(0.9, base_confidence)
                    best_service = service_code
            if best_service:
                return SlotExtractionResult(value=best_service, confidence=round(best_confidence, 2))
        return SlotExtractionResult(value=None, confidence=0.0)

    def classify_confirmation(self, text: str, lang: str = "vi") -> Optional[str]:
        if not text or not text.strip():
            return None
        norm = self.normalize(text)
        lowered = norm.strip().lower()
        if not lowered:
            return None
        padded = f" {lowered} "
        for phrase in CONFIRM_NO_PHRASES:
            token = phrase.strip().lower()
            if token and (padded == f" {token} " or f" {token} " in padded):
                return "no"
        for phrase in CONFIRM_YES_PHRASES:
            token = phrase.strip().lower()
            if token and (padded == f" {token} " or f" {token} " in padded):
                return "yes"
        return None
    
    def is_emergency(self, text: str, lang: str = "vi") -> Optional[str]:
        if not text or not text.strip():
            return None
        norm = self.normalize(text)
        if not norm:
            return None
        lowered = norm.lower()
        tokens = set(lowered.split())
        # if any(token in EMERGENCY_SELECTION_TOKENS for token in tokens):
        #     return "yes"
        if any(keyword in lowered for keyword in EMERGENCY_KEYWORDS):
            return "yes"
        return None

    def _resolve_hospital_id(
        self,
        *,
        chat_context: ChatContext | None = None,
        hospital_id: Optional[str] = None,
    ) -> Optional[str]:
        if hospital_id not in (None, "", []):
            return str(hospital_id)
        ctx_tenant: Optional[str] = None
        if chat_context is not None:
            ctx_tenant = getattr(chat_context, "tenant_id", None)
        if ctx_tenant not in (None, "", []):
            return str(ctx_tenant)
        if self._directory_default_hospital_id not in (None, "", []):
            return str(self._directory_default_hospital_id)
        return None

    def _fetch_directory_hints(self, hospital_id: str) -> List[Tuple[str, str]]:
        if hospital_id in self._directory_hints_cache:
            return self._directory_hints_cache[hospital_id]
        try:
            hints = self._directory_repo.get_departments_hint(hospital_id)
        except Exception:
            logger.exception(
                "NLU: failed to fetch department hints for hospital_id=%s",
                hospital_id,
            )
            hints = []
        self._directory_hints_cache[hospital_id] = hints
        return hints

    def _get_place_hints(self, hospital_id: Optional[str]) -> Tuple[str, ...]:
        cache_key = hospital_id
        if cache_key in self._place_hints_cache:
            return self._place_hints_cache[cache_key]
        hints: set[str] = set(self.cfg.place_hints)
        if hospital_id:
            for normalized_hint, _dept_id in self._fetch_directory_hints(hospital_id):
                if normalized_hint:
                    hints.add(normalized_hint)
        cached = tuple(sorted(hints))
        self._place_hints_cache[cache_key] = cached
        return cached

    def _fetch_service_package_hints(self, hospital_id: str) -> List[Tuple[str, str]]:
        if hospital_id in self._service_package_hints_cache:
            return self._service_package_hints_cache[hospital_id]
        try:
            hints = self._directory_repo.get_service_packages_hint(hospital_id)
        except Exception:
            logger.exception(
                "NLU: failed to fetch service package hints for hospital_id=%s",
                hospital_id,
            )
            hints = []
        self._service_package_hints_cache[hospital_id] = hints
        # logger.debug(f"Fetched service package hints for hospital_id={hospital_id}: {hints}")
        return hints

    def _get_service_type_aliases(self, hospital_id: Optional[str]) -> Dict[str, str]:
        cache_key = hospital_id
        cached = self._service_package_aliases_cache.get(cache_key)
        if cached is not None:
            return cached
        mapping: Dict[str, str] = dict()
        if not hospital_id:
            mapping = self._default_service_type_aliases()
        if hospital_id:
            for normalized_hint, pkg_id in self._fetch_service_package_hints(hospital_id):
                if normalized_hint and pkg_id:
                    mapping.setdefault(normalized_hint, pkg_id)
        self._service_package_aliases_cache[cache_key] = mapping
        logger.debug(f"Loaded service type aliases for hospital_id={hospital_id}: {mapping}")
        return mapping

    def _load_department_lexicon_aliases(self) -> Dict[str, str]:
        if self._lexicon_department_aliases is not None:
            return self._lexicon_department_aliases
        mapping: Dict[str, str] = {}
        lexicon_path = (
            Path(__file__)
            .resolve()
            .parents[2]
            / "core-service"
            / "app"
            / "knowledgebases"
            / "lexicons.csv"
        )
        if not lexicon_path.exists():
            self._lexicon_department_aliases = mapping
            return mapping
        try:
            with lexicon_path.open(encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    if (row.get("type") or "").strip().lower() != "department":
                        continue
                    term = (row.get("term") or "").strip()
                    canonical = (row.get("canonical") or "").strip()
                    target_ids: List[str] = []
                    raw_ids = row.get("related_poi_ids") or "[]"
                    try:
                        parsed_ids = ast.literal_eval(raw_ids)
                        if isinstance(parsed_ids, (list, tuple)):
                            target_ids = [str(item) for item in parsed_ids if item]
                    except (SyntaxError, ValueError):
                        target_ids = []
                    target = target_ids[0] if target_ids else canonical
                    normalized_entries: set[str] = set()
                    for entry in [term, canonical]:
                        if entry:
                            normalized_entries.add(entry)
                    examples_raw = row.get("examples") or "[]"
                    try:
                        examples = ast.literal_eval(examples_raw)
                        if isinstance(examples, (list, tuple)):
                            normalized_entries.update(str(item) for item in examples if item)
                    except (SyntaxError, ValueError):
                        pass
                    for entry in normalized_entries:
                        normalized_entry = self.normalize(entry)
                        if normalized_entry:
                            mapping[normalized_entry] = target
        except OSError:
            mapping = {}
        self._lexicon_department_aliases = mapping
        logger.debug(f"Loaded department lexicon aliases: {mapping}")
        return mapping

    def _get_department_aliases(self, hospital_id: Optional[str]) -> Dict[str, str]:
        cache_key = hospital_id
        cached = self._department_aliases_cache.get(cache_key)
        if cached is not None:
            return cached
        mapping: Dict[str, str] = dict()
        if not hospital_id:
            mapping.update(self._load_department_lexicon_aliases())
        if hospital_id:
            for normalized_hint, dept_id in self._fetch_directory_hints(hospital_id):
                if normalized_hint and dept_id:
                    mapping.setdefault(normalized_hint, dept_id)
        self._department_aliases_cache[cache_key] = mapping
        logger.debug(f"Loaded department aliases for hospital_id={hospital_id}: {mapping}")
        return mapping

    def _expand_directory_hint_entries(self, raw_hint: Any) -> Tuple[str, ...]:
        entries: List[str] = []
        if isinstance(raw_hint, str):
            cleaned = raw_hint.replace("\n", " // ")
            entries.extend(piece.strip() for piece in cleaned.split("//"))
        elif isinstance(raw_hint, (list, tuple, set)):
            for item in raw_hint:
                if isinstance(item, str):
                    cleaned = item.replace("\n", " // ")
                    entries.extend(piece.strip() for piece in cleaned.split("//"))
        normalized: List[str] = []
        seen: set[str] = set()
        for entry in entries:
            normalized_entry = self.normalize(entry)
            if normalized_entry and normalized_entry not in seen:
                seen.add(normalized_entry)
                normalized.append(normalized_entry)
        return tuple(normalized)

    def _build_room_aliases(self, room_number: str) -> Tuple[str, ...]:
        if not room_number:
            return tuple()
        templates = [
            room_number,
            f"phong {room_number}",
            f"phong kham {room_number}",
            f"p {room_number}",
            f"p. {room_number}",
        ]
        normalized_aliases: List[str] = []
        seen: set[str] = set()
        for template in templates:
            normalized = self.normalize(template)
            if not normalized:
                continue
            if template is room_number and normalized.isdigit():
                continue
            if normalized not in seen:
                seen.add(normalized)
                normalized_aliases.append(normalized)
        return tuple(normalized_aliases)

    def _build_room_alias_entries(
        self,
        room: Dict[str, Any],
        *,
        department_name: str,
        department_id: Optional[str],
    ) -> Dict[str, DirectoryDestinationMatch]:
        mapping: Dict[str, DirectoryDestinationMatch] = {}
        room_number = (room.get("room_number") or "").strip()
        if not room_number:
            return mapping
        aliases = self._build_room_aliases(room_number)
        if not aliases:
            return mapping
        room_id_raw = room.get("room_id")
        metadata = {
            "room_id": str(room_id_raw) if room_id_raw not in (None, "", []) else None,
            "department_id": department_id,
            "department_name": department_name,
        }
        metadata = {k: v for k, v in metadata.items() if v not in (None, "", [])}
        room_label = room_number
        normalized_label = self.normalize(room_label)
        if not normalized_label.startswith("phong"):
            room_label = f"Phòng {room_number}"
        for alias in aliases:
            mapping.setdefault(
                alias,
                DirectoryDestinationMatch(
                    value=room_label,
                    place_type="room",
                    metadata=metadata,
                ),
            )
        location_desc = (room.get("location_description") or "").strip()
        if location_desc:
            normalized_location = self.normalize(location_desc)
            if normalized_location:
                mapping.setdefault(
                    normalized_location,
                    DirectoryDestinationMatch(
                        value=room_label,
                        place_type="room",
                        metadata=metadata,
                    ),
                )
        return mapping

    def _get_directory_destination_aliases(
        self,
        hospital_id: Optional[str],
    ) -> Dict[str, DirectoryDestinationMatch]:
        cache_key = hospital_id
        cached = self._directory_destination_aliases.get(cache_key)
        if cached is not None:
            return cached
        aliases: Dict[str, DirectoryDestinationMatch] = {}
        if not hospital_id:
            self._directory_destination_aliases[cache_key] = aliases
            return aliases
        try:
            departments = self._directory_repo.get_departments_full(hospital_id)
        except Exception:
            logger.exception(
                "NLU: failed to fetch directory departments for hospital_id=%s",
                hospital_id,
            )
            departments = []
        for dept in departments:
            dept_name = (dept.get("name") or "").strip()
            if not dept_name:
                continue
            dept_id_raw = dept.get("department_id")
            dept_id = str(dept_id_raw) if dept_id_raw not in (None, "", []) else None
            metadata = {"department_id": dept_id}
            metadata = {k: v for k, v in metadata.items() if v not in (None, "", [])}
            normalized_dept = self.normalize(dept_name)
            if normalized_dept:
                aliases.setdefault(
                    normalized_dept,
                    DirectoryDestinationMatch(
                        value=dept_name,
                        place_type="department",
                        metadata=metadata,
                    ),
                )
            for hint in self._expand_directory_hint_entries(dept.get("hint")):
                aliases.setdefault(
                    hint,
                    DirectoryDestinationMatch(
                        value=dept_name,
                        place_type="department",
                        metadata=metadata,
                    ),
                )
            for room in dept.get("examination_rooms") or []:
                room_aliases = self._build_room_alias_entries(
                    room,
                    department_name=dept_name,
                    department_id=dept_id,
                )
                for alias, entry in room_aliases.items():
                    aliases.setdefault(alias, entry)
        seen_zones: set[str] = set()
        for dept in departments:
            dept_name = (dept.get("name") or "").strip()
            if not dept_name:
                continue
            try:
                zones = self._directory_repo.search_zones_by_department_name(
                    hospital_id,
                    dept_name,
                )
            except Exception:
                logger.exception(
                    "NLU: failed to fetch directory zones for hospital_id=%s department=%s",
                    hospital_id,
                    dept_name,
                )
                zones = []
            for zone in zones:
                zone_name = (zone.get("name") or "").strip()
                if not zone_name:
                    continue
                normalized_zone = self.normalize(zone_name)
                if not normalized_zone or normalized_zone in aliases or normalized_zone in seen_zones:
                    continue
                zone_id_raw = zone.get("zone_id")
                zone_id = (
                    str(zone_id_raw)
                    if zone_id_raw not in (None, "", [])
                    else None
                )
                metadata = {
                    "zone_id": zone_id,
                    "department_name": dept_name,
                }
                metadata = {k: v for k, v in metadata.items() if v not in (None, "", [])}
                aliases[normalized_zone] = DirectoryDestinationMatch(
                    value=zone_name,
                    place_type="zone",
                    metadata=metadata,
                )
                seen_zones.add(normalized_zone)
        self._directory_destination_aliases[cache_key] = aliases
        return aliases

    def _match_directory_destination(
        self,
        norm_text: str,
        hospital_id: str,
    ) -> Optional[SlotExtractionResult]:
        if not norm_text:
            return None
        aliases = self._get_directory_destination_aliases(hospital_id)
        if not aliases:
            return None
        best_alias: Optional[str] = None
        best_entry: Optional[DirectoryDestinationMatch] = None
        best_score: Tuple[int, int] = (-1, -1)
        for alias, entry in aliases.items():
            if not alias:
                continue
            pattern = rf"(?<![A-Za-z0-9]){re.escape(alias)}(?![A-Za-z0-9])"
            if not re.search(pattern, norm_text):
                continue
            priority = self._destination_priority(entry.place_type)
            score = (priority, len(alias))
            if score > best_score:
                best_score = score
                best_alias = alias
                best_entry = entry
        if not best_entry or not best_alias:
            return None
        confidence = self._destination_confidence(best_entry.place_type, len(best_alias))
        return SlotExtractionResult(value=best_entry.value, confidence=confidence)

    @staticmethod
    def _destination_priority(place_type: str) -> int:
        priorities = {"room": 3, "department": 2, "zone": 1}
        return priorities.get(place_type, 0)

    @staticmethod
    def _destination_confidence(place_type: str, alias_len: int) -> float:
        base = 0.82
        if place_type == "room":
            base = 0.9
        elif place_type == "zone":
            base = 0.88
        elif place_type == "department":
            base = 0.86
        bonus = min(max(alias_len - 4, 0) * 0.01, 0.07)
        return round(min(base + bonus, 0.97), 2)

    def _default_department_aliases(self) -> Dict[str, str]:
        defaults = [
            ("khoa tong quat", "1"),
            ("tong quat", "1"),
            ("kham tong quat", "1"),
            ("khoa tim mach", "2"),
            ("tim mach", "2"),
            ("kham tim", "2"),
            ("khoa ho hap", "3"),
            ("ho hap", "3"),
            ("kham ho hap", "3"),
            ("khoa than kinh", "4"),
            ("than kinh", "4"),
            ("kham than kinh", "4"),
            ("khoa chan thuong chinh hinh", "5"),
            ("chan thuong chinh hinh", "5"),
            ("kham chan thuong chinh hinh", "5"),
            ("khoa tai mui hong", "6"),
            ("tai mui hong", "6"),
            ("kham tai mui hong", "6"),
            ("khoa mat", "7"),
            ("mat", "7"),
            ("kham mat", "7"),
            ("khoa nhi", "8"),
            ("nhi", "8"),
            ("kham nhi", "8"),
        ]
        normalized: Dict[str, str] = {}
        for phrase, dept_id in defaults:
            norm_phrase = self.normalize(phrase)
            if norm_phrase:
                normalized[norm_phrase] = dept_id
        return normalized

    def _default_service_type_aliases(self) -> Dict[str, str]:
        defaults = [
            ("kham co bhyt", "1"),
            ("kham co bao hiem y te", "1"),
            ("kham bao hiem y te", "1"),
            ("bao hiem y te", "1"),
            ("kham co bao hiem y te", "1"),
            ("kham bhyt", "1"),
            ("kham thuong", "2"),
            ("kham khong co bhyt", "2"),
            ("khong co bhyt", "2"),
            ("kham thuong quy", "2"),
            ("kham dich vu", "3"),
            ("kham dv", "3"),
            ("kham vip", "4"),
            ("goi vip", "4"),
        ]
        normalized: Dict[str, str] = {}
        for phrase, service_code in defaults:
            norm_phrase = self.normalize(phrase)
            if norm_phrase:
                normalized[norm_phrase] = service_code
        return normalized

@lru_cache(maxsize=1)
def get_nlu_service() -> NLUService:
    """P2.1 - lru_cache replaces global singleton.

    Preserves directory hint cache (Codex #7) - NLUService holds caches
    internally; one instance per process keeps them warm.
    """
    return NLUService()
