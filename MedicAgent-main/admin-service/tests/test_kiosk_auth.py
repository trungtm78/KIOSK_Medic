"""Wedge 4.2 - Per-kiosk token auth (CSO Finding #2).

Test the core token primitives: generate, hash, verify, prefix matching.
"""

import pytest

from app.core.kiosk_auth import (
    generate_token,
    hash_token,
    verify_token,
    extract_prefix,
)


def test_generate_token_has_kt_prefix():
    token = generate_token()
    assert token.startswith("kt_"), f"token must start with 'kt_' for identification: {token}"


def test_generate_token_has_sufficient_entropy():
    """At least 32 chars (without prefix) for ~190 bits of entropy."""
    token = generate_token()
    assert len(token) >= 35, f"token too short: {len(token)} chars"


def test_generate_token_is_unique():
    tokens = {generate_token() for _ in range(100)}
    assert len(tokens) == 100, "generate_token must produce unique values"


def test_hash_token_returns_non_raw():
    token = generate_token()
    hashed = hash_token(token)
    assert hashed != token, "hash must not equal raw token"
    assert hashed.startswith("$2"), f"bcrypt hash expected, got: {hashed[:10]}"


def test_verify_token_accepts_correct_token():
    token = generate_token()
    hashed = hash_token(token)
    assert verify_token(token, hashed) is True


def test_verify_token_rejects_wrong_token():
    token = generate_token()
    hashed = hash_token(token)
    assert verify_token("kt_wrong_token_string_here_xxx", hashed) is False


def test_verify_token_rejects_garbage_hash():
    """Don't crash on malformed hash - return False."""
    token = generate_token()
    assert verify_token(token, "not-a-valid-bcrypt-hash") is False


def test_extract_prefix_returns_first_12_chars():
    token = "kt_a1b2c3d4e5f6g7h8"
    assert extract_prefix(token) == "kt_a1b2c3d4e"


def test_extract_prefix_handles_short_tokens():
    """Edge case: should not crash on short input."""
    assert extract_prefix("kt_ab") == "kt_ab"
