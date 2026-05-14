import json
import logging
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import numpy as np

try:
    import faiss  # type: ignore
except ImportError:  # pragma: no cover - handled at runtime
    faiss = None  # type: ignore

from sqlalchemy.orm import Session

from app.embeddings.model_provider import get_model
from app.directory import models

logger = logging.getLogger(__name__)


DEFAULT_INDEX_PATH = Path(__file__).resolve().parents[2] / "data" / "indexes" / "service-faiss.index"
DEFAULT_METADATA_PATH = Path(__file__).resolve().parents[2] / "data" / "indexes" / "service-metadata.json"


def _ensure_paths(index_path: Path, metadata_path: Path):
    index_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)


def _normalize(vecs: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-10
    return vecs / norms


def build_index(
    db: Session,
    index_path: Path = DEFAULT_INDEX_PATH,
    metadata_path: Path = DEFAULT_METADATA_PATH,
    hospital_id: Optional[int] = None,
) -> Tuple[int, Path, Path]:
    """
    Embed all active services and build a FAISS index.
    """
    if faiss is None:
        raise RuntimeError("faiss is not installed. Please install faiss-cpu.")

    query = db.query(models.Service).filter(models.Service.status == 1)
    if hospital_id is not None:
        query = query.filter(models.Service.hospital_id == hospital_id)
    services = query.options().all()
    if not services:
        raise ValueError("No services found to index.")

    model = get_model()
    texts: List[str] = []
    metadata: List[dict] = []

    for svc in services:
        cat_names = [c.name for c in svc.categories] if svc.categories else []
        text_parts = [svc.name or "", svc.aliases or "", " ".join(cat_names)]
        text = " | ".join(p for p in text_parts if p)
        texts.append(text)
        metadata.append(
            {
                "service_id": svc.service_id,
                "hospital_id": svc.hospital_id,
                "code": svc.code,
                "name": svc.name,
                "categories": cat_names,
            }
        )

    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    dim = embeddings.shape[1]

    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype("float32"))

    _ensure_paths(index_path, metadata_path)
    faiss.write_index(index, str(index_path))
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")

    logger.info("Built service index: %d vectors -> %s", len(metadata), index_path)
    return len(metadata), index_path, metadata_path


class ServiceIndex:
    def __init__(self, index_path: Path = DEFAULT_INDEX_PATH, metadata_path: Path = DEFAULT_METADATA_PATH):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata: List[dict] = []

    def load(self):
        if faiss is None:
            raise RuntimeError("faiss is not installed. Please install faiss-cpu.")
        if not self.index_path.exists() or not self.metadata_path.exists():
            raise FileNotFoundError(f"Index or metadata not found: {self.index_path}, {self.metadata_path}")
        self.index = faiss.read_index(str(self.index_path))
        self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))

    def is_ready(self) -> bool:
        return (
            faiss is not None
            and self.index_path.exists()
            and self.metadata_path.exists()
        )

    def search(
        self,
        query: str,
        hospital_id: int,
        top_k: int = 5,
        overfetch: int = 20,
    ) -> List[dict]:
        if not self.is_ready():
            return []
        if self.index is None or not self.metadata:
            self.load()

        model = get_model()
        vec = model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        k = min(max(top_k, overfetch), len(self.metadata))
        scores, indices = self.index.search(vec, k)
        results: List[dict] = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]
            if meta.get("hospital_id") != hospital_id:
                continue
            results.append({**meta, "score": float(score)})
            if len(results) >= top_k:
                break
        return results


service_index = ServiceIndex()
