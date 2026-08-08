"""In-memory WebSocket connection manager (Redis Pub/Sub optional later)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._channels: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._channels.setdefault(channel, set()).add(websocket)
        logger.info(
            "ws connect channel=%s clients=%s", channel, len(self._channels.get(channel, ()))
        )

    async def disconnect(self, channel: str, websocket: WebSocket) -> None:
        async with self._lock:
            clients = self._channels.get(channel)
            if clients and websocket in clients:
                clients.discard(websocket)
            if clients is not None and not clients:
                self._channels.pop(channel, None)

    async def broadcast(self, channel: str, message: dict[str, Any]) -> None:
        async with self._lock:
            clients = list(self._channels.get(channel, set()))
        dead: list[WebSocket] = []
        for ws in clients:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(channel, ws)


manager = ConnectionManager()
