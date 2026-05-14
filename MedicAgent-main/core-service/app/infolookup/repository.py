from __future__ import annotations

import json
import re
import unicodedata
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from app.core.config import settings
from app.infolookup.embedding import SemanticSearcher
from app.servicelogs.servicelogger import logger

PARAGRAPH_TOKEN_WEIGHT = 0.1
QA_TOKEN_WEIGHT = 2
SEMANTIC_QA_WEIGHT = 3


@dataclass(frozen=True)
class KnowledgeSource:
    topic: str
    file_path: Path
    hospital_id: Optional[str] = None


@dataclass
class KnowledgeEntry:
    entry_id: str
    doc_id: str
    doc_title: Optional[str]
    topic: str
    source: str
    chapter_label: Optional[str]
    chapter_title: Optional[str]
    article_label: Optional[str]
    article_title: Optional[str]
    clause_id: Optional[str]
    text: str
    keywords: List[str]
    numerical_values: List[str]
    qas: List[str]
    hospital_id: Optional[str]
    # Pre-computed helper fields
    normalized_text: str
    tokens: set[str]
    keyword_tokens: set[str]
    paragraph_tokens: set[str]
    qa_tokens: set[str]
    flowchart: Optional[Dict[str, Any]] = None
    workflow_type: Optional[str] = None

    def score(self, question_tokens: set[str], question_norm: str, question_numbers: set[str]) -> float:
        if not self.text:
            return 0.0
        paragraph_overlap = len(self.paragraph_tokens & question_tokens)
        qa_overlap = len(self.qa_tokens & question_tokens)
        weighted_overlap = (
            paragraph_overlap * PARAGRAPH_TOKEN_WEIGHT + qa_overlap * QA_TOKEN_WEIGHT
        )
        if weighted_overlap == 0:
            # fallback to substring match on shorter snippets
            if len(self.normalized_text) <= 120 and self.normalized_text and self.normalized_text in question_norm:
                weighted_overlap = PARAGRAPH_TOKEN_WEIGHT
            else:
                return 0.0

        base = weighted_overlap / max(len(question_tokens), 1)

        # keyword boost
        keyword_hit = bool(self.keyword_tokens & question_tokens)
        if not keyword_hit:
            for kw in self.keywords:
                kw_norm = _normalize_text(kw)
                if kw_norm and kw_norm in question_norm:
                    keyword_hit = True
                    break
        if keyword_hit:
            base += 0.15

        # numerical boost
        if self.numerical_values and question_numbers:
            for num in self.numerical_values:
                num_norm = _normalize_text(num)
                if num_norm and num_norm in question_numbers:
                    base += 0.1
                    break

        # explicit article/clause mention
        if self.article_label:
            token = _normalize_text(self.article_label)
            if token and token in question_norm:
                base += 0.05
        if self.clause_id:
            clause_token = f"khoan {self.clause_id}"
            if clause_token in question_norm:
                base += 0.03

        return min(base, 1.5)


def _normalize_text(value: str) -> str:
    text = value.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^a-z0-9% ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _tokenize(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9%]+", value))


def _normalize_hospital_id(value: Optional[str]) -> Optional[str]:
    """Normalize various hospital identifiers to a numeric string (e.g. `1`) when possible."""
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    text = text.replace("_", "")
    if text.startswith("hospital"):
        text = text[len("hospital") :].strip()
    if not text:
        return None
    if text.isdigit():
        return str(int(text)) if text != "0" else "0"
    digits = "".join(ch for ch in text if ch.isdigit())
    if digits:
        return str(int(digits)) if digits != "0" else "0"
    return text


