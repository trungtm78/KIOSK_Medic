from __future__ import annotations

import os
import re
from typing import Any, Callable, Dict, Optional, Sequence

import requests

from ..servicelogs.servicelogger import logger


class InfoLookupService:
    """HTTP client wrapper for the core-service info lookup API."""

    def __init__(self, base_url: Optional[str] = None, *, timeout: float = 6.0) -> None:
        default_base = "http://medicagent-core-service:8080"
        fallback_base = "http://localhost:8083"
        configured = base_url or os.getenv("INFO_LOOKUP_SERVICE_URL") or default_base
        self.base_url = (configured or fallback_base).rstrip("/")
        self.endpoint = f"{self.base_url}/v1/info/lookup"
        self.price_endpoint = f"{self.base_url}/v1/info/prices/lookup"
        self.timeout = timeout

    def lookup(
        self,
        *,
        question: str,
        topic: Optional[str] = None,
        hospital_id: Optional[str] = None,
        max_results: int = 1,
    ) -> Dict[str, Any]:
        return self.lookup_generic(
            question=question,
            topic=topic,
            hospital_id=hospital_id,
            max_results=max_results,
        )

    def lookup_generic(
        self,
        *,
        question: str,
        topic: Optional[str] = None,
        hospital_id: Optional[str] = None,
        max_results: int = 1,
    ) -> Dict[str, Any]:
        return self._lookup_topic(
            question=question,
            topic=topic,
            hospital_id=hospital_id,
            max_results=max_results,
        )

    def lookup_policy(
        self,
        *,
        question: str,
        hospital_id: Optional[str] = None,
        max_results: int = 1,
    ) -> Dict[str, Any]:
        return self._lookup_topic(
            question=question,
            topic="insurance_policy",
            hospital_id=hospital_id,
            max_results=max_results,
        )

    def lookup_workflow(
        self,
        *,
        question: str,
        hospital_id: Optional[str] = None,
        max_results: int = 1,
    ) -> Dict[str, Any]:
        return self._lookup_topic(
            question=question,
            topic="hospital_workflow",
            hospital_id=hospital_id,
            max_results=max_results,
            markdown_formatter=self._format_workflow_markdown,
        )

    def lookup_price(
        self,
        *,
        hospital_id: str,
        question: Optional[str] = None,
        service_code: Optional[str] = None,
        payer_type: Optional[str] = None,
        area_tag: Optional[str] = None,
        effective_date: Optional[str] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "hospital_id": hospital_id,
            "top_k": max(1, min(top_k, 10)),
        }
        if service_code:
            payload["service_code"] = service_code
        if question:
            payload["q"] = question
        normalized_question = (question or "").lower()
        if normalized_question:
            if any(term in normalized_question for term in ("tự chi trả", "không bảo hiểm", "tự túc")):
                payer_type = "TU_CHI_TRA"
            elif any(term in normalized_question for term in ("bhyt", "bảo hiểm y tế", "bảo hiểm")):
                payer_type = "BHYT"
        if payer_type:
            payload["payer_type"] = payer_type
        if area_tag:
            payload["area_tag"] = area_tag
        if effective_date:
            payload["effective_date"] = effective_date

        try:
            response = requests.post(self.price_endpoint, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            logger.info(
                "PRICE LOOKUP: success endpoint=%s payload=%s",
                self.price_endpoint,
                payload,
            )
            return data if isinstance(data, dict) else {}
        except requests.HTTPError as http_err:
            logger.exception("PRICE LOOKUP: HTTP error", exc_info=http_err)
        except Exception as exc:  # noqa: BLE001
            logger.exception("PRICE LOOKUP: request failed", exc_info=exc)
        return {}

    def _lookup_topic(
        self,
        *,
        question: str,
        topic: Optional[str],
        hospital_id: Optional[str],
        max_results: int,
        markdown_formatter: Optional[Callable[[Optional[Sequence[Dict[str, Any]]]], str]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "question": question,
            "max_results": max(1, min(max_results, 5)),
        }
        if topic:
            payload["topic"] = topic
        if hospital_id:
            payload["hospital_id"] = str(hospital_id)

        try:
            response = requests.post(self.endpoint, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                formatter = markdown_formatter or self._format_results_markdown
                data["markdown"] = formatter(data.get("results"))
            logger.info(
                "INFO LOOKUP: success endpoint=%s payload=%s results=%s",
                self.endpoint,
                payload,
                len(data.get("results", []) if isinstance(data, dict) else []),
            )
            return data if isinstance(data, dict) else {}
        except requests.HTTPError as http_err:
            logger.exception("INFO LOOKUP: HTTP error", exc_info=http_err)
        except Exception as exc:  # noqa: BLE001
            logger.exception("INFO LOOKUP: request failed", exc_info=exc)
        return {}

    def _format_results_markdown(self, results: Optional[Sequence[Dict[str, Any]]]) -> str:
        if not results:
            return ""

        sections: list[str] = []
        for idx, item in enumerate(results, start=1):
            doc_title = (item or {}).get("doc_title") or (item or {}).get("doc_id") or "Tài liệu liên quan"
            chapter_label = (item or {}).get("chapter_label")
            chapter_title = (item or {}).get("chapter_title")
            article_label = (item or {}).get("article_label")
            article_title = (item or {}).get("article_title")
            paragraph_text = ((item or {}).get("text") or "").strip()

            header = f"# {idx}. {doc_title}"
            sections.append(header)

            meta_parts: list[str] = []
            if chapter_label or chapter_title:
                chapter = " ".join(part for part in [chapter_label, chapter_title] if part)
                meta_parts.append(chapter)
            if article_label or article_title:
                article = " ".join(part for part in [article_label, article_title] if part)
                meta_parts.append(article)

            if meta_parts:
                sections.append(f"**{' – '.join(meta_parts)}**")

            if paragraph_text:
                sections.extend(self._format_paragraph_text(paragraph_text))

            sections.append("")  # blank line between entries

        return "\n".join(sections).strip()

    def _format_paragraph_text(self, paragraph: str) -> list[str]:
        if not paragraph:
            return []

        lines: list[str] = []
        markers = (" a)", " b)", " c)", " d)", " đ)", " e)", " g)", " h)", " i)", " k)")
        if any(marker in paragraph for marker in markers):
            normalized = paragraph.replace(";", "; ")
            segments = [seg.strip() for seg in normalized.split(";") if seg.strip()]
            for segment in segments:
                bullet = self._format_sub_clause(segment)
                lines.append(f"- {bullet}")
        else:
            lines.append(paragraph)
        return lines

    def _format_sub_clause(self, clause: str) -> str:
        clause = clause.strip()
        match = re.match(r"^([a-z])\)\s*(.*)$", clause)
        if match:
            label, body = match.groups()
            return f"({label}) {body.strip()}"
        return clause

    def _format_workflow_markdown(self, results: Optional[Sequence[Dict[str, Any]]]) -> str:
        if not results:
            return ""
        sections: list[str] = []
        for idx, item in enumerate(results, start=1):
            flowchart = (item or {}).get("flowchart") or {}
            flow_title = (flowchart or {}).get("title") or (item or {}).get("doc_title") or (item or {}).get("doc_id") or "Quy trình"
            description = (flowchart or {}).get("description") or ""
            sections.append(f"# {idx}. {flow_title}")
            if description:
                sections.append(description)
            steps = (flowchart or {}).get("steps") or []
            if steps:
                for step_idx, step in enumerate(steps, start=1):
                    if not isinstance(step, dict):
                        continue
                    title = str(step.get("title") or "").strip() or f"Bước {step_idx}"
                    desc = str(step.get("description") or "").strip()
                    line = f"{step_idx}. {title}"
                    if desc:
                        line += f": {desc}"
                    sections.append(line)
            else:
                paragraph_text = ((item or {}).get("text") or "").strip()
                if paragraph_text:
                    sections.append(paragraph_text)
            sections.append("")
        return "\n".join(sections).strip()


_INFO_LOOKUP_SINGLETON: Optional[InfoLookupService] = None


def get_info_lookup_service() -> InfoLookupService:
    global _INFO_LOOKUP_SINGLETON
    if _INFO_LOOKUP_SINGLETON is None:
        _INFO_LOOKUP_SINGLETON = InfoLookupService()
    return _INFO_LOOKUP_SINGLETON
