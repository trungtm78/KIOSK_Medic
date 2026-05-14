# app/services/textnorm.py
import unicodedata, re

_ws = re.compile(r"\s+")


def strip_accents(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def normalize(s: str) -> str:
    return _ws.sub(" ", s.lower().strip())


def normalize_vi(s: str) -> str:
    return normalize(strip_accents(s)).replace("đ", "d")


def canon_label(*parts: str) -> str:
    return normalize_vi(" ".join(p for p in parts if p))

