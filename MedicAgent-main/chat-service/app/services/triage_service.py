from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..repositories.directory_repository import (
    DirectoryRepository,
    get_directory_repository,
)
from ..servicelogs.servicelogger import logger
from .syndrome_classifier import get_syndrome_classifier
from .triage_config import (
    DEFAULT_SYNDROME_TRIAGE_UNITS,
    DEFAULT_TRIAGE_UNITS,
    TRIAGE_SYNDROME_RULES,
    MAX_SYNDROME_SUGGESTIONS,
    MAX_UNIT_SUGGESTIONS,
)


@dataclass(frozen=True)
class SyndromeCandidate:
    syndrome_id: str
    name: str
    score: float
    matches: Tuple[Dict[str, Any], ...] # Details of symptom matches contributing to this syndrome


@dataclass(frozen=True)
class TriageSuggestionResult:
    syndromes: Tuple[SyndromeCandidate, ...] = ()
    triage_units: Tuple[Dict[str, Any], ...] = ()


class TriageService:
    def __init__(self, *, directory_repo: Optional[DirectoryRepository] = None) -> None:
        self._directory_repo = directory_repo or get_directory_repository()
        self._syndrome_map_cache: Dict[str, Dict[str, Tuple[Dict[str, Any], ...]]] = {}
        self._fallback_cache: Dict[str, Tuple[Dict[str, Any], ...]] = {}
        self._syndrome_catalog = self._build_syndrome_catalog()

    # def llm_suggest_units(
    #     self,
    #     symptoms: Sequence[Dict[str, Any]],
    #     *,
    #     hospital_id: Optional[str] = None,
    #     top_n: int = 1,
    # ) -> TriageSuggestionResult:
    #     if not symptoms:
    #         return TriageSuggestionResult()

    #     symptom_texts: List[str] = []
    #     for item in symptoms:
    #         if not isinstance(item, dict):
    #             continue
    #         label = item.get("symptom_name") or item.get("symptom") or item.get("text")
    #         if label:
    #             conf = self._safe_float(item.get("confidence"))
    #             symptom_texts.append(f"{label} ({conf:.2f})" if conf > 0 else str(label))
    #     if not symptom_texts:
    #         return TriageSuggestionResult()

    #     syndrome_catalog = {
    #         rule.get("syndrome_id"): rule.get("name")
    #         for rule in TRIAGE_SYNDROME_RULES
    #         if rule.get("syndrome_id")
    #     }
    #     catalog_lines = "\n".join(
    #         f"- {syndrome_id}: {name}" for syndrome_id, name in syndrome_catalog.items() if name
    #     )
    #     prompt = (
    #         "Chọn 1 syndrome_id phù hợp nhất từ danh sách dưới đây, dựa trên triệu chứng"
    #         "Trả về json: {\"syndrome_id\":\"...\",\"confidence\":0-1}. "
    #         "Nếu không chắc, syndrome_id = \"unknown\".\n"
    #         f"Triệu chứng: {', '.join(symptom_texts)}\n"
    #         f"Danh sách hội chứng:\n{catalog_lines}\n"
    #     )

    #     base_url = os.getenv("LLM_API_BASE") or "http://medicagent-llm:8000/v1"
    #     model = os.getenv("LLM_MODEL") or os.getenv("VLLM_MODEL") or os.getenv("SERVED_MODEL_NAME")
    #     if not model:
    #         model_id = os.getenv("MODEL_ID") or "Menlo/Jan-nano-128k"
    #         model = model_id.rsplit("/", 1)[-1]
    #     payload = {
    #         "model": model,
    #         "messages": [
    #             {"role": "system", "content": "Bạn là trợ lý tiếp nhận thông tin y tế để xử lý tại bệnh viện."},
    #             {"role": "user", "content": prompt},
    #         ],
    #         "temperature": 0.1,
    #         "max_tokens": 128,
    #         "response_format": {"type": "json_object"},
    #     }
    #     logger.debug("Sending LLM triage suggestion request to %s with payload: %s", base_url, payload)
    #     try:
    #         response = requests.post(
    #             f"{base_url.rstrip('/')}/chat/completions",
    #             json=payload,
    #             timeout=6,
    #         )
    #         response.raise_for_status()
    #         data = response.json()
    #     except Exception as exc:  # noqa: BLE001
    #         logger.exception("LLM triage suggestion failed", exc_info=exc)
    #         return TriageSuggestionResult()

    #     content = ""
    #     if isinstance(data, dict):
    #         choices = data.get("choices") or []
    #         if choices and isinstance(choices, list):
    #             message = choices[0].get("message") or {}
    #             content = message.get("content") or ""
    #     if not content:
    #         return TriageSuggestionResult()

    #     parsed: Dict[str, Any] = {}
    #     try:
    #         parsed = json.loads(content)
    #     except json.JSONDecodeError:
    #         match = re.search(r"\{.*\}", content, re.DOTALL)
    #         if match:
    #             try:
    #                 parsed = json.loads(match.group(0))
    #             except json.JSONDecodeError:
    #                 parsed = {}

    #     syndrome_id = str(parsed.get("syndrome_id") or "").strip()
    #     if not syndrome_id or syndrome_id == "unknown" or syndrome_id not in syndrome_catalog:
    #         return TriageSuggestionResult()

    #     score = self._safe_float(parsed.get("confidence"))
    #     score = min(1.0, max(0.0, score if score > 0 else 0.55))
    #     candidate = SyndromeCandidate(
    #         syndrome_id=syndrome_id,
    #         name=syndrome_catalog.get(syndrome_id) or syndrome_id,
    #         score=score,
    #         matches=(),
    #     )
    #     triage_units = self._map_syndromes_to_units((candidate,), hospital_id)
    #     result = TriageSuggestionResult(
    #         syndromes=(candidate,),
    #         triage_units=triage_units[: max(1, top_n)],
    #     )
    #     logger.debug("LLM triage suggestion result: %s", result)
    #     return result
    
    def suggest_units(
        self,
        symptoms: Sequence[Dict[str, Any]],
        *,
        hospital_id: Optional[str] = None,
        top_n: int = 3,
        text: Optional[str] = None,
    ) -> TriageSuggestionResult:
        if not symptoms and not (text and text.strip()):
            return TriageSuggestionResult()

        scored: List[Dict[str, Any]] = []
        classifier = get_syndrome_classifier()
        if classifier and text and text.strip():
            logger.debug("Scoring triage syndromes using trained classifier")
            scored = self._score_syndromes_from_model(text, top_n=top_n)
            logger.debug("Scored syndromes from model: %s", scored)

        if not scored and symptoms:
            logger.debug("Scoring triage syndromes for symptoms=%s", symptoms)
            scored = self._score_syndromes(symptoms)
        if not scored:
            logger.info("No triage syndrome matched for provided input")
            return TriageSuggestionResult()

        top_candidates = tuple(
            SyndromeCandidate(
                syndrome_id=item["syndrome_id"],
                name=item["name"],
                score=item["score"],
                matches=item["matches"],
            )
            for item in scored[: max(1, top_n)]
        )
        logger.info(
            "Top syndrome predictions: %s",
            [(candidate.name, candidate.score) for candidate in top_candidates],
        )

        triage_units = self._map_syndromes_to_units(top_candidates, hospital_id)
        logger.debug("Mapped triage units: %s", triage_units)
        if triage_units:
            logger.info(
                "Resolved triage units: %s",
                [
                    (
                        unit.get("name"),
                        unit.get("triage_unit_id"),
                        unit.get("syndrome_score"),
                    )
                    for unit in triage_units
                ],
            )
        return TriageSuggestionResult(
            syndromes=top_candidates,
            triage_units=triage_units,
        )

    def _score_syndromes_from_model(self, text: str, top_n: int) -> List[Dict[str, Any]]:
        classifier = get_syndrome_classifier()
        if not classifier:
            return []
        top_k = max(1, min(top_n, MAX_SYNDROME_SUGGESTIONS))
        predictions = classifier.predict_top(text, top_k=top_k)
        if not predictions:
            return []
        results: List[Dict[str, Any]] = []
        for pred in predictions:
            syndrome_id = pred.label
            results.append(
                {
                    "syndrome_id": syndrome_id,
                    "name": self._syndrome_catalog.get(syndrome_id) or syndrome_id,
                    "score": round(pred.score, 4),
                    "matches": (),
                }
            )
        return results

    def _score_syndromes(self, symptoms: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
        lookup = self._index_symptoms(symptoms)
        results: List[Dict[str, Any]] = []

        for rule in TRIAGE_SYNDROME_RULES:
            score = float(rule.get("base_score", 0.0))
            matches: List[Dict[str, Any]] = []
            for mapping in rule.get("symptoms", ()):  # type: ignore[arg-type]
                symptom_id = mapping.get("symptom_id")
                if not symptom_id:
                    continue
                symptom = lookup.get(symptom_id)
                if not symptom:
                    continue
                weight = self._safe_float(mapping.get("weight", 0.0))
                confidence = self._safe_float(symptom.get("confidence"))
                if confidence <= 0.0 or weight <= 0.0:
                    continue
                contribution = confidence * weight
                score += contribution
                matches.append(
                    {
                        "symptom_id": symptom_id,
                        "symptom_name": symptom.get("symptom_name") or symptom.get("symptom"),
                        "confidence": round(confidence, 3),
                        "weight": round(weight, 3),
                        "score": round(contribution, 3),
                        "matches": self._clone_matches(symptom.get("matches")),
                    }
                )
            if not matches:
                continue
            final_score = min(1.0, round(score, 4))
            threshold = self._safe_float(rule.get("threshold", 0.5))
            if final_score < threshold:
                logger.debug(
                    "Syndrome %s scored %.3f below threshold %.3f",
                    rule.get("syndrome_id"),
                    final_score,
                    threshold,
                )
                continue
            results.append(
                {
                    "syndrome_id": rule["syndrome_id"],
                    "name": rule["name"],
                    "score": final_score,
                    "matches": tuple(matches),
                }
            )

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[0:MAX_SYNDROME_SUGGESTIONS]

    @staticmethod
    def _build_syndrome_catalog() -> Dict[str, str]:
        catalog: Dict[str, str] = {}
        for rule in TRIAGE_SYNDROME_RULES:
            syndrome_id = rule.get("syndrome_id")
            if syndrome_id:
                catalog[str(syndrome_id)] = rule.get("name") or str(syndrome_id)
        return catalog

    def _map_syndromes_to_units(
        self,
        syndromes: Sequence[SyndromeCandidate],
        hospital_id: Optional[str],
    ) -> Tuple[Dict[str, Any], ...]:
        """Maps the given syndromes to triage units based on hospital-specific or default mappings.
        vi: Ánh xạ các hội chứng đã cho sang các đơn vị phân loại dựa trên ánh xạ cụ thể của bệnh viện hoặc mặc định."""
        if not syndromes:
            return ()

        mapping = self._get_hospital_mapping(hospital_id)
        logger.debug(
            "Using syndrome-to-triage-unit mapping for hospital %s: %s",
            hospital_id,
            mapping,
        )
        resolved: List[Dict[str, Any]] = []

        for candidate in syndromes:
            units = list(mapping.get(candidate.syndrome_id) or self._build_default_units(candidate.syndrome_id))
            for idx, unit in enumerate(units, start=1):
                priority = unit.get("priority") or idx
                payload: Dict[str, Any] = {
                    "syndrome_id": candidate.syndrome_id,
                    "syndrome_name": candidate.name,
                    "syndrome_score": candidate.score,
                    "triage_unit_id": unit.get("triage_unit_id"),
                    "department_id": unit.get("department_id") or unit.get("triage_unit_id"),
                    "name": unit.get("name"),
                    "priority": priority,
                }
                multiplier = unit.get("score_multiplier")
                if multiplier is not None:
                    try:
                        payload["weighted_score"] = round(candidate.score * float(multiplier), 3)
                    except (TypeError, ValueError):
                        payload["weighted_score"] = candidate.score
                resolved.append(payload)

        deduplicated = self._deduplicate_units(resolved)
        return tuple(deduplicated[0:MAX_UNIT_SUGGESTIONS])
        # return tuple(resolved)
        

    def _get_hospital_mapping(
        self,
        hospital_id: Optional[str],
    ) -> Dict[str, Tuple[Dict[str, Any], ...]]:
        """Fetches and caches the syndrome-to-triage-unit mapping for a given hospital.
        vi: Lấy và lưu vào bộ nhớ đệm ánh xạ từ hội chứng sang đơn vị phân loại cho một bệnh viện cụ thể."""
        if hospital_id in (None, "", []):
            return {}
        cache_key = str(hospital_id)
        if cache_key not in self._syndrome_map_cache:
            logger.debug("Cache not existed, Caching syndrome mappings for hospital %s", cache_key)
            raw = self._directory_repo.get_syndrome_triage_mappings(cache_key)
            normalized = self._normalize_directory_mappings(raw)
            self._syndrome_map_cache[cache_key] = normalized
            logger.debug(
                "Loaded %s syndrome mappings for hospital %s",
                len(normalized),
                cache_key,
            )

        hospital_mapping = self._syndrome_map_cache.get(cache_key, {})
        logger.debug(f"Using cached syndrome mappings for hospital {cache_key}: {hospital_mapping}")
        return hospital_mapping

    def _normalize_directory_mappings(
        self,
        payload: Any,
    ) -> Dict[str, Tuple[Dict[str, Any], ...]]:
        """
        Normalizes the raw mapping payload from the directory into a structured format.
        vi: Chuẩn hóa payload ánh xạ thô từ thư mục thành định dạng có"""
        mapping: Dict[str, Tuple[Dict[str, Any], ...]] = {}
        if not isinstance(payload, (list, tuple)):
            return mapping

        for item in payload:
            if not isinstance(item, dict):
                continue
            syndrome_id = item.get("syndrome_id") or item.get("id")
            if not syndrome_id:
                continue
            units_source = item.get("triage_units")
            unit_dicts: List[Dict[str, Any]] = []
            if isinstance(units_source, dict):
                unit_dicts = [units_source]
            elif isinstance(units_source, (list, tuple)):
                unit_dicts = [unit for unit in units_source if isinstance(unit, dict)]
            else:
                candidate = {
                    key: item.get(key)
                    for key in ("triage_unit_id", "department_id", "name", "priority", "score_multiplier")
                }
                if any(candidate.values()):
                    unit_dicts = [candidate]

            normalized_units: List[Dict[str, Any]] = []
            for unit in unit_dicts:
                trig_unit_id = unit.get("triage_unit_id") or unit.get("department_id")
                if not trig_unit_id:
                    continue
                normalized_units.append(
                    {
                        "triage_unit_id": str(trig_unit_id),
                        "department_id": unit.get("department_id") or unit.get("triage_unit_id"),
                        "name": unit.get("name"),
                        "priority": unit.get("priority"),
                        "score_multiplier": unit.get("score_multiplier"),
                    }
                )
            if normalized_units:
                mapping[str(syndrome_id)] = tuple(normalized_units)
        return mapping

    def _build_default_units(self, syndrome_id: str) -> Tuple[Dict[str, Any], ...]:
        if syndrome_id in self._fallback_cache:
            return self._fallback_cache[syndrome_id]

        unit_key = DEFAULT_SYNDROME_TRIAGE_UNITS.get(syndrome_id)
        resolved: List[Dict[str, Any]] = []
        if unit_key:
            unit_def = DEFAULT_TRIAGE_UNITS.get(unit_key)
            if not unit_def:
                logger.warning(
                    "Unknown default triage unit '%s' for syndrome '%s'",
                    unit_key,
                    syndrome_id,
                )
            else:
                resolved.append(
                    {
                        "triage_unit_id": unit_def["triage_unit_id"],
                        "department_id": unit_def.get("department_id"),
                        "name": unit_def.get("name"),
                        "priority": 1,
                    }
                )
        if not resolved:
            fallback = DEFAULT_TRIAGE_UNITS["general"]
            resolved.append(
                {
                    "triage_unit_id": fallback["triage_unit_id"],
                    "department_id": fallback.get("department_id"),
                    "name": fallback.get("name"),
                    "priority": 1,
                }
            )
        result = tuple(resolved)
        self._fallback_cache[syndrome_id] = result
        return result

    @staticmethod
    def _index_symptoms(symptoms: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        lookup: Dict[str, Dict[str, Any]] = {}
        for raw in symptoms:
            if not isinstance(raw, dict):
                continue
            symptom_id = raw.get("symptom_id")
            if not symptom_id or symptom_id == "fallback":
                continue
            confidence = TriageService._safe_float(raw.get("confidence"))
            if confidence <= 0.0:
                continue
            existing = lookup.get(symptom_id)
            if existing is None or confidence > TriageService._safe_float(existing.get("confidence")):
                lookup[symptom_id] = raw
        return lookup

    @staticmethod
    def _clone_matches(raw: Any) -> Tuple[Dict[str, Any], ...]:
        if isinstance(raw, dict):
            return (dict(raw),)
        if isinstance(raw, (list, tuple)):
            cloned: List[Dict[str, Any]] = []
            for item in raw:
                if isinstance(item, dict):
                    cloned.append(dict(item))
            return tuple(cloned)
        return ()

    @staticmethod
    def _safe_float(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _score_for_unit(payload: Dict[str, Any]) -> float:
        weighted = payload.get("weighted_score")
        if isinstance(weighted, (int, float)):
            return float(weighted)
        return TriageService._safe_float(payload.get("syndrome_score"))

    @staticmethod
    def _deduplicate_units(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        ordered_keys: List[str] = []
        by_unit: Dict[str, Dict[str, Any]] = {}

        for raw_entry in entries:
            key = raw_entry.get("triage_unit_id") or raw_entry.get("department_id")
            if not key:
                continue

            entry = dict(raw_entry)
            score = TriageService._score_for_unit(entry)
            source_info: Dict[str, Any] = {
                "syndrome_id": entry.get("syndrome_id"),
                "syndrome_name": entry.get("syndrome_name"),
                "score": entry.get("syndrome_score"),
            }
            if entry.get("weighted_score") is not None:
                source_info["weighted_score"] = entry.get("weighted_score")
            if entry.get("matches"):
                source_info["matches"] = entry.get("matches")

            existing = by_unit.get(key)
            if existing is None:
                entry["source_syndromes"] = [source_info]
                entry["best_score"] = score
                ordered_keys.append(key)
                by_unit[key] = entry
                continue

            existing.setdefault("source_syndromes", []).append(source_info)
            existing_priority = existing.get("priority")
            entry_priority = entry.get("priority")
            numeric_priorities = [
                value for value in (existing_priority, entry_priority) if isinstance(value, (int, float))
            ]
            if numeric_priorities:
                existing["priority"] = min(numeric_priorities)

            current_best = existing.get("best_score", 0.0)
            if score > current_best:
                existing["syndrome_id"] = entry.get("syndrome_id")
                existing["syndrome_name"] = entry.get("syndrome_name")
                existing["syndrome_score"] = entry.get("syndrome_score")
                if entry.get("weighted_score") is not None:
                    existing["weighted_score"] = entry.get("weighted_score")
                else:
                    existing.pop("weighted_score", None)
                existing["matches"] = entry.get("matches")
                existing["best_score"] = score

        result: List[Dict[str, Any]] = []
        for key in ordered_keys:
            entry = by_unit[key]
            entry.pop("best_score", None)
            result.append(entry)
        return result


@lru_cache(maxsize=1)
def get_triage_service() -> TriageService:
    """P2.1 - lru_cache replaces global singleton."""
    return TriageService()
