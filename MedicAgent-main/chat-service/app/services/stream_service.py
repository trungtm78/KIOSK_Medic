import asyncio
import json
from typing import Any, AsyncIterator, Dict, Optional, Set


class StreamService:
    def __init__(self) -> None:
        self._subscribers: Dict[str, Set[asyncio.Queue[str]]] = {}
        self._lock = asyncio.Lock()

    async def _get_room(self, conversation_id: str) -> Set[asyncio.Queue[str]]:
        async with self._lock:
            room = self._subscribers.get(conversation_id)
            if room is None:
                room = set()
                self._subscribers[conversation_id] = room
            return room

    async def subscribe(self, conversation_id: str, heartbeat_interval: float = 10.0) -> AsyncIterator[str]:
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=100)
        room = await self._get_room(conversation_id)
        room.add(queue)

        try:
            # Initial comment to establish stream
            yield ": connected\n\n"
            while True:
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=heartbeat_interval)
                    yield item
                except asyncio.TimeoutError:
                    # Heartbeat
                    yield ": ping\n\n"
        finally:
            room.discard(queue)

    async def publish(self, conversation_id: str, event: str, data: Dict[str, Any]) -> None:
        room = await self._get_room(conversation_id)
        if not room:
            return
        payload = f"event: {event}\n" + "data: " + json.dumps(data, ensure_ascii=False) + "\n\n"
        for q in list(room):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                # Drop if a subscriber is too slow
                room.discard(q)


_STREAM_SINGLETON: Optional[StreamService] = None


def get_stream_service() -> StreamService:
    global _STREAM_SINGLETON
    if _STREAM_SINGLETON is None:
        _STREAM_SINGLETON = StreamService()
    return _STREAM_SINGLETON

