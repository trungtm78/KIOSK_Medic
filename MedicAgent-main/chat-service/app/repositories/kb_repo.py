from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import KBDoc, KBChunk, KBEmbedding


class KBRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_doc(self, tenant_id: Optional[str], kind: str, title: str, source: Optional[str] = None) -> KBDoc:
        doc = KBDoc(tenant_id=tenant_id, kind=kind, title=title, source=source)
        self.session.add(doc)
        return doc

    def add_chunk(self, kb_doc_id: str, ordinal: int, content: str) -> KBChunk:
        chunk = KBChunk(kb_doc_id=kb_doc_id, ordinal=ordinal, content=content)
        self.session.add(chunk)
        return chunk

    def set_embedding(self, kb_chunk_id: str, embedding: list[float]) -> KBEmbedding:
        emb = self.session.get(KBEmbedding, kb_chunk_id)
        if emb is None:
            emb = KBEmbedding(kb_chunk_id=kb_chunk_id, embedding=embedding)
        else:
            emb.embedding = embedding
        self.session.add(emb)
        return emb

    def list_chunks(self, kb_doc_id: str) -> List[KBChunk]:
        stmt = select(KBChunk).where(KBChunk.kb_doc_id == kb_doc_id).order_by(KBChunk.ordinal.asc())
        return list(self.session.execute(stmt).scalars())

