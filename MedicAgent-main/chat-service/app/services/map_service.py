from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests

from ..repositories.directory_repository import DirectoryRepository, get_directory_repository
from ..servicelogs.servicelogger import logger


class MapService:
    def __init__(
        self,
        map_base_url: Optional[str] = None,
        directory_base_url: Optional[str] = None,
        *,
        timeout: float = 6.0,
        directory_repo: Optional[DirectoryRepository] = None,
    ) -> None:
        default_map = "http://medicagent-core-service:8080/v1/maps"
        fallback_map = "http://localhost:8083/v1/maps"
        configured_map = map_base_url or os.getenv("MAP_SERVICE_URL") or default_map
        self._map_base_url = (configured_map or fallback_map).rstrip("/")
        self._timeout = timeout
        self._shortest_path_endpoint = f"{self._map_base_url}/shortest-path"
        self._default_map_name = os.getenv("MAP_DEFAULT_NAME", "bvdl_v1")
        try:
            self._default_kiosk_id = int(os.getenv("MAP_DEFAULT_KIOSK_ID", "1"))
        except ValueError:
            self._default_kiosk_id = 1
        if directory_repo is not None:
            self._directory_repo = directory_repo
        elif directory_base_url:
            self._directory_repo = DirectoryRepository(base_url=directory_base_url)
        else:
            self._directory_repo = get_directory_repository()
        self._kiosk_cache: Dict[int, Dict[str, Any]] = {}

    def get_route(
        self,
        slots: Dict[str, Any],
        *,
        hospital_id: Optional[str] = None,
        kiosk_id: Optional[int] = None,
        map_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        logger.debug("Handling get_route service call with slots=%s", slots)
        destination = str(slots.get("to_poi") or "").strip()
        if not destination:
            raise ValueError("Destination (to_poi) is required for route lookup")

        start = str(slots.get("from_poi") or "").strip()
        resolved_kiosk_id = int(kiosk_id or self._default_kiosk_id)
        kiosk_info: Optional[Dict[str, Any]] = None
        if not start or not hospital_id:
            kiosk_info = self._kiosk_cache.get(resolved_kiosk_id)
            if kiosk_info is None:
                kiosk_info = self._directory_repo.get_kiosk_info(resolved_kiosk_id)
                if kiosk_info:
                    self._kiosk_cache[resolved_kiosk_id] = kiosk_info
        if not start:
            start = str((kiosk_info or {}).get("location") or "KIOSK")
            logger.debug("Resolved start location from kiosk: %s", start)

        resolved_hospital_id = hospital_id or slots.get("hospital_id")
        if not resolved_hospital_id and kiosk_info:
            resolved_hospital_id = (
                kiosk_info.get("hospital_id")
                or ((kiosk_info.get("hospital") or {}).get("hospital_id"))
            )
        try:
            hospital_id_int = int(str(resolved_hospital_id))
        except (TypeError, ValueError):
            raise ValueError("Hospital ID is required for route lookup") from None

        resolved_map_name = str(
            map_name
            or slots.get("map_name")
            or self._default_map_name
        ).strip() or self._default_map_name
        logger.debug("Resolved map name: %s", resolved_map_name)

        payload = {
            "map_name": resolved_map_name,
            "start": start,
            "end": destination,
            "hospital_id": hospital_id_int,
        }

        try:
            response = requests.post(self._shortest_path_endpoint, json=payload, timeout=self._timeout)
            response.raise_for_status()
            data = response.json()
            logger.info(
                "MAP: shortest path ok map=%s start=%s end=%s",
                resolved_map_name,
                start,
                destination,
            )
            if isinstance(data, dict):
                return data
            logger.warning("MAP: unexpected response format from shortest path endpoint")
        except requests.HTTPError as http_err:
            status = http_err.response.status_code if http_err.response else "unknown"
            logger.warning(
                "MAP: shortest path HTTP %s payload=%s", status, payload
            )
        except requests.RequestException as exc:
            logger.warning("MAP: shortest path request failed payload=%s err=%s", payload, exc)
        except ValueError as exc:
            logger.warning("MAP: invalid JSON from shortest path endpoint err=%s", exc)

        logger.info("MAP: falling back to static route for start=%s end=%s", start, destination)
        return {
            "ok": False,
            "start": start,
            "end": destination,
            "direction_text": "Hiện chưa có dữ liệu tuyến đường chi tiết.",
        }
