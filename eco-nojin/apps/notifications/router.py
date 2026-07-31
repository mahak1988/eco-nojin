"""In-app notifications (email stub)."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])

_STORE: list[dict] = [
    {
        "id": 1,
        "title": "Irrigation reminder",
        "body": "Zone B soil moisture below threshold",
        "type": "irrigation",
        "read": False,
        "created_at": datetime.now(UTC).isoformat(),
    },
    {
        "id": 2,
        "title": "Pest alert",
        "body": "Aphid risk elevated for next 48h",
        "type": "pest",
        "read": False,
        "created_at": datetime.now(UTC).isoformat(),
    },
]


class NotifOut(BaseModel):
    id: int
    title: str
    body: str
    type: str
    read: bool
    created_at: str


@router.get("")
async def list_notifications(unread_only: bool = Query(False)):
    items = [n for n in _STORE if (not unread_only or not n["read"])]
    return {"data": items, "meta": {"total": len(items)}}


@router.post("/{notif_id}/read")
async def mark_read(notif_id: int):
    for n in _STORE:
        if n["id"] == notif_id:
            n["read"] = True
            return {"ok": True}
    return {"ok": False}


@router.post("/email-stub")
async def email_stub(to: str, subject: str, body: str | None = None):
    return {"queued": True, "to": to, "subject": subject, "channel": "email-stub"}
