from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, gen_uuid


UUID = String(36)


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    client_conversation_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    tenant_id: Mapped[Optional[str]] = mapped_column(UUID, nullable=True)
    channel: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    fsm_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    memory: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    started_at: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=False), server_default=func.now())
    ended_at: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=False), nullable=True)

    turns: Mapped[List["Turn"]] = relationship("Turn", back_populates="conversation", cascade="all, delete-orphan")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    transitions: Mapped[List["StateTransition"]] = relationship("StateTransition", back_populates="conversation", cascade="all, delete-orphan")
    handoff_sessions: Mapped[List["HandoffSession"]] = relationship("HandoffSession", back_populates="conversation", cascade="all, delete-orphan")


Index("ix_conversation_tenant_status", Conversation.tenant_id, Conversation.status)
Index("ix_conversation_started_at", Conversation.started_at)
Index("ix_conversation_client_id", Conversation.tenant_id, Conversation.channel, Conversation.client_conversation_id, unique=True)


class Turn(Base):
    __tablename__ = "turns"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    conversation_id: Mapped[str] = mapped_column(UUID, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    turn_no: Mapped[int] = mapped_column(Integer, nullable=False)
    user_msg_id: Mapped[Optional[str]] = mapped_column(UUID, ForeignKey("messages.id", ondelete="SET NULL"))
    bot_msg_id: Mapped[Optional[str]] = mapped_column(UUID, ForeignKey("messages.id", ondelete="SET NULL"))
    ctx_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=False), server_default=func.now())

    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="turns")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="turn", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("conversation_id", "turn_no", name="uq_turn_conversation_turnno"),
        Index("ix_turn_conversation_created", "conversation_id", "created_at"),
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    conversation_id: Mapped[str] = mapped_column(UUID, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=False), server_default=func.now())

    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")
    nlu_results: Mapped[List["NLUResult"]] = relationship("NLUResult", back_populates="message", cascade="all, delete-orphan")
    citations: Mapped[List["Citation"]] = relationship("Citation", back_populates="message", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_message_conversation_created", "conversation_id", "created_at"),
        Index("ix_message_role", "role"),
    )


class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(UUID, nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ts: Mapped[Any] = mapped_column(DateTime(timezone=False), server_default=func.now())

    __table_args__ = (
        Index("ix_transcript_conversation_ts", "conversation_id", "ts"),
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    turn_id: Mapped[str] = mapped_column(UUID, ForeignKey("turns.id", ondelete="CASCADE"), nullable=False)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    input: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    output: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    started_at: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=False), nullable=True)
    finished_at: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=False), nullable=True)

    turn: Mapped[Turn] = relationship("Turn", back_populates="tasks")

    __table_args__ = (
        Index("ix_task_turn", "turn_id"),
        Index("ix_task_status", "status"),
        Index("ix_task_started", "started_at"),
    )


class StateTransition(Base):
    __tablename__ = "state_transitions"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    conversation_id: Mapped[str] = mapped_column(UUID, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    fsm_id: Mapped[str] = mapped_column(String(128), nullable=False)
    from_state: Mapped[str] = mapped_column(String(255), nullable=False)
    event: Mapped[str] = mapped_column(String(64), nullable=False)
    to_state: Mapped[str] = mapped_column(String(255), nullable=False)
    guard_eval: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=False), server_default=func.now())

    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="transitions")

    __table_args__ = (
        Index("ix_st_conversation_created", "conversation_id", "created_at"),
        Index("ix_st_event", "conversation_id", "event"),
        Index("ix_st_fsm", "fsm_id"),
    )


class NLUResult(Base):
    __tablename__ = "nlu_results"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    message_id: Mapped[str] = mapped_column(UUID, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    intent: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    entities: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    features: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=False), server_default=func.now())

    message: Mapped[Message] = relationship("Message", back_populates="nlu_results")

    __table_args__ = (
        Index("ix_nlu_message", "message_id"),
        Index("ix_nlu_intent", "intent"),
    )


class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    message_id: Mapped[str] = mapped_column(UUID, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    kb_chunk_id: Mapped[str] = mapped_column(UUID, ForeignKey("kb_chunks.id", ondelete="CASCADE"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)

    message: Mapped[Message] = relationship("Message", back_populates="citations")
    kb_chunk: Mapped["KBChunk"] = relationship("KBChunk", back_populates="citations")

    __table_args__ = (
        Index("ix_citation_message_score", "message_id", "score"),
        Index("ix_citation_chunk", "kb_chunk_id"),
    )


class KBDoc(Base):
    __tablename__ = "kb_docs"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    tenant_id: Mapped[Optional[str]] = mapped_column(UUID, nullable=True)
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=False), server_default=func.now())

    chunks: Mapped[List["KBChunk"]] = relationship("KBChunk", back_populates="doc", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_kb_doc_tenant_kind", "tenant_id", "kind"),
        Index("ix_kb_doc_created", "created_at"),
    )


class KBChunk(Base):
    __tablename__ = "kb_chunks"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    kb_doc_id: Mapped[str] = mapped_column(UUID, ForeignKey("kb_docs.id", ondelete="CASCADE"), nullable=False)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    doc: Mapped[KBDoc] = relationship("KBDoc", back_populates="chunks")
    embedding: Mapped["KBEmbedding"] = relationship("KBEmbedding", back_populates="chunk", uselist=False, cascade="all, delete-orphan")
    citations: Mapped[List[Citation]] = relationship("Citation", back_populates="kb_chunk")

    __table_args__ = (
        Index("ix_kb_chunk_doc_ordinal", "kb_doc_id", "ordinal"),
    )


class KBEmbedding(Base):
    __tablename__ = "kb_embeddings"

    kb_chunk_id: Mapped[str] = mapped_column(UUID, ForeignKey("kb_chunks.id", ondelete="CASCADE"), primary_key=True)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=False), server_default=func.now())

    chunk: Mapped[KBChunk] = relationship("KBChunk", back_populates="embedding")


class HandoffSession(Base):
    __tablename__ = "handoff_sessions"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    conversation_id: Mapped[str] = mapped_column(UUID, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    channel_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="open")
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=False), server_default=func.now())
    closed_at: Mapped[Optional[Any]] = mapped_column(DateTime(timezone=False), nullable=True)

    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="handoff_sessions")