def _normalize_qas(value: object) -> List[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    qas: List[str] = []
    if isinstance(value, (list, tuple, set)):
        for item in value:
            if isinstance(item, str):
                item_str = item.strip()
                if item_str:
                    qas.append(item_str)
    return qas


def _extract_paragraph_components(raw: object) -> tuple[str, List[str]]:
    if isinstance(raw, dict):
        text = str(raw.get("text") or "").strip()
        qas_list = _normalize_qas(raw.get("qas"))
        return text, qas_list
    text = str(raw or "").strip()
    return text, []


class KnowledgeRepository:
    """
    Load structured knowledge base documents (JSON) and expose lightweight search.
    """

    def __init__(self, sources: Optional[Sequence[KnowledgeSource]] = None):
        if sources is None:
            sources = self._default_sources()
        self.sources = list(sources)
        self.entries: List[KnowledgeEntry] = []
        self.entry_map: Dict[str, KnowledgeEntry] = {}
        self.semantic = SemanticSearcher()
        self.lexical_weight = float(settings.INFO_LOOKUP_LEXICAL_WEIGHT)
        self.semantic_weight = float(settings.INFO_LOOKUP_SEMANTIC_WEIGHT)
        self.lexical_max_score = 0.2
        self._normalize_weights()
        self._load_sources()
        if self.semantic.enabled and self.entries:
            self.semantic.index(self.entries)

    def _normalize_weights(self) -> None:
        if not self.semantic.enabled:
            self.lexical_weight = 1.0
            self.semantic_weight = 0.0
            return
        total = self.lexical_weight + self.semantic_weight
        if total <= 0:
            self.lexical_weight = 0.5
            self.semantic_weight = 0.5
        else:
            self.lexical_weight /= total
            self.semantic_weight /= total
        logger.debug(f"KnowledgeRepository weights normalized: lexical={self.lexical_weight}, semantic={self.semantic_weight}")  # debug log

    def _default_sources(self) -> List[KnowledgeSource]:
        base_dir = Path(__file__).resolve().parents[1] / "knowledgebases"
        return [
            KnowledgeSource(
                topic="insurance_policy_qa",
                file_path=base_dir / "bhyt_qa.json",
                hospital_id=None,
            ),
            KnowledgeSource(
                topic="insurance_policy",
                file_path=base_dir / "bhyt_qa.json",
                hospital_id=None,
            ),
            KnowledgeSource(
                topic="hospital_workflow",
                file_path=base_dir / "hospital_workflows.json",
                hospital_id=None,
            ),
            KnowledgeSource(
                topic="hospital_workflow",
                file_path=base_dir / "hospital_1" / "workflows.json",
                hospital_id="1",
            ),
        ]

    def _load_sources(self) -> None:
        entries: List[KnowledgeEntry] = []
        for source in self.sources:
            if not source.file_path.exists():
                logger.warning("Knowledge base file missing: %s", source.file_path)
                continue
            try:
                data = json.loads(source.file_path.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.error("Failed to load knowledge base %s: %s", source.file_path, exc)
                continue
            entries.extend(self._flatten_document(data, source))

        self.entries = entries
        self.entry_map = {entry.entry_id: entry for entry in entries}
        logger.info("Loaded %d knowledge snippets from %d sources", len(entries), len(self.sources))

    def _flatten_document(self, data: dict, source: KnowledgeSource) -> Iterable[KnowledgeEntry]:
        metadata = data.get("metadata", {})
        doc_id = metadata.get("doc_id") or source.file_path.stem
        doc_title = metadata.get("title")
        source_path = str(source.file_path)

        for chapter in data.get("chapters", []):
            chapter_label = chapter.get("label")
            chapter_title = chapter.get("title")
            articles = chapter.get("articles") or []
            for article in articles:
                article_label = article.get("label")
                article_title = article.get("title")
                article_keywords = article.get("keywords") or []
                article_numbers = article.get("numerical_values") or []
                article_qas = _normalize_qas(article.get("qas"))
                merged_paragraphs = self._merge_paragraphs(article.get("paragraphs") or [])
                paragraph_texts: List[str] = []
                paragraph_qas: List[str] = []
                for paragraph_text, paragraph_qas_list in merged_paragraphs:
                    text_value = (paragraph_text or "").strip()
                    if text_value:
                        paragraph_texts.append(text_value)
                    if paragraph_qas_list:
                        paragraph_qas.extend(paragraph_qas_list)

                full_text = "\n".join(paragraph_texts).strip()
                if not full_text:
                    continue
                combined_qas = list(article_qas) + paragraph_qas

                yield self._build_entry(
                    topic=source.topic,
                    doc_id=doc_id,
                    doc_title=doc_title,
                    source_path=source_path,
                    chapter_label=chapter_label,
                    chapter_title=chapter_title,
                    article_label=article_label,
                    article_title=article_title,
                    clause_id=None,
                    text=full_text,
                    qas=combined_qas,
                    keywords=article_keywords,
                    numbers=article_numbers,
                    hospital_id=source.hospital_id,
                    flowchart=article.get("flowchart"),
                    workflow_type=article.get("workflow_type"),
                )

    @staticmethod
    def _merge_paragraphs(paragraphs: Sequence[object]) -> List[tuple[str, List[str]]]:
        merged: List[tuple[str, List[str]]] = []
        for raw in paragraphs:
            text, qas = _extract_paragraph_components(raw)
            if not text:
                continue
            merged.append((text, list(qas)))
        return merged

    def _build_entry(
        self,
        *,
        topic: str,
        doc_id: str,
        doc_title: Optional[str],
        source_path: str,
        chapter_label: Optional[str],
        chapter_title: Optional[str],
        article_label: Optional[str],
        article_title: Optional[str],
        clause_id: Optional[str],
        text: str,
        qas: List[str],
        keywords: List[str],
        numbers: List[str],
        hospital_id: Optional[str],
        flowchart: Optional[Dict[str, Any]],
        workflow_type: Optional[str] = None,
    ) -> KnowledgeEntry:
        normalized_hospital = _normalize_hospital_id(hospital_id)
        qas_clean = [qa.strip() for qa in (qas or []) if qa and qa.strip()]
        augmented_text = " ".join(part for part in [text, *qas_clean] if part)
        text_norm = _normalize_text(text)
        paragraph_tokens = _tokenize(text_norm)
        qa_tokens: set[str] = set()
        for qa in qas_clean:
            qa_tokens.update(_tokenize(_normalize_text(qa)))
        normalized_text = _normalize_text(augmented_text)
        tokens = paragraph_tokens | qa_tokens
        keyword_tokens = set()
        for kw in keywords or []:
            keyword_tokens.update(_tokenize(_normalize_text(kw)))

        entry_id = self._generate_entry_id(
            doc_id=doc_id,
            article_label=article_label,
            clause_id=clause_id,
            text=text,
        )

        return KnowledgeEntry(
            entry_id=entry_id,
            doc_id=doc_id,
            doc_title=doc_title,
            topic=topic,
            source=source_path,
            chapter_label=chapter_label,
            chapter_title=chapter_title,
            article_label=article_label,
            article_title=article_title,
            clause_id=clause_id,
            text=text,
            qas=qas_clean,
            keywords=keywords,
            numerical_values=numbers,
            hospital_id=normalized_hospital,
            normalized_text=normalized_text,
            tokens=tokens,
            keyword_tokens=keyword_tokens,
            paragraph_tokens=paragraph_tokens,
            qa_tokens=qa_tokens,
            flowchart=flowchart,
            workflow_type=(workflow_type or "").strip().lower() or None,
        )

    def _generate_entry_id(
        self,
        *,
        doc_id: str,
        article_label: Optional[str],
        clause_id: Optional[str],
        text: str,
    ) -> str:
        raw = "|".join(
            [
                doc_id or "",
                article_label or "",
                clause_id or "",
            ]
        )
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        return f"{raw}|{text_hash}"

    def search(
        self,
        question: str,
        *,
        topic: Optional[str] = None,
        hospital_id: Optional[str] = None,
        workflow_type: Optional[str] = None,
        limit: int = 3,
    ) -> List[tuple[KnowledgeEntry, float]]:
        question_norm = _normalize_text(question)
        question_tokens = _tokenize(question_norm)
        if not question_tokens or limit <= 0:
            return []

        question_numbers = {tok for tok in question_tokens if re.match(r"^\d+%?$", tok)}
        normalized_hospital = _normalize_hospital_id(hospital_id)

        lexical_scores: Dict[str, float] = {}
        for entry in self.entries:
            if topic and entry.topic != topic:
                continue
            if normalized_hospital and entry.hospital_id:
                entry_hospital = _normalize_hospital_id(entry.hospital_id)
                if entry_hospital != normalized_hospital:
                    continue
            if workflow_type:
                normalized = workflow_type.strip().lower()
                entry_type = (entry.workflow_type or "").strip().lower()
                if normalized and entry_type and entry_type != normalized:
                    continue
                if normalized and not entry_type:
                    continue
            score = entry.score(question_tokens, question_norm, question_numbers)
            if score > 0.0:
                lexical_scores[entry.entry_id] = score

        semantic_scores: Dict[str, float] = {}
        if self.semantic.enabled:
            semantic_hits = self.semantic.search(
                question,
                topic=topic,
                hospital_id=normalized_hospital,
                limit=max(limit * 2, 10),
            )
            for entry_id, sem_score, source in semantic_hits:
                if entry_id not in self.entry_map:
                    continue
                weight = SEMANTIC_QA_WEIGHT if source == "qa" else 1.0
                score = max(float(sem_score) * weight, 0.0)
                semantic_scores[entry_id] = max(semantic_scores.get(entry_id, 0.0), score)

        candidate_ids: Set[str] = set(lexical_scores) | set(semantic_scores)
        if not candidate_ids:
            return []

        results: List[tuple[KnowledgeEntry, float]] = []
        for entry_id in candidate_ids:
            entry = self.entry_map.get(entry_id)
            if not entry:
                continue
            lex_score = lexical_scores.get(entry_id, 0.0)
            sem_score = semantic_scores.get(entry_id, 0.0)
            lex_norm = min(lex_score / self.lexical_max_score, 1.0) if self.lexical_max_score else lex_score
            final_score = self.lexical_weight * lex_norm + self.semantic_weight * sem_score
            if lex_score > 0 and sem_score > 0:
                final_score += 0.05
            results.append((entry, final_score))

        results.sort(key=lambda item: item[1], reverse=True)
        return results[:limit]

    def reload(self) -> None:
        """Reload sources from disk (useful during development)."""
        self._load_sources()
        if self.semantic.enabled and self.entries:
            self.semantic.index(self.entries)
