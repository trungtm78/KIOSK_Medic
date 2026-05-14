from __future__ import annotations

import sys
from pathlib import Path


def _ensure_app_on_path() -> None:
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.append(str(root))


def test_lookup_returns_snippet_for_insurance_policy():
    _ensure_app_on_path()
    from app.infolookup.schemas import InfoLookupRequest
    from app.infolookup.service import InfoLookupService

    svc = InfoLookupService()
    payload = InfoLookupRequest(
        question="BHYT chi trả bao nhiêu phần trăm chi phí khám bệnh?",
        topic="insurance_policy",
        max_results=1,
    )

    response = svc.lookup(payload)

    assert response.results, "Expected at least one snippet to be returned"
    snippet = response.results[0]
    assert snippet.doc_id in {"nghidinh_188_2025", "luat_bhyt"}
    assert "chi trả" in snippet.text.lower()
    assert snippet.score > 0.0
