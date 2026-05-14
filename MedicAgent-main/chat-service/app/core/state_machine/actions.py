# app/core/state_machine/actions.py

from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from ...servicelogs.servicelogger import logger
from ...repositories.directory_repository import get_directory_repository


SLOT_PROMPTS = {
    "department_id": "Vui lòng chọn khoa mà bạn muốn tới.",
    "service_type": "Bạn muốn thực hiện dịch vụ khám bệnh nào?",
    "service_name": "Bạn đang quan tâm đến dịch vụ/thủ tục nào?",
    "appointment_status": "Bạn đã có lịch hẹn trước chưa?",
    "document_have": "Bạn đã chuẩn bị sẵn giấy tờ nào?",
    "insurance_type": "Bạn sử dụng loại bảo hiểm nào?",
    "main_symptom": "Bạn đang gặp triệu chứng chính nào?",
    "age_group": "Độ tuổi của người cần hỗ trợ là bao nhiêu?",
    "gender": "Giới tính của người cần hỗ trợ là gì?",
    "to_poi": "Bạn muốn di chuyển đến khu vực nào trong bệnh viện?",
    "from_poi": "Hiện tại bạn đang đứng ở vị trí nào?",
    "mobility": "Bạn có yêu cầu hỗ trợ di chuyển đặc biệt nào không?",
    "language": "Bạn muốn nhận hướng dẫn bằng ngôn ngữ nào?",
}

CONFIRM_PROMPT = "Vui lòng kiểm tra lại thông tin và xác nhận để tiếp tục."


_DEPARTMENT_OPTIONS: List[Dict[str, Any]] = [
    {"id": 1, "name": "Khoa tổng quát"},
    {"id": 2, "name": "Khoa tim mạch"},
    {"id": 3, "name": "Khoa hô hấp"},
    {"id": 4, "name": "Khoa thần kinh"},
    {"id": 5, "name": "Chấn thương chỉnh hình"},
    {"id": 6, "name": "Khoa tai mũi họng"},
    {"id": 7, "name": "Khoa mắt"},
    {"id": 8, "name": "Khoa nhi"},
]

_SERVICE_PACKAGE_OPTIONS: List[Dict[str, Any]] = [
    {"id": 1, "name": "Khám có BHYT"},
    {"id": 2, "name": "Khám thường"},
    {"id": 3, "name": "Khám dịch vụ"},
    {"id": 4, "name": "Khám VIP"},
]

_INFO_TOPIC_OPTIONS: List[Dict[str, Any]] = [
    {"id": "insurance_policy", "name": "Quyền lợi BHYT"},
    {"id": "service_pricing", "name": "Giá dịch vụ khám chữa bệnh"},
    {"id": "procedure", "name": "Thủ tục, hồ sơ cần chuẩn bị"},
    {"id": "hospital_workflow", "name": "Quy trình khám chữa bệnh"},
]


