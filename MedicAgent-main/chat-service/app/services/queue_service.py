import os
from typing import Any, Dict, Optional

import requests

from ..servicelogs.servicelogger import logger


class QueueService:
    """Client wrapper for the queue service API."""

    def __init__(self, base_url: Optional[str] = None, *, timeout: float = 5.0) -> None:
        default_base = "http://medicagent-core-service:8080/v1"
        fallback_base = "http://localhost:8083/v1"
        configured = base_url or os.getenv("QUEUE_SERVICE_URL") or default_base
        self.base_url = (configured or fallback_base).rstrip("/")
        self.timeout = timeout

    def create_ticket(self, slots: Dict[str, Any], hospital_id: str) -> Dict[str, Any]:
        """Request the next queue number from the external queue service.

        Falls back to a synthetic ticket if the API is unavailable.
        """
        payload = {
            "patient_id": self._as_int(slots.get("patient_id"), default=1),
            "department_id": self._as_int(slots.get("department_id"), default=1),
            "service_package_id": self._as_int(slots.get("service_type"), default=1),
            "kiosk_id": self._as_int(slots.get("kiosk_id"), default=1),
        }
        endpoints = [
            # f"{self.base_url}/queue/queue/next-number",
            f"{self.base_url}/queue/next-number/{hospital_id}",
        ]
        for idx, url in enumerate(endpoints):
            try:
                response = requests.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                logger.info("QUEUE: issued ticket via API endpoint=%s payload=%s response=%s", url, payload, data)
                return {"ticket": data}
            except requests.HTTPError as http_err:
                status = http_err.response.status_code if http_err.response else None
                if status == 404 and idx + 1 < len(endpoints):
                    logger.warning("QUEUE: endpoint %s returned 404, retrying alternative", url)
                    continue
                logger.exception("QUEUE: HTTP error when requesting ticket", exc_info=http_err)
            except Exception as exc:  # noqa: BLE001
                logger.exception("QUEUE: failed to request ticket", exc_info=exc)
                break
        logger.error("QUEUE: falling back to synthetic ticket")
        fallback = {
            "ticket": {
                "queue_number": "N/A",
                "department_id": payload["department_id"],
                "service_package_id": payload["service_package_id"],
                "note": "Queue service unavailable",
            },
        }
        return fallback

    @staticmethod
    def _as_int(value: Any, *, default: int) -> int:
        try:
            if value is None or value == "":
                return default
            return int(value)
        except (TypeError, ValueError):
            return default
