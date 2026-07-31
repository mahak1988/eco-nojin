"""WebSocket endpoints — monitoring channel."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from apps.shared_core.websocket.manager import manager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    allowed = {"monitoring", "notifications", "ai-chat"}
    if channel not in allowed:
        await websocket.close(code=4400)
        return
    await manager.connect(channel, websocket)
    try:
        # heartbeat + optional client pings
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=25.0)
                if data == "ping":
                    await websocket.send_json({"type": "pong", "ts": datetime.now(UTC).isoformat()})
                else:
                    await manager.broadcast(channel, {"type": "echo", "channel": channel, "payload": data})
            except TimeoutError:
                await websocket.send_json(
                    {
                        "type": "heartbeat",
                        "channel": channel,
                        "ts": datetime.now(UTC).isoformat(),
                    }
                )
    except WebSocketDisconnect:
        await manager.disconnect(channel, websocket)
    except Exception as e:
        logger.debug("ws error: %s", e)
        await manager.disconnect(channel, websocket)
