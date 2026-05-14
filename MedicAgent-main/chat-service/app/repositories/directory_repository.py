import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

import requests

from ..servicelogs.servicelogger import logger
from ..services.textnorm import normalize_vi


class DirectoryRepository:
    def __init__(self, base_url: Optional[str] = None, *, timeout: float = 5.0) -> None:
        self._base_urls = self._init_base_urls(base_url)
        self._timeout = timeout
        self._syndrome_mapping_cache: Dict[str, List[Dict[str, Any]]] = {}

    @staticmethod
    def _init_base_urls(configured: Optional[str]) -> List[str]:
        candidates = [
            configured or "",
            os.getenv("DIRECTORY_SERVICE_URL", ""),
            "http://medicagent-core-service:8080/v1/directory",
            "http://medicagent-gateway:8000/v1/directory",
            "http://localhost:8083/v1/directory",
        ]
        normalized: List[str] = []
        for url in candidates:
            trimmed = (url or "").strip()
            if not trimmed:
                continue
            normalized_url = trimmed.rstrip("/")
            if normalized_url not in normalized:
                normalized.append(normalized_url)
        return normalized

    def get_departments_name(self, hospital_id: str) -> List[Dict[str, Any]]:
        path = f"/hospitals/{hospital_id}/departments/simple"
        for base in self._base_urls:
            url = f"{base}{path}"
            try:
                response = requests.get(url, timeout=self._timeout)
                response.raise_for_status()
                departments = self._normalize_department_payload(response.json())
                if departments is not None:
                    filtered = [
                        {"department_id": dept.get("department_id"), "name": dept.get("name")}
                        for dept in departments
                        if isinstance(dept, dict) and dept.get("department_id") is not None and dept.get("name")
                    ]
                    logger.info("DIRECTORY: fetched %s departments from %s", len(filtered), url)
                    logger.debug("Departments fetched: %s", filtered)
                    return filtered
            except requests.HTTPError as http_err:
                status = http_err.response.status_code if http_err.response else "unknown"
                logger.warning("DIRECTORY: HTTP %s when requesting %s", status, url)
            except requests.RequestException as exc:
                logger.warning("DIRECTORY: request to %s failed (%s)", url, exc)
            except ValueError as exc:
                logger.warning("DIRECTORY: invalid JSON from %s (%s)", url, exc)
        logger.error("DIRECTORY: unable to fetch departments for hospital %s", hospital_id)
        return []

    def get_departments_full(self, hospital_id: str) -> List[Dict[str, Any]]:
        path = f"/hospitals/{hospital_id}/departments"
        for base in self._base_urls:
            url = f"{base}{path}"
            try:
                response = requests.get(url, timeout=self._timeout)
                response.raise_for_status()
                departments = self._normalize_department_payload(response.json())
                if departments is not None:
                    logger.info(
                        "DIRECTORY: fetched %s detailed departments from %s",
                        len(departments),
                        url,
                    )
                    return departments
            except requests.HTTPError as http_err:
                status = http_err.response.status_code if http_err.response else "unknown"
                logger.warning("DIRECTORY: HTTP %s when requesting %s", status, url)
            except requests.RequestException as exc:
                logger.warning("DIRECTORY: request to %s failed (%s)", url, exc)
            except ValueError as exc:
                logger.warning("DIRECTORY: invalid JSON from %s (%s)", url, exc)
        logger.error("DIRECTORY: unable to fetch detailed departments for hospital %s", hospital_id)
        return []

    def get_departments_hint(self, hospital_id: str) -> List[Tuple[str, str]]:
        path = f"/hospitals/{hospital_id}/departments/simple"
        for base in self._base_urls:
            url = f"{base}{path}"
            try:
                response = requests.get(url, timeout=self._timeout)
                response.raise_for_status()
                departments = self._normalize_department_payload(response.json())
                if departments is None:
                    continue
                results: List[Tuple[str, str]] = []
                seen: set[Tuple[str, str]] = set()
                for dept in departments:
                    if not isinstance(dept, dict):
                        continue
                    department_id = dept.get("department_id")
                    raw_hint = dept.get("hint")
                    if department_id is None or not raw_hint:
                        continue
                    department_id_str = str(department_id)
                    segments: List[str] = []
                    if isinstance(raw_hint, str):
                        cleaned_hint = raw_hint.replace("\n", " // ")
                        segments.extend(piece.strip() for piece in cleaned_hint.split("//"))
                    elif isinstance(raw_hint, (list, tuple, set)):
                        for item in raw_hint:
                            if isinstance(item, str):
                                cleaned_item = item.replace("\n", " // ")
                                segments.extend(piece.strip() for piece in cleaned_item.split("//"))
                    for segment in segments:
                        normalized = normalize_vi(segment)
                        if not normalized:
                            continue
                        key = (normalized, department_id_str)
                        if key in seen:
                            continue
                        seen.add(key)
                        results.append(key)
                if results:
                    logger.info("DIRECTORY: fetched %s department hints from %s", len(results), url)
                    return results
            except requests.HTTPError as http_err:
                status = http_err.response.status_code if http_err.response else "unknown"
                logger.warning("DIRECTORY: HTTP %s when requesting %s", status, url)
            except requests.RequestException as exc:
                logger.warning("DIRECTORY: request to %s failed (%s)", url, exc)
            except ValueError as exc:
                logger.warning("DIRECTORY: invalid JSON from %s (%s)", url, exc)
        logger.error("DIRECTORY: unable to fetch department hints for hospital %s", hospital_id)
        return []

    def search_zones_by_department_name(self, hospital_id: str, name: str) -> List[Dict[str, Any]]:
        path = "/search/zones/by-department"
        params = {"hospital_id": hospital_id, "name": name}
        for base in self._base_urls:
            url = f"{base}{path}"
            try:
                response = requests.get(url, params=params, timeout=self._timeout)
                response.raise_for_status()
                zones = response.json()
                if isinstance(zones, list):
                    filtered = [
                        {"zone_id": zone.get("zone_id"), "name": zone.get("name")}
                        for zone in zones
                        if isinstance(zone, dict)
                        and zone.get("zone_id") is not None
                        and zone.get("name")
                    ]
                    logger.info(
                        "DIRECTORY: fetched %s zones for department=%s from %s",
                        len(filtered),
                        name,
                        url,
                    )
                    return filtered
            except requests.HTTPError as http_err:
                status = http_err.response.status_code if http_err.response else "unknown"
                logger.warning("DIRECTORY: zone search HTTP %s when requesting %s", status, url)
            except requests.RequestException as exc:
                logger.warning("DIRECTORY: zone search request to %s failed (%s)", url, exc)
            except ValueError as exc:
                logger.warning("DIRECTORY: zone search invalid JSON from %s (%s)", url, exc)
        logger.error(
            "DIRECTORY: unable to fetch zones for department=%s hospital=%s",
            name,
            hospital_id,
        )
        return []

    def get_service_packages_name(self, hospital_id: str) -> List[Dict[str, Any]]:
        path = f"/hospitals/{hospital_id}/service-packages"
        for base in self._base_urls:
            url = f"{base}{path}"
            try:
                response = requests.get(url, timeout=self._timeout)
                response.raise_for_status()
                packages = self._normalize_service_package_payload(response.json())
                if packages is not None:
                    filtered = [
                        {
                            "service_package_id": pkg.get("service_package_id"),
                            "name": pkg.get("name"),
                            "is_bhyt_applicable": pkg.get("is_bhyt_applicable"),
                        }
                        for pkg in packages
                        if isinstance(pkg, dict)
                        and pkg.get("service_package_id") is not None
                        and pkg.get("name")
                    ]
                    logger.info("DIRECTORY: fetched %s service packages from %s", len(filtered), url)
                    return filtered
            except requests.HTTPError as http_err:
                status = http_err.response.status_code if http_err.response else "unknown"
                logger.warning("DIRECTORY: HTTP %s when requesting %s", status, url)
            except requests.RequestException as exc:
                logger.warning("DIRECTORY: request to %s failed (%s)", url, exc)
            except ValueError as exc:
                logger.warning("DIRECTORY: invalid JSON from %s (%s)", url, exc)
        logger.error("DIRECTORY: unable to fetch service packages for hospital %s", hospital_id)
        return []

    def get_kiosk_info(self, kiosk_id: int | str) -> Optional[Dict[str, Any]]:
        path = f"/kiosks/{kiosk_id}/info"
        for base in self._base_urls:
            url = f"{base}{path}"
            try:
                response = requests.get(url, timeout=self._timeout)
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict):
                    logger.info("DIRECTORY: fetched kiosk info id=%s from %s", kiosk_id, url)
                    return data
            except requests.HTTPError as http_err:
                status = http_err.response.status_code if http_err.response else "unknown"
                logger.warning("DIRECTORY: kiosk info HTTP %s when requesting %s", status, url)
            except requests.RequestException as exc:
                logger.warning("DIRECTORY: kiosk info request to %s failed (%s)", url, exc)
            except ValueError as exc:
                logger.warning("DIRECTORY: kiosk info invalid JSON from %s (%s)", url, exc)
        logger.error("DIRECTORY: unable to fetch kiosk info for kiosk_id %s", kiosk_id)
        return None

    def get_service_packages_hint(self, hospital_id: str) -> List[Tuple[str, str]]:
        path = f"/hospitals/{hospital_id}/service-packages"
        for base in self._base_urls:
            url = f"{base}{path}"
            try:
                response = requests.get(url, timeout=self._timeout)
                response.raise_for_status()
                packages = self._normalize_service_package_payload(response.json())
                if packages is None:
                    continue
                results: List[Tuple[str, str]] = []
                seen: set[Tuple[str, str]] = set()
                for pkg in packages:
                    if not isinstance(pkg, dict):
                        continue
                    package_id = pkg.get("service_package_id")
                    raw_hint = pkg.get("hint")
                    if package_id is None or not raw_hint:
                        continue
                    package_id_str = str(package_id)
                    segments: List[str] = []
                    if isinstance(raw_hint, str):
                        cleaned_hint = raw_hint.replace("\n", " // ")
                        segments.extend(piece.strip() for piece in cleaned_hint.split("//"))
                    elif isinstance(raw_hint, (list, tuple, set)):
                        for item in raw_hint:
                            if isinstance(item, str):
                                cleaned_item = item.replace("\n", " // ")
                                segments.extend(piece.strip() for piece in cleaned_item.split("//"))
                    for segment in segments:
                        normalized = normalize_vi(segment)
                        if not normalized:
                            continue
                        key = (normalized, package_id_str)
                        if key in seen:
                            continue
                        seen.add(key)
                        results.append(key)
                if results:
                    logger.info("DIRECTORY: fetched %s service package hints from %s", len(results), url)
                    return results
            except requests.HTTPError as http_err:
                status = http_err.response.status_code if http_err.response else "unknown"
                logger.warning("DIRECTORY: HTTP %s when requesting %s", status, url)
            except requests.RequestException as exc:
                logger.warning("DIRECTORY: request to %s failed (%s)", url, exc)
            except ValueError as exc:
                logger.warning("DIRECTORY: invalid JSON from %s (%s)", url, exc)
        logger.error("DIRECTORY: unable to fetch service package hints for hospital %s", hospital_id)
        return []

    def get_departments_by_service_package(
        self, hospital_id: str, service_package_id: str
    ) -> List[Dict[str, Any]]:
        path = f"/hospitals/{hospital_id}/service-packages/{service_package_id}/departments"
        for base in self._base_urls:
            url = f"{base}{path}"
            try:
                response = requests.get(url, timeout=self._timeout)
                response.raise_for_status()
                departments = self._normalize_department_payload(response.json())
                if departments is not None:
                    filtered = [
                        {
                            "department_id": dept.get("department_id"),
                            "name": dept.get("name"),
                            "hint": dept.get("hint"),
                        }
                        for dept in departments
                        if isinstance(dept, dict)
                        and dept.get("department_id") is not None
                        and dept.get("name")
                    ]
                    logger.info(
                        "DIRECTORY: fetched %s departments for hospital=%s, package=%s from %s",
                        len(filtered),
                        hospital_id,
                        service_package_id,
                        url,
                    )
                    logger.debug("Departments fetched by service package: %s", filtered)
                    return filtered
            except requests.HTTPError as http_err:
                status = http_err.response.status_code if http_err.response else "unknown"
                logger.warning("DIRECTORY: HTTP %s when requesting %s", status, url)
            except requests.RequestException as exc:
                logger.warning("DIRECTORY: request to %s failed (%s)", url, exc)
            except ValueError as exc:
                logger.warning("DIRECTORY: invalid JSON from %s (%s)", url, exc)
        logger.error(
            "DIRECTORY: unable to fetch departments for hospital=%s service_package=%s",
            hospital_id,
            service_package_id,
        )
        return []

    def get_service_packages_by_department(self, department_id: str) -> List[Dict[str, Any]]:
        path = f"/departments/{department_id}/service-packages"
        for base in self._base_urls:
            url = f"{base}{path}"
            try:
                response = requests.get(url, timeout=self._timeout)
                response.raise_for_status()
                packages = self._normalize_service_package_payload(response.json())
                if packages is not None:
                    filtered = [
                        {
                            "service_package_id": pkg.get("service_package_id"),
                            "name": pkg.get("name"),
                            "is_bhyt_applicable": pkg.get("is_bhyt_applicable"),
                            "hint": pkg.get("hint"),
                            "status": pkg.get("status"),
                        }
                        for pkg in packages
                        if isinstance(pkg, dict)
                        and pkg.get("service_package_id") is not None
                        and pkg.get("name")
                    ]
                    logger.info(
                        "DIRECTORY: fetched %s service packages for department=%s from %s",
                        len(filtered),
                        department_id,
                        url,
                    )
                    logger.debug(
                        "Service packages fetched by department %s: %s", department_id, filtered
                    )
                    return filtered
            except requests.HTTPError as http_err:
                status = http_err.response.status_code if http_err.response else "unknown"
                logger.warning("DIRECTORY: HTTP %s when requesting %s", status, url)
            except requests.RequestException as exc:
                logger.warning("DIRECTORY: request to %s failed (%s)", url, exc)
            except ValueError as exc:
                logger.warning("DIRECTORY: invalid JSON from %s (%s)", url, exc)
        logger.error(
            "DIRECTORY: unable to fetch service packages for department %s", department_id
        )
        return []
    
    def get_emergency_info(self, hostipal_id) -> Dict[str, Any]:
        return { "hostipal_id" : hostipal_id,
                 "Department": "Phòng cấp cứu",
                 "Location": "Tầng trệt, Sảnh chính"}

    def get_syndrome_triage_mappings(self, hospital_id: str) -> List[Dict[str, Any]]:
        cached = self._syndrome_mapping_cache.get(hospital_id)
        if cached is not None:
            return cached

        path = f"/hospitals/{hospital_id}/triage/syndrome-mappings"
        for base in self._base_urls:
            url = f"{base}{path}"
            try:
                response = requests.get(url, timeout=self._timeout)
                response.raise_for_status()
                mappings = self._normalize_syndrome_mapping_payload(response.json())
                if mappings is not None:
                    self._syndrome_mapping_cache[hospital_id] = mappings
                    logger.info(
                        "DIRECTORY: fetched %s syndrome mappings from %s",
                        len(mappings),
                        url,
                    )
                    logger.debug("Syndrome mappings fetched: %s", mappings)
                    return mappings
            except requests.HTTPError as http_err:
                status = http_err.response.status_code if http_err.response else "unknown"
                logger.warning("DIRECTORY: HTTP %s when requesting %s", status, url)
            except requests.RequestException as exc:
                logger.warning("DIRECTORY: request to %s failed (%s)", url, exc)
            except ValueError as exc:
                logger.warning("DIRECTORY: invalid JSON from %s (%s)", url, exc)

        logger.error("DIRECTORY: unable to fetch syndrome mappings for hospital %s", hospital_id)
        self._syndrome_mapping_cache[hospital_id] = []
        return []

    @staticmethod
    def _normalize_department_payload(payload: Any) -> Optional[List[Dict[str, Any]]]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            data = payload.get("data")
            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict)]
            return [payload] if payload else []
        return None

    @staticmethod
    def _normalize_service_package_payload(payload: Any) -> Optional[List[Dict[str, Any]]]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            data = payload.get("data")
            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict)]
            return [payload] if payload else []
        return None

    @staticmethod
    def _normalize_syndrome_mapping_payload(payload: Any) -> Optional[List[Dict[str, Any]]]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            data = payload.get("data")
            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict)]
            return [payload] if payload else []
        return None


@lru_cache(maxsize=1)
def get_directory_repository() -> DirectoryRepository:
    return DirectoryRepository()