class Actions:
    def __init__(self, ctx, queue_svc, map_svc, kb_svc, info_svc, reply, metrics):
        self.ctx = ctx
        self.queue = queue_svc
        self.map = map_svc
        self.kb = kb_svc
        self.info = info_svc
        self.reply = reply
        self.metrics = metrics
        self.directory_repo = get_directory_repository()
        self._department_options: List[Dict[str, Any]]
        self._service_package_options: List[Dict[str, Any]] = list(_SERVICE_PACKAGE_OPTIONS)

    def init_flow(self, name: str) -> None:
        self.ctx.start_flow(name)
        if name == "issue_ticket":
            self.ctx.flow.required_slots = ["service_type", "department_id"]
        elif name == "info_lookup":
            self.ctx.flow.required_slots = []
        logger.info("Flow initialized name=%s session=%s", name, self.ctx.session_id)
        setattr(self.ctx, "last_prompted_slot", None)
        setattr(self.ctx, "last_prompted_identity", None)
        setattr(self.ctx, "awaiting_health_book_confirmation", False)

    def set_required_slots(self, slots) -> None:
        cleaned = []
        for slot in slots or []:
            normalized = slot
            if normalized.endswith("[]"):
                normalized = normalized[:-2]
            if normalized.endswith("?"):
                normalized = normalized[:-1]
            cleaned.append(normalized)
        self.ctx.flow.required_slots = cleaned
        logger.debug("Set required slots %s", cleaned)

    def ask_next_slot(self) -> None:
        logger.debug("Asking for next missing slot %s", self.ctx.slots)
        key, prompt = self.ctx.next_missing_slot()
        if not key:
            logger.debug("No pending slot to ask; skipping prompt.")
            return
        display_prompt = SLOT_PROMPTS.get(key, prompt or f"Vui lòng cung cấp '{key}'")
        self._prompt_slot(key, display_prompt)
        
    def handle_emergency_response(self) -> None:
        
        self.reply.say(
            "Nếu bạn đang gặp tình huống khẩn cấp, vui lòng đến ngay khu vực cấp cứu."
        )
        
        
    def handle_emergency(self) -> None:
        hospital_id = self._resolve_hospital_id()
        logger.debug("Resolved hospital_id=%s for emergency info lookup", hospital_id)
        emergency_info = self.directory_repo.get_emergency_info(hospital_id)
        self.reply.show_info(emergency_info)

    def ask_slot_service_package(self) -> None:
        hospital_id = self._resolve_hospital_id()
        department_id = self.ctx.slots.get("department_id")
        choices: List[Dict[str, Any]] = []
        if department_id:
            try:
                packages = self.directory_repo.get_service_packages_by_department(str(department_id))
            except Exception:  # noqa: BLE001
                logger.exception(
                    "Failed to fetch service packages for department_id=%s", department_id
                )
            else:
                choices = [
                    {
                        "id": pkg.get("service_package_id"),
                        "name": pkg.get("name"),
                        "is_bhyt_applicable": pkg.get("is_bhyt_applicable"),
                    }
                    for pkg in packages
                    if isinstance(pkg, dict)
                    and pkg.get("service_package_id") is not None
                    and pkg.get("name")
                ]
        if hospital_id:
            if not choices:
                try:
                    packages = self.directory_repo.get_service_packages_name(hospital_id)
                except Exception:  # noqa: BLE001
                    logger.exception(
                        "Failed to fetch service packages for hospital_id=%s", hospital_id
                    )
                else:
                    choices = [
                        {
                            "id": pkg.get("service_package_id"),
                            "name": pkg.get("name"),
                            "is_bhyt_applicable": pkg.get("is_bhyt_applicable"),
                        }
                        for pkg in packages
                        if isinstance(pkg, dict)
                        and pkg.get("service_package_id") is not None
                        and pkg.get("name")
                    ]
        if choices:
            self._service_package_options = choices
        else:
            choices = list(_SERVICE_PACKAGE_OPTIONS)
            
        logger.debug("Service package choices: %s", choices)
        prompt = SLOT_PROMPTS.get("service_type", "Vui lòng chọn gói dich vụ khám bệnh")
        self._prompt_slot("service_type", prompt, options=choices or None)
        
    def ask_slot_department(self) -> None:
        hospital_id = self._resolve_hospital_id()
        logger.debug("Resolved hospital_id=%s for department lookup", hospital_id)
        service_package_id = self.ctx.slots.get("service_type")
        choices: List[Dict[str, Any]] = []
        if service_package_id and hospital_id:
            try:
                departments = self.directory_repo.get_departments_by_service_package(
                    str(hospital_id), str(service_package_id)
                )
            except Exception:  # noqa: BLE001
                logger.exception(
                    "Failed to fetch departments for hospital_id=%s service_package_id=%s",
                    hospital_id,
                    service_package_id,
                )
            else:
                choices = [
                    {"id": dept.get("department_id"), "name": dept.get("name")}
                    for dept in departments
                    if isinstance(dept, dict)
                    and dept.get("department_id") is not None
                    and dept.get("name")
                ]
        if hospital_id and not choices:
            try:
                departments = self.directory_repo.get_departments_name(hospital_id)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to fetch departments for hospital_id=%s", hospital_id)
            else:
                choices = [
                    {"id": dept.get("department_id"), "name": dept.get("name")}
                    for dept in departments
                    if isinstance(dept, dict)
                    and dept.get("department_id") is not None
                    and dept.get("name")
                ]
        if choices:
            self._department_options = choices
        else:
            choices = list(self._department_options or _DEPARTMENT_OPTIONS)
        prompt = SLOT_PROMPTS.get("department_id", "Vui long chon khoa/phong")
        self._prompt_slot("department_id", prompt, options=choices or None)

    def confirm_slots(self) -> None:
        self.ctx.waiting_confirm = True
        self.reply.summarize(self.ctx.slots)
        state_hint = self._format_state_hint("confirm")
        state_identity = state_hint or (self.ctx.state or "")
        self.reply.ask(CONFIRM_PROMPT, slot="confirm", state_hint=state_hint)
        setattr(self.ctx, "last_prompted_slot", "confirm")
        setattr(self.ctx, "last_prompted_identity", state_identity)

    def create_ticket(self) -> None:
        hospital_id = self._resolve_hospital_id()
        ticket_payload = self.queue.create_ticket(self.ctx.slots, hospital_id=hospital_id)
        ticket_info = ticket_payload.get("ticket", ticket_payload)
        dept_id = self.ctx.slots.get("department_id")
        svc_id = self.ctx.slots.get("service_type")
        dept_name = self._lookup_department_name(dept_id)
        svc_name = self._lookup_service_package_name(svc_id)
        if dept_name is not None:
            ticket_info.setdefault("department_name", dept_name)
        if svc_name is not None:
            ticket_info.setdefault("service_package_name", svc_name)
        self.reply.ticket_done({"ticket": ticket_info})
        self.metrics.bump("issue_ticket.done")

    def get_route(self) -> Optional[Any]:
        return self._prepare_route_response()

    def _prepare_route_response(self) -> Optional[Dict[str, Any]]:
        logger.debug("Handling get_route action")
        intent = (self.ctx.nlu.intent or "").lower()
        if intent == "kiosk_navigation":
            hospital_id = self._resolve_hospital_id()
            try:
                route = self.map.get_route(
                    self.ctx.slots,
                    hospital_id=hospital_id,
                )
                logger.debug("Computed route: %s", route)
            except ValueError as exc:
                logger.warning("MAP: unable to compute route (%s)", exc)
                self.metrics.bump("directions.error")
                return {
                    "info": "Mình chưa xác định được điểm đến để chỉ đường, bạn mô tả lại giúp mình nhé?",
                }
            except Exception:
                logger.exception("MAP: unexpected error while computing route")
                self.metrics.bump("directions.error")
                return {
                    "type": "say",
                    "payload": "Mình đang gặp sự cố khi tính đường đi, bạn vui lòng thử lại sau nhé.",
                }
        else:
            route = {
                "start": self.ctx.slots.get("from_poi", "KIOSK"),
                "end": self.ctx.slots.get("to_poi", "DEST"),
                "direction_text": "Tính năng chỉ đường đang được cập nhật.",
            }

        self.metrics.bump("directions.shown")
        return {"type": "info", "payload": {"topic": "kiosk_navigation", "route": route}}

    def query_procedure_kb(self) -> None:
        info = self.kb.query(self.ctx.slots)
        self.reply.show_checklist(info)

    def answer_info_lookup(self) -> Optional[Any]:
        question = (self.ctx.slots.get("info_question") or "").strip().lower()
        if not question:
            question = (self.ctx.slots.get("last_user_message") or "").strip()
        if not question:
            setattr(self.ctx, "suppress_hint_once", True)
            return {"type": "say", "payload": "Bạn muốn mình tra cứu thông tin gì?"}

        raw_topic = (self.ctx.slots.get("info_topic") or "").strip()
        topic = raw_topic or (self.ctx.nlu.intent or "").strip() or None
        if topic and not raw_topic:
            # persisting the inferred topic allows downstream guards to work consistently
            self.ctx.slots["info_topic"] = topic
        normalized_topic = (topic or "").strip()
        topic_handlers = {
            "service_pricing": self._answer_service_price_lookup,
            "service_price_lookup": self._answer_service_price_lookup,
            "insurance_policy": self._answer_policy_lookup,
            "kiosk_navigation": self._answer_kiosk_navigation,
            "hospital_workflow": self._answer_workflow_lookup,
        }

        handler = topic_handlers.get(normalized_topic)
        logger.debug("Info lookup handler for topic '%s': %s", normalized_topic, handler)
        if handler:
            
            payload = handler(question)
            # Todo: phần này lẽ ra không nên ở đây, đang trong luồng call_lookup.
            # Phần hỏi thêm này nên đặt trong ask_more_info, khi exit luồng, emplement tạm cho STT trước.
            # payload["prompt"] = "Thông tin đã hoàn tất, bạn có muốn tra cứu thêm thông tin gì thêm không?"
            self.reply.show_info(payload)
            return

        # Fallback to policy lookup flow for requests that the NLU could not categorize.
        return self._answer_policy_lookup(question, topic=normalized_topic or None)

    def prepare_info_lookup(self) -> None:
        question = (self.ctx.slots.get("info_question") or self.ctx.slots.get("last_user_message") or "").strip()
        if question:
            self.ctx.slots["info_question"] = question

    def ask_info_topic(self) -> None:
        # prompt = self.ctx.slots.pop("_info_topic_prompt_override", None)
        # if not prompt:
        #     prompt = (
        #         "Bạn cần tra cứu thông tin nào? Bạn có thể hỏi về bảo hiểm y tế, giá dịch vụ, thủ tục hồ sơ,"
        #         " hướng dẫn đường đi,..."
        #     )
        payload = {"message_no_stt": "Bạn cần tra cứu thông tin nào? Bạn có thể hỏi về bảo hiểm y tế, giá dịch vụ, thủ tục hồ sơ, hướng dẫn đường đi,...",
                   "audio_file": "ask_info_topic.mp3"}
        self.reply.static_ask(payload)

    def clear_info_topic(self) -> None:
        logger.debug("Clearing info lookup topic-related slots")
        # reset topic-related slots to avoid leaking into the next lookup request
        for key in ("info_topic", "info_question", "_info_topic_prompt_override"):
            self.ctx.slots.pop(key, None)

    def _response_contains_info(self, response: Optional[Any]) -> bool:
        if not response:
            return False
        responses = response if isinstance(response, list) else [response]
        for item in responses:
            if isinstance(item, dict) and item.get("type") == "info":
                return True
        return False

    def _answer_policy_lookup(self, question: str, topic: Optional[str] = None) -> Optional[Any]:
        hospital_id = self._resolve_hospital_id()
        lookup_topic = (topic or "insurance_policy").strip() or "insurance_policy"
        logger.debug("Handling policy lookup question=%s topic=%s", question, lookup_topic)
        try:
            if lookup_topic == "insurance_policy":
                response = self.info.lookup_policy(
                    question=question,
                    hospital_id=hospital_id,
                    max_results=1,
                )
            else:
                response = self.info.lookup_generic(
                    question=question,
                    topic=lookup_topic,
                    hospital_id=hospital_id,
                    max_results=1,
                )
        except Exception:  # noqa: BLE001
            logger.exception("Info lookup request failed question=%s topic=%s", question, lookup_topic)
            self.metrics.bump("info_lookup.error")
            setattr(self.ctx, "suppress_hint_once", True)
            return {"type": "say", "payload": "Hiện tại mình chưa tra cứu được thông tin này, bạn thử lại sau hoặc hỏi nhân viên hỗ trợ nhé."}

        response_payload = self._handle_lookup_response(
            question=question,
            topic=lookup_topic,
            response=response,
        )
        if self._response_contains_info(response_payload):
            self.metrics.bump("info_lookup.success")
        setattr(self.ctx, "suppress_hint_once", True)
        return response_payload

    def _answer_kiosk_navigation(self, question: str) -> Optional[Any]:
        logger.debug("Handling kiosk navigation request for question: %s", question)
        if (self.ctx.nlu.intent or "").lower() != "kiosk_navigation":
            self.ctx.nlu.intent = "kiosk_navigation"
        return self._prepare_route_response()

    def _answer_workflow_lookup(self, question: str) -> Optional[Any]:
        logger.debug("Handling hospital workflow lookup for question: %s", question)
        hospital_id = self._resolve_hospital_id()
        try:
            response = self.info.lookup_workflow(
                question=question,
                hospital_id=hospital_id,
                max_results=1,
            )
        except Exception:  # noqa: BLE001
            logger.exception("Workflow lookup request failed question=%s", question)
            self.metrics.bump("info_lookup.error")
            setattr(self.ctx, "suppress_hint_once", True)
            return {"type": "say", "payload": "Hiện tại mình chưa tra cứu được thông tin này, bạn thử lại sau hoặc hỏi nhân viên hỗ trợ nhé."}

        response_payload = self._handle_lookup_response(
            question=question,
            topic="hospital_workflow",
            response=response,
        )
        if self._response_contains_info(response_payload):
            self.metrics.bump("info_lookup.success")
        setattr(self.ctx, "suppress_hint_once", True)
        logger.debug(f"Return payload: {response_payload}")
        return response_payload

    def _handle_lookup_response(
        self,
        *,
        question: str,
        topic: str,
        response: Optional[Dict[str, Any]],
    ) -> Optional[Any]:
        results = (response or {}).get("results") if isinstance(response, dict) else None
        if not results:
            self.metrics.bump("info_lookup.empty")
            return {"type": "say", "payload": "Mình chưa tìm thấy thông tin phù hợp. Bạn có thể mô tả cụ thể hơn hoặc hỏi nhân viên hỗ trợ nhé."}

        top = results[0]
        answer_text = str(top.get("text") or "").strip()
        doc_title = top.get("doc_title")
        article_label = top.get("article_label")
        clause_id = top.get("clause_id")
        flowchart = top.get("flowchart")

        citation_parts: List[str] = []
        if doc_title:
            citation_parts.append(str(doc_title))
        if article_label:
            citation_parts.append(str(article_label))
        if clause_id:
            citation_parts.append(f"khoản {clause_id}")
        citation = ", ".join(citation_parts)

        if citation:
            # place holder for future citation message
            pass

        info_payload = {
            "question": question,
            "topic": topic,
            "all_results": (response or {}).get("markdown") if isinstance(response, dict) else "",
        }

        summary_text = answer_text or ""
        if flowchart:
            info_payload["flowchart"] = flowchart
            summary_text = self._format_flowchart_summary(flowchart) or summary_text
        if summary_text:
            if citation:
                summary_text = f"{summary_text}"
            info_payload["message"] = summary_text

        # responses: List[Dict[str, Any]] = []
        # if not answer_text:
        #     responses.append({"type": "say", "payload": "Mình đã tìm được thông tin liên quan, bạn kiểm tra giúp nhé."})

        # responses.append({"type": "info", "payload": info_payload})
        self.ctx.slots["info_last_result"] = top
        return info_payload

    def _answer_service_price_lookup(self, question: str) -> Optional[Any]:
        hospital_id = self._resolve_hospital_id()
        if not hospital_id:
            setattr(self.ctx, "suppress_hint_once", True)
            return {"message": "Mình chưa xác định được bệnh viện để tra cứu bảng giá. Bạn vui lòng chọn bệnh viện trước nhé."}

        payer_type = (
            (self.ctx.slots.get("payer_type") or self.ctx.slots.get("insurance_type") or "")
            .strip()
            .upper()
        ) or None
        service_code = (self.ctx.slots.get("service_code") or "").strip() or None
        area_tag = (self.ctx.slots.get("service_area") or "").strip() or None
        effective_date = (self.ctx.slots.get("price_effective_date") or "").strip() or None

        try:
            response = self.info.lookup_price(
                hospital_id=str(hospital_id),
                question=question,
                service_code=service_code,
                payer_type=payer_type,
                area_tag=area_tag,
                effective_date=effective_date,
                top_k=3,
            )
        except Exception:  # noqa: BLE001
            logger.exception("Price lookup failed question=%s hospital_id=%s", question, hospital_id)
            self.metrics.bump("info_lookup.price.error")
            setattr(self.ctx, "suppress_hint_once", True)
            return {"message": "Hiện tại mình chưa tra cứu được giá dịch vụ, bạn thử lại sau hoặc hỏi nhân viên hỗ trợ nhé."}

        suggestions = (response or {}).get("suggestions") or []
        results = []
        if isinstance(response, dict):
            if response.get("result"):
                results.append(response["result"])
            if response.get("results"):
                results.extend(response["results"])

        seen = set()
        deduped = []
        for item in results:
            svc_id = (item or {}).get("service_id")
            if svc_id in seen:
                continue
            seen.add(svc_id)
            deduped.append(item)
        results = deduped

        topic_label = (self.ctx.slots.get("info_topic") or "").strip() or "service_pricing"

        if results:
            message = self._format_price_results(results)
            # self.reply.show_info(message)
            price_payload = {
                "question": question,
                "topic": topic_label,
                "all_results": message,
            }
            # self.reply.show_info(price_payload)
            self.metrics.bump("info_lookup.price.success")
            self.ctx.slots["info_last_price_results"] = results
            setattr(self.ctx, "suppress_hint_once", True)
            return price_payload

        if suggestions:
            lines = [
                f"- {item.get('service_name')} (mã {item.get('service_code')})"
                for item in suggestions
                if item.get("service_name") and item.get("service_code")
            ]
            if lines:
                text = "Mình tìm thấy một số dịch vụ phù hợp:\n" + "\n".join(lines)
                text += "\nBạn vui lòng chọn mã dịch vụ hoặc mô tả cụ thể hơn nhé."
                self.ctx.slots["info_price_suggestions"] = suggestions
                setattr(self.ctx, "suppress_hint_once", True)
                return {"message": text}

        self.metrics.bump("info_lookup.price.empty")
        setattr(self.ctx, "suppress_hint_once", True)
        return {"mesage": "Mình chưa tìm thấy bảng giá phù hợp. Bạn có thể mô tả cụ thể hơn hoặc hỏi nhân viên hỗ trợ nhé."}

    def _format_price_results(self, results: List[Dict[str, Any]]) -> str:
        lines: List[str] = ["Mình tìm được thông tin giá như sau:"]
        for item in results:
            service_name = item.get("service_name") or "Dịch vụ"
            service_code = item.get("service_code")
            header = f"{service_name}"
            if service_code:
                header += f" (mã {service_code})"
            lines.append(header)
            prices = item.get("prices") or []
            if not prices:
                lines.append("- Chưa có giá áp dụng")
                continue
            for price in prices:
                payer_raw = price.get("payer_type")
                payer = ""
                if isinstance(payer_raw, str):
                    payer = payer_raw.replace("TU_CHI_TRA","Tự chi trả")
                elif payer_raw is not None:
                    payer = str(payer_raw)
                payer = payer or "Giá"
                value = self._format_price_value(price.get("price"))
                currency = price.get("currency") or ""
                # effective_from = price.get("effective_from")
                # effective_to = price.get("effective_to")
                notes = (price.get("notes") or "").strip()
                parts: List[str] = []
                # if effective_from:
                #     part = f"từ {effective_from}"
                #     if effective_to:
                #         part += f" đến {effective_to}"
                #     parts.append(part)
                # elif effective_to:
                #     parts.append(f"đến {effective_to}")
                if notes:
                    parts.append(notes)
                detail = f" ({'; '.join(parts)})" if parts else ""
                lines.append(f"- {payer}: {value} {currency}{detail}".rstrip())
        return "\n".join(lines)

    def _format_flowchart_summary(self, flowchart: Dict[str, Any]) -> str:
        if not isinstance(flowchart, dict):
            return ""
        title = str(flowchart.get("title") or "").strip()
        steps = flowchart.get("steps") or []
        parts: List[str] = []
        if title:
            parts.append(title)
        for idx, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                continue
            label = str(step.get("title") or "").strip() or f"Bước {idx}"
            description = str(step.get("description") or "").strip()
            line = f"Bước {idx}: {label}"
            if description:
                line += f" - {description}"
            parts.append(line)
        return ". ".join(part for part in parts if part).strip()

    def ask_more_info(self) -> None:
        logger.info("Prompting user for additional info lookup")
        payload = {"message_no_stt": "Thông tin đã hoàn tất, bạn có muốn tra cứu thêm thông tin gì thêm không?",
                   "audio_file": "ask_more_info.mp3"
                   }
        self.reply.static_ask(payload)
        # followup_prompt = "Bạn có cần hỏi thêm thông tin gì khác không? Nếu có, bạn cứ nhập câu hỏi mới nhé."
        # self.ctx.slots["_info_topic_prompt_override"] = followup_prompt

    def _format_price_value(self, value: Any) -> str:
        if value in (None, ""):
            return ""
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return str(value)
        quantized = amount.quantize(Decimal("0.01"))
        if quantized == quantized.to_integral():
            return f"{int(quantized):,}".replace(",", ".") # Đổi dấu phẩy thành dấu chấm phân cách hàng nghìn, ví dụ 1.200.000 (1 triêu hai trăm nghìn)
        return f"{quantized:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def finish_info_lookup(self) -> None:
        self.ctx.reset()
        setattr(self.ctx, "last_prompted_slot", None)
        setattr(self.ctx, "last_prompted_identity", None)
        setattr(self.ctx, "suppress_hint_once", True)

    # def query_triage_kb(self) -> None:
    #     try:
    #         suggestions = self.kb.query(self.ctx.slots)
    #     except Exception:
    #         suggestions = None
    #     self.reply.show_triage_suggestions(suggestions)

    def prompt_orchestrating_hint(self) -> None:
        if getattr(self.ctx, "suppress_hint_once", False):
            setattr(self.ctx, "suppress_hint_once", False)
            return
        self.reply.say("Ban muon gap bac si, chi duong hay hoi thu tuc?")

    def smalltalk(self) -> None:
        self.reply.smalltalk()

    def ask_emergency(self) -> None:
        prompt = (
            "Bạn có đang gặp tình huống khẩn cấp cần được hỗ trợ ngay không? "
            "Một số dấu hiệu khẩn cấp thường gặp gồm:"
        )
        options = [
            {"id": "1", "name": "Đau ngực hoặc khó thở dữ dội"},
            {"id": "2", "name": "Co giật, ngất xỉu, hoặc mất ý thức"},
            {"id": "3", "name": "Bị tai nạn, bị thương nặng, chảy máu không cầm được"},
        ]
        state_hint = self.ctx.state or "ask_emergency"
        self.reply.ask(prompt, state_hint = state_hint, options=options)

    def ask_main_symptom(self) -> None:
        prompt = SLOT_PROMPTS.get("main_symptom", "Bạn đang gặp triệu chứng chính nào?")
        self._prompt_slot("main_symptom", prompt, required=True)

    def show_triage_suggestions(self) -> None:
        suggestions = self.ctx.slots.get("triage_suggestions") or []
        names = [
            str(item.get("name"))
            for item in suggestions
            if isinstance(item, dict) and item.get("name")
        ]
        logger.debug("Sending triage suggestion names to client: %s", names)
        self.reply.suggest(names)
        
    def prompt_triage_suggestions(self) -> None:
        suggestions = self.ctx.slots.get("triage_suggestions") or []
        deparment_name = suggestions[0].get("name") if suggestions and isinstance(suggestions[0], dict) else None
        if deparment_name:
            self.reply.say(f"Triệu chứng của bạn phù hợp với {deparment_name}")
        else:
            self.reply.say("Không tìm đươc khoa phù hợp với triệu chứng của bạn, vui lòng liên hệ nhân viên y tế để được hỗ trợ.")
        
        
    
    def suggest_humman_handoff(self) -> None:
        self.reply.say("Mình sẽ kết nối bạn với nhân viên y tế để hỗ trợ cụ thể hơn.")

    def do_nothing(self) -> None:
        logger.debug("No-op action invoked for current transition.")

    def reset_flow(self) -> None:
        self.ctx.reset()
        setattr(self.ctx, "last_prompted_slot", None)
        setattr(self.ctx, "last_prompted_identity", None)
        self.reply.say("Da huy thao tac, quay lai man hinh chinh.")

    def prompt_additional_lookup(self) -> None:
        prompt = "Bạn có muốn tra cứu các thông tin khác không?"
        state_hint = "state.issue_ticket.follow_up"
        options = [
            {"id": "yes", "name": "Có"},
            {"id": "no", "name": "Không"},
        ]
        self.reply.ask(prompt, slot="followup_choice", state_hint=state_hint, required=True, options=options)
        setattr(self.ctx, "last_prompted_slot", "followup_choice")
        setattr(self.ctx, "last_prompted_identity", state_hint)

    def followup_continue(self) -> None:
        self.ctx.reset()
        setattr(self.ctx, "last_prompted_slot", None)
        setattr(self.ctx, "last_prompted_identity", None)
        self.reply.say("Mình quay lại hỗ trợ bạn tra cứu thông tin khác nhé.")

    def followup_end_session(self) -> None:
        self.ctx.reset()
        setattr(self.ctx, "last_prompted_slot", None)
        setattr(self.ctx, "last_prompted_identity", None)
        self.reply.say("Cảm ơn bạn. Nếu cần hỗ trợ thêm, hãy nói với mình bất cứ lúc nào.")

    def fallback_suggest(self) -> None:
        self.reply.suggest(["Gap bac si", "Chi duong", "Hoi thu tuc"])

    def on_timeout(self) -> None:
        self.reply.say("Dang tam dung do khong tuong tac. Ban co the bat dau lai bat cu luc nao.")

    def ask_personal_health_book(self) -> None:
        prompt = "Bạn đã có sổ khám bệnh cá nhân chưa?"
        state_hint = "state.issue_ticket.ask_per_health_book"
        self.ctx.awaiting_health_book_confirmation = True
        self.reply.ask(prompt, slot="has_health_book", state_hint=state_hint, required=True)
        setattr(self.ctx, "last_prompted_slot", "has_health_book")
        setattr(self.ctx, "last_prompted_identity", state_hint)

    def mark_health_book_present(self) -> None:
        self.ctx.slots["has_health_book"] = True
        self.ctx.awaiting_health_book_confirmation = False
        setattr(self.ctx, "last_prompted_slot", None)
        setattr(self.ctx, "last_prompted_identity", None)

    def require_health_book_first(self) -> None:
        message = "Bạn cần mua sổ khám bệnh trước khi đăng ký khám."
        self.ctx.slots["has_health_book"] = False
        self.ctx.awaiting_health_book_confirmation = False
        self.ctx.reset()
        setattr(self.ctx, "last_prompted_slot", None)
        setattr(self.ctx, "last_prompted_identity", None)
        self.reply.say(message)

    def _prompt_slot(
        self,
        slot: str,
        prompt: str,
        *,
        options: Optional[List[Dict[str, Any]]] = None,
        required: bool = True,
    ) -> None:
        state_hint = self._format_state_hint(slot)
        state_identity = state_hint or (self.ctx.state or "")
        prev_slot = getattr(self.ctx, "last_prompted_slot", None)
        prev_identity = getattr(self.ctx, "last_prompted_identity", None)
        if prev_slot == slot and prev_identity == state_identity:
            logger.debug("Skip duplicate prompt for slot=%s identity=%s", slot, state_identity)
            return
        self.reply.ask(prompt, slot=slot, state_hint=state_hint, required=required, options=options)
        setattr(self.ctx, "last_prompted_slot", slot)
        setattr(self.ctx, "last_prompted_identity", state_identity)

    def _format_state_hint(self, slot: Optional[str]) -> Optional[str]:
        state_path = self.ctx.state or ""
        if not state_path:
            return None
        if slot == "confirm" and state_path.endswith(".GATHER"):
            state_path = state_path[: -len(".GATHER")] + ".CONFIRM"
        parts: List[str] = []
        for piece in state_path.split("."):
            if not piece or piece.upper() == "ROOT":
                continue
            normalized = piece.lower()
            if normalized.startswith("flow_"):
                normalized = normalized[5:]
            parts.append(normalized)
        if not parts:
            return None
        base = "state." + ".".join(parts)
        if slot:
            if slot == "confirm":
                return f"{base}.confirm"
            return f"{base}.askslot.{slot}"
        return base

    def _resolve_hospital_id(self) -> Optional[str]:
        slot_value = self.ctx.slots.get("hospital_id")
        if slot_value not in (None, "", []):
            return str(slot_value)
        context_value = getattr(self.ctx, "hospital_id", None)
        if context_value not in (None, "", []):
            return str(context_value)
        tenant_value = getattr(self.ctx, "tenant_id", None)
        if tenant_value not in (None, "", []):
            return str(tenant_value)
        return None

    def _lookup_department_name(self, dept_id: Any) -> Optional[str]:
        if dept_id is None:
            return None
        options = getattr(self, "_department_options", _DEPARTMENT_OPTIONS)
        for option in options:
            option_id = option.get("id")
            if option_id is None:
                option_id = option.get("department_id")
            if str(option_id) == str(dept_id):
                return option.get("name")
        return None

    def _lookup_service_package_name(self, service_id: Any) -> Optional[str]:
        if service_id is None:
            return None
        options = getattr(self, "_service_package_options", _SERVICE_PACKAGE_OPTIONS)
        for option in options:
            if str(option.get("id")) == str(service_id):
                return option.get("name")
        return None
