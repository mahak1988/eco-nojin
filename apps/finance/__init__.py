"""
Finance Router — Minimal stub (source restored from compiled bytecode).
Original router.py was lost; this stub restores the API surface.
"""
from __future__ import annotations
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/finance", tags=["Finance"])

@router.get("/health")
async def finance_health():
    return {"status": "ok", "module": "finance"}

@router.get("/summary")
async def finance_summary():
    return {
        "total_revenue": 0.0,
        "total_expenses": 0.0,
        "net_profit": 0.0,
        "pending_invoices": 0,
    }