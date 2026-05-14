from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Sequence

import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


@dataclass
class IntentPrediction:
    label: str
    score: float
    probabilities: Dict[str, float]


class IntentClassifier:
    def __init__(
        self,
        model_dir: Optional[Path] = None,
        model_name: Optional[str] = None,
    ) -> None:
        project_default = Path(__file__).resolve().parents[2] / "models" / "intent_classifier"
        container_default = Path("/app/models/intent_classifier")
        fallback_dir = container_default if container_default.exists() else project_default
        base_dir = Path(os.getenv("INTENT_MODEL_DIR", fallback_dir))
        if not base_dir.exists():
            raise FileNotFoundError(f"Intent classifier directory not found: {base_dir}")

        self.config_path = base_dir / "config.json"
        self.classifier_path = base_dir / "intent_classifier.joblib"
        self.label_path = base_dir / "label_encoder.json"

        if not self.classifier_path.exists():
            raise FileNotFoundError(f"Classifier weights not found: {self.classifier_path}")
        if not self.label_path.exists():
            raise FileNotFoundError(f"Label encoder not found: {self.label_path}")

        self.config = {}
        if self.config_path.exists():
            self.config = json.loads(self.config_path.read_text(encoding="utf-8"))

        self.classes = json.loads(self.label_path.read_text(encoding="utf-8"))["classes"]
        self.label_to_index = {label: idx for idx, label in enumerate(self.classes)}

        self.classifier = joblib.load(self.classifier_path)

        name = model_name or self.config.get(
            "model_name", "AITeamVN/Vietnamese_Embedding"
        )
        self.encoder = self._load_encoder(name)

    def _load_encoder(self, model_name: str):
        try:
            return SentenceTransformer(model_name)
        except NotImplementedError as exc:
            if "meta tensor" not in str(exc).lower():
                raise
            logger.warning(
                "SentenceTransformer failed due to meta tensor issue, falling back to HF encoder: %s", exc
            )
            return _HFMeanPoolingEncoder(model_name)
        except (OSError, ValueError, RuntimeError, Exception) as exc:
            logger.warning(
                "SentenceTransformer failed to load model %s (%s). Falling back to HF encoder with slow tokenizer.",
                model_name,
                exc,
            )
            return _HFMeanPoolingEncoder(model_name)

    def predict(self, text: str) -> IntentPrediction:
        if not text or not text.strip():
            return IntentPrediction(label="unknown", score=0.0, probabilities={})

        embedding = self.encoder.encode([text], convert_to_numpy=True, normalize_embeddings=True)
        probs = self.classifier.predict_proba(embedding)[0]
        best_idx = int(np.argmax(probs))
        best_label = self.classes[best_idx]
        return IntentPrediction(
            label=best_label,
            score=float(probs[best_idx]),
            probabilities={label: float(probs[idx]) for idx, label in enumerate(self.classes)},
        )


@lru_cache(maxsize=1)
def get_intent_classifier() -> Optional[IntentClassifier]:
    """P2.1 - lru_cache replaces global singleton.

    Preserves negative caching behavior (Codex #6): if model file is missing,
    cache None so we don't retry expensive model load on every request.
    Tests call get_intent_classifier.cache_clear() to reset.
    """
    try:
        return IntentClassifier()
    except FileNotFoundError:
        return None


class _HFMeanPoolingEncoder:
    """Lightweight fallback encoder to avoid meta tensor failures."""

    def __init__(self, model_name: str, device: Optional[str] = None) -> None:
        import torch
        from transformers import AutoModel, AutoTokenizer

        self._torch = torch
        self.device = torch.device(device) if device else torch.device("cpu")
        # Some community models ship only slow tokenizers. Force use_fast=False to avoid crashes.
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

    def encode(
        self,
        texts: Sequence[str],
        convert_to_numpy: bool = True,
        normalize_embeddings: bool = False,
    ):
        torch = self._torch
        if isinstance(texts, str):
            texts = [texts]
        if not isinstance(texts, (list, tuple)):
            texts = list(texts)

        with torch.no_grad():
            features = self.tokenizer(
                list(texts),
                padding=True,
                truncation=True,
                return_tensors="pt",
            )
            features = {key: value.to(self.device) for key, value in features.items()}
            outputs = self.model(**features)
            token_embeddings = outputs.last_hidden_state
            attention_mask = features["attention_mask"].unsqueeze(-1).expand(token_embeddings.size()).float()
            summed = torch.sum(token_embeddings * attention_mask, dim=1)
            counts = attention_mask.sum(dim=1).clamp(min=1e-9)
            embeddings = summed / counts
            if normalize_embeddings:
                embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
            if convert_to_numpy:
                return embeddings.cpu().numpy()
            return embeddings
