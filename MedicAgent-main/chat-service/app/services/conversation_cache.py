from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Tuple

from .conversation_manager import ConversationManager


@dataclass
class RuntimeMessage:
    id: str
    role: str
    content: str
    meta: Dict[str, Any]
    created_at: float
    nlu: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationRuntime:
    key: str
    tenant_id: str
    channel: str
    client_conversation_id: str
    session_id: str
    manager: ConversationManager
    outbox: List[Dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    status: str = "active"
    messages: List[RuntimeMessage] = field(default_factory=list)
    ended_reason: Optional[str] = None

    def touch(self) -> None:
        self.updated_at = time.time()

    def append_message(self, role: str, content: str, meta: Dict[str, Any], nlu: Dict[str, Any]) -> str:
        message_id = meta.get("message_id") or str(uuid.uuid4())
        enriched_meta = dict(meta)
        enriched_meta.setdefault("idempotency_key", meta.get("idempotency_key"))
        runtime_message = RuntimeMessage(
            id=message_id,
            role=role,
            content=content,
            meta=enriched_meta,
            created_at=time.time(),
            nlu=nlu,
        )
        self.messages.append(runtime_message)
        self.touch()
        return message_id

    def snapshot(self) -> Dict[str, Any]:
        return self.manager.snapshot()

    def mark_closed(self, reason: str) -> None:
        self.status = "closed"
        self.ended_reason = reason
        self.touch()


class ConversationCache:
    def __init__(self, ttl_seconds: int = 120) -> None:
        self._ttl = ttl_seconds
        self._lock = Lock()
        self._items: Dict[str, ConversationRuntime] = {}

    def _make_key(self, tenant_id: str, channel: str, client_conversation_id: str) -> str:
        return f"{tenant_id}:{channel}:{client_conversation_id}"

    def get_or_create(
        self,
        tenant_id: str,
        channel: str,
        client_conversation_id: str,
        factory: Callable[[str], ConversationRuntime],
    ) -> Tuple[ConversationRuntime, bool]:
        key = self._make_key(tenant_id, channel, client_conversation_id)
        with self._lock:
            runtime = self._items.get(key)
            if runtime is not None:
                runtime.touch()
                return runtime, False
            runtime = factory(key)
            self._items[key] = runtime
            return runtime, True

    def remove(self, runtime: ConversationRuntime) -> None:
        with self._lock:
            self._items.pop(runtime.key, None)

    def collect_expired(self) -> List[ConversationRuntime]:
        now = time.time()
        expired: List[ConversationRuntime] = []
        with self._lock:
            keys_to_delete = [key for key, runtime in self._items.items() if now - runtime.updated_at > self._ttl]
            for key in keys_to_delete:
                runtime = self._items.pop(key, None)
                if runtime:
                    expired.append(runtime)
        return expired

    def items(self) -> List[ConversationRuntime]:
        with self._lock:
            return list(self._items.values())
