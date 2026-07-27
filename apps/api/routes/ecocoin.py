"""EcoCoin routes."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from apps.shared_core.deps import require_write_auth

router = APIRouter(prefix="/api/v1/ecocoin", tags=["ecocoin"])


class BalanceResponse(BaseModel):
    address: str
    balance: float
    currency: str = "ECO"


class TransferRequest(BaseModel):
    from_address: str
    to_address: str
    amount: float
    project_id: Optional[str] = None


class TransferResponse(BaseModel):
    tx_hash: str
    status: str
    amount: float
    timestamp: str


class StakeRequest(BaseModel):
    address: str
    amount: float
    tier_id: int


@router.get("/balance/{address}")
async def get_balance(address: str) -> BalanceResponse:
    return BalanceResponse(address=address, balance=0.0)


@router.get("/stats")
async def get_stats() -> dict[str, Any]:
    return {
        "total_supply": 0,
        "circulating_supply": 0,
        "active_stewards": 0,
    }


@router.post("/transfer")
async def transfer(
    req: TransferRequest,
    _: None = Depends(require_write_auth),
) -> TransferResponse:
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    return TransferResponse(
        tx_hash="0x" + "0" * 64,
        status="pending",
        amount=req.amount,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/staking/tiers")
async def get_staking_tiers() -> list[dict[str, Any]]:
    return [
        {"id": 0, "duration": "3 months", "apy": 8.0, "min_amount": 1000},
        {"id": 1, "duration": "6 months", "apy": 15.0, "min_amount": 5000},
    ]


@router.post("/staking/stake")
async def stake(
    req: StakeRequest,
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    return {"status": "staked", "amount": req.amount, "tier_id": req.tier_id}
