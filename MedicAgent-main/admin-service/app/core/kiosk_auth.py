"""Per-kiosk token auth primitives (CSO Finding #2 fix).

Tokens are opaque strings prefixed with `kt_`. They are stored as bcrypt
hashes with the first 12 chars (`token_prefix`) kept in clear for fast
lookup before bcrypt comparison.

Usage:
    raw = generate_token()           # 'kt_abc123def456...'
    hashed = hash_token(raw)         # '$2b$12$...'
    prefix = extract_prefix(raw)     # 'kt_abc123de'
    # store (prefix, hashed) in DB; return raw to admin ONCE

Verification:
    rows = db.query(KioskToken).filter(prefix=extract_prefix(received)).all()
    for row in rows:
        if verify_token(received, row.token_hash):
            return row  # authenticated

bcrypt is intentionally slow; verification cost is bounded by token_prefix
hits (typically 1 per prefix collision).

FastAPI usage:
    from app.core.kiosk_auth import verify_kiosk_token_dependency, KioskAuth

    @router.get("/protected")
    def endpoint(principal: KioskAuth):
        return {"tenant": principal.tenant_id}
"""

import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Optional

import bcrypt
from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session, select

_TOKEN_PREFIX = "kt_"
_RAW_BYTES = 24  # 24 bytes -> ~32 chars urlsafe; total token ~35 chars
_BCRYPT_ROUNDS = 12  # 2^12 iterations - ~250ms on modern CPU


def generate_token() -> str:
    """Cryptographically random opaque token, ~190 bits of entropy."""
    return _TOKEN_PREFIX + secrets.token_urlsafe(_RAW_BYTES)


def hash_token(raw: str) -> str:
    """Bcrypt hash of the raw token. Use for DB storage."""
    return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)).decode(
        "utf-8"
    )


def verify_token(raw: str, hashed: str) -> bool:
    """Constant-time comparison via bcrypt. Returns False on any error.

    Never raises - malformed hashes return False so attackers can't probe
    storage state via error oracle.
    """
    try:
        return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def extract_prefix(raw: str, length: int = 12) -> str:
    """First N chars of token - stored separately as DB lookup key.

    Short tokens returned as-is (graceful handling of malformed input).
    """
    return raw[:length] if len(raw) >= length else raw


@dataclass
class KioskPrincipal:
    """Authenticated kiosk identity passed to route handlers."""

    tenant_id: int
    kiosk_name: str
    token_id: int
    scopes: list[str]


def verify_kiosk_token_dependency(
    x_kiosk_token: Annotated[Optional[str], Header()] = None,
) -> KioskPrincipal:
    """FastAPI dependency: validate X-Kiosk-Token header, return principal.

    Raises 401 if token missing/invalid/revoked/expired.
    """
    if not x_kiosk_token or not x_kiosk_token.startswith(_TOKEN_PREFIX):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed X-Kiosk-Token header",
        )

    # Import here to avoid circular imports at module load
    from app.core.db import get_engine
    from app.models import KioskToken

    prefix = extract_prefix(x_kiosk_token)
    now = datetime.utcnow()

    with Session(get_engine()) as db:
        candidates = db.exec(
            select(KioskToken).where(KioskToken.token_prefix == prefix)
        ).all()

        for row in candidates:
            if not verify_token(x_kiosk_token, row.token_hash):
                continue

            if row.revoked_at is not None:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, detail="Token revoked"
                )
            if row.expires_at is not None and row.expires_at < now:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, detail="Token expired"
                )

            # Update last_used_at (best-effort, do not fail auth if write fails)
            try:
                row.last_used_at = now
                db.add(row)
                db.commit()
            except Exception:
                pass

            return KioskPrincipal(
                tenant_id=row.tenant_id,
                kiosk_name=row.kiosk_name,
                token_id=row.id,
                scopes=[s.strip() for s in (row.scopes or "").split(",") if s.strip()],
            )

    raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


KioskAuth = Annotated[KioskPrincipal, Depends(verify_kiosk_token_dependency)]

