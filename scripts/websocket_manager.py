"""
مدیریت WebSocket connections برای streaming بلادرنگ
"""
from fastapi import WebSocket
from typing import Dict, List, Set
import asyncio
import json
import structlog
from datetime import datetime

logger = structlog.get_logger()


class ConnectionManager:
    """مدیریت connections WebSocket به تفکیک session"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.logger = logger.bind(component="websocket_manager")

    async def connect(self, websocket: WebSocket, session_id: str):
        """اتصال یک کلاینت به یک session"""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        self.logger.info("client_connected",
                         session_id=session_id,
                         total_clients=len(self.active_connections[session_id]))

    def disconnect(self, websocket: WebSocket, session_id: str):
        """قطع اتصال یک کلاینت"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
            self.logger.info("client_disconnected", session_id=session_id)

    async def send_event(self, session_id: str, event: dict):
        """ارسال رویداد به همه کلاینت‌های یک session"""
        if session_id not in self.active_connections:
            return

        event_with_timestamp = {
            **event,
            "timestamp": datetime.now().isoformat()
        }

        # ارسال به همه کلاینت‌های متصل
        disconnected = set()
        for websocket in self.active_connections[session_id]:
            try:
                await websocket.send_json(event_with_timestamp)
            except Exception as e:
                self.logger.warning("send_failed", error=str(e))
                disconnected.add(websocket)

        # حذف کلاینت‌های قطع‌شده
        for ws in disconnected:
            self.disconnect(ws, session_id)

    async def broadcast(self, event: dict):
        """ارسال به همه sessionها"""
        for session_id in list(self.active_connections.keys()):
            await self.send_event(session_id, event)

    def get_active_sessions(self) -> Dict[str, int]:
        """دریافت لیست sessionهای فعال و تعداد کلاینت‌های هرکدام"""
        return {
            session_id: len(clients)
            for session_id, clients in self.active_connections.items()
        }


# Singleton instance
manager = ConnectionManager()