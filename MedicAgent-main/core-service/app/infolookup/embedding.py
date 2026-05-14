from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, TYPE_CHECKING
from uuid import NAMESPACE_URL, uuid5

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.servicelogs.servicelogger import logger

if TYPE_CHECKING:  # pragma: no cover
    from app.infolookup.repository import KnowledgeEntry


class SemanticSearcher:
    def __init__(self) -> None:
        self.enabled = bool(settings.QDRANT_ENABLED)
        self.collection = settings.QDRANT_COLLECTION
        self._client: Optional[QdrantClient] = None
        self._model: Optional[SentenceTransformer] = None
        self._dim: Optional[int] = None

        if not self.enabled:
            logger.info("Semantic search disabled via configuration.")
            return

        try:
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            self._dim = int(self._model.get_sentence_embedding_dimension())
            self._client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                api_key=settings.QDRANT_API_KEY,
            )
            self._ensure_collection()
            logger.info(
                "Semantic search enabled using model=%s collection=%s",
                settings.EMBEDDING_MODEL_NAME,
                self.collection,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to initialise semantic search: %s", exc, exc_info=True)
            self.enabled = False
            self._client = None
            self._model = None
            self._dim = None

    def _ensure_collection(self) -> None:
        assert self._client is not None
        assert self._dim is not None
        try:
            self._client.recreate_collection(
                collection_name=self.collection,
                vectors_config=qmodels.VectorParams(
                    size=self._dim,
                    distance=qmodels.Distance.COSINE,
                ),
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to recreate Qdrant collection: %s", exc)
            raise

    def index(self, entries: Sequence["KnowledgeEntry"]) -> None:
        if not self.enabled:
            return
        if not entries:
            return
        if self._client is None or self._model is None:
            return

        logger.info("Indexing %d knowledge entries into Qdrant", len(entries))

        batch_size = 64
        for start in range(0, len(entries), batch_size):
            batch = entries[start : start + batch_size]
            documents: List[tuple["KnowledgeEntry", str, str]] = []
            for entry in batch:
                paragraph_text = (entry.text or "").strip()
                if paragraph_text:
                    documents.append((entry, "paragraph", paragraph_text))
                if entry.qas:
                    qa_text = " ".join(q.strip() for q in entry.qas if q.strip())
                    if qa_text:
                        documents.append((entry, "qa", qa_text))

            if not documents:
                continue

            vectors = self._encode([doc[2] for doc in documents])

            points: List[qmodels.PointStruct] = []
            for (entry, source, _), vector in zip(documents, vectors):
                payload = {
                    "entry_id": entry.entry_id,
                    "doc_id": entry.doc_id,
                    "topic": entry.topic,
                    "hospital_id": entry.hospital_id,
                    "source": source,
                }
                point_id = self._build_point_id(entry.entry_id, source)
                point = qmodels.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
                points.append(point)

            try:
                self._client.upsert(collection_name=self.collection, points=points)
            except Exception as exc:  # pragma: no cover - defensive
                logger.error("Failed to upsert points batch into Qdrant: %s", exc)
                continue

    def search(
        self,
        question: str,
        *,
        topic: Optional[str],
        hospital_id: Optional[str],
        limit: int,
    ) -> List[tuple[str, float, str]]:
        if not self.enabled or not question.strip():
            return []
        if self._client is None or self._model is None:
            return []

        vector = self._encode([question])[0]
        query_filter = self._build_filter(topic=topic, hospital_id=hospital_id)

        try:
            hits = self._client.search(
                collection_name=self.collection,
                query_vector=vector,
                limit=limit,
                with_payload=True,
                query_filter=query_filter,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Semantic search error: %s", exc)
            return []

        results: List[tuple[str, float, str]] = []
        for hit in hits:
            payload = hit.payload or {}
            entry_id = payload.get("entry_id")
            if not entry_id:
                continue
            source = payload.get("source") or "paragraph"
            results.append((entry_id, float(hit.score or 0.0), source))
        return results

    @staticmethod
    def _build_point_id(entry_id: str, source: str) -> str:
        token = f"{entry_id}|{source}"
        return str(uuid5(NAMESPACE_URL, token))

    def _encode(self, texts: Iterable[str]) -> List[List[float]]:
        assert self._model is not None
        embeddings = self._model.encode(
            list(texts),
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        if isinstance(embeddings, np.ndarray):
            return embeddings.astype(float).tolist()
        return [list(vec) for vec in embeddings]

    def _build_filter(
        self,
        *,
        topic: Optional[str],
        hospital_id: Optional[str],
    ) -> Optional[qmodels.Filter]:
        must: List[qmodels.FieldCondition] = []
        if topic:
            must.append(
                qmodels.FieldCondition(
                    key="topic",
                    match=qmodels.MatchValue(value=topic),
                )
            )
        if hospital_id:
            must.append(
                qmodels.FieldCondition(
                    key="hospital_id",
                    match=qmodels.MatchValue(value=hospital_id),
                )
            )
        if not must:
            return None
        return qmodels.Filter(must=must)


# Avoid runtime circular imports; type-only imports handled above.
