from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


DEFAULT_MODEL_ID = "hynt/Zipformer-30M-RNNT-6000h"
DEFAULT_CACHE_ROOT = Path(__file__).resolve().parents[2] / "model_cache" / "zipformer"
DEFAULT_PROVIDER = "cpu"
DEFAULT_NUM_THREADS = 1
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_FEATURE_DIM = 80
DEFAULT_DECODING_METHOD = "greedy_search"
DEFAULT_HOTWORDS_SCORE = 1.5


@dataclass(slots=True)
class ZipformerSettings:
    """Runtime configuration for the Zipformer service."""

    model_id: str = field(default=DEFAULT_MODEL_ID)
    revision: Optional[str] = field(default=None)
    cache_root: Path = field(default_factory=lambda: DEFAULT_CACHE_ROOT)
    provider: str = field(default=DEFAULT_PROVIDER)
    num_threads: int = field(default=DEFAULT_NUM_THREADS)
    sample_rate: int = field(default=DEFAULT_SAMPLE_RATE)
    feature_dim: int = field(default=DEFAULT_FEATURE_DIM)
    decoding_method: str = field(default=DEFAULT_DECODING_METHOD)
    use_int8: bool = field(default=False)
    hotwords_file: Optional[Path] = field(default=None)
    hotwords_score: float = field(default=DEFAULT_HOTWORDS_SCORE)

    def __post_init__(self) -> None:
        self.cache_root = Path(self.cache_root)
        if self.hotwords_file is not None:
            self.hotwords_file = Path(self.hotwords_file)

    @classmethod
    def from_env(cls) -> "ZipformerSettings":
        cache_override = os.getenv("ZIPFORMER_CACHE_DIR")
        hotwords = os.getenv("ZIPFORMER_HOTWORDS_FILE")

        return cls(
            model_id=os.getenv("ZIPFORMER_MODEL_ID", DEFAULT_MODEL_ID),
            revision=os.getenv("ZIPFORMER_REVISION") or None,
            cache_root=Path(cache_override) if cache_override else DEFAULT_CACHE_ROOT,
            provider=os.getenv("ZIPFORMER_PROVIDER", DEFAULT_PROVIDER),
            num_threads=int(os.getenv("ZIPFORMER_NUM_THREADS", str(DEFAULT_NUM_THREADS))),
            sample_rate=int(os.getenv("ZIPFORMER_SAMPLE_RATE", str(DEFAULT_SAMPLE_RATE))),
            feature_dim=int(os.getenv("ZIPFORMER_FEATURE_DIM", str(DEFAULT_FEATURE_DIM))),
            decoding_method=os.getenv("ZIPFORMER_DECODING_METHOD", DEFAULT_DECODING_METHOD),
            use_int8=_parse_bool(os.getenv("ZIPFORMER_USE_INT8"), default=False),
            hotwords_file=Path(hotwords) if hotwords else None,
            hotwords_score=float(os.getenv("ZIPFORMER_HOTWORDS_SCORE", str(DEFAULT_HOTWORDS_SCORE))),
        )

    @property
    def model_dir(self) -> Path:
        target = self.cache_root / self.model_id.replace("/", "__")
        target.mkdir(parents=True, exist_ok=True)
        return target

    def model_filenames(self) -> dict[str, str]:
        suffix = ".int8.onnx" if self.use_int8 else ".onnx"
        base = "epoch-20-avg-10"
        return {
            "encoder": f"encoder-{base}{suffix}",
            "decoder": f"decoder-{base}{suffix}",
            "joiner": f"joiner-{base}{suffix}",
            "tokens": "config.json",
        }
