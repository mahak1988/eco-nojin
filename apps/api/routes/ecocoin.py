"""EcoCoin routes — mock/stub API aligned with contracts and tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from apps.shared_core.deps import require_write_auth

router = APIRouter(prefix="/api/v1/ecocoin", tags=["ecocoin"])

# ---------------------------------------------------------------------------
# Models (exported for unit tests)
# ---------------------------------------------------------------------------


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


class StakingTier(BaseModel):
    id: int
    duration: str
    apy: float
    multiplier: float
    min_amount: float


class EcoCoinStats(BaseModel):
    total_supply: float
    circulating_supply: float
    total_minted: float
    total_burned: float
    active_stewards: int
    hectares_covered: float
    co2_sequestered: float


# ---------------------------------------------------------------------------
# Static mock data
# ---------------------------------------------------------------------------

_STAKING_TIERS: list[StakingTier] = [
    StakingTier(id=0, duration="3 months", apy=8.0, multiplier=1.0, min_amount=1000),
    StakingTier(id=1, duration="6 months", apy=15.0, multiplier=1.2, min_amount=5000),
    StakingTier(id=2, duration="12 months", apy=25.0, multiplier=1.5, min_amount=10000),
    StakingTier(id=3, duration="24 months", apy=50.0, multiplier=2.0, min_amount=25000),
]

_MOCK_BALANCES: dict[str, float] = {
    "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18": 12500.0,
}

_MOCK_TXS: list[dict[str, Any]] = [
    {
        "tx_hash": "0x" + "a" * 64,
        "type": "transfer",
        "amount": 100.0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
]

_MOCK_MINTS: list[dict[str, Any]] = [
    {
        "block_number": 1_234_567,
        "minter": "0xOracle",
        "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
        "amount": 500.0,
        "project_id": "amazon-north-47",
        "tx_hash": "0x" + "b" * 64,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/balance/{address}", response_model=BalanceResponse)
async def get_balance(address: str) -> BalanceResponse:
    balance = _MOCK_BALANCES.get(address, 100.0)
    return BalanceResponse(address=address, balance=balance)


@router.get("/stats", response_model=EcoCoinStats)
async def get_stats() -> EcoCoinStats:
    return EcoCoinStats(
        total_supply=312_500_000,
        circulating_supply=287_400_000,
        total_minted=325_600_000,
        total_burned=13_100_000,
        active_stewards=12_847,
        hectares_covered=142_500,
        co2_sequestered=1_842_000,
    )


@router.post("/transfer", response_model=TransferResponse)
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
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/staking/tiers")
async def get_staking_tiers() -> list[dict[str, Any]]:
    return [t.model_dump() for t in _STAKING_TIERS]


@router.post("/staking/stake")
async def stake(
    req: StakeRequest,
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    tier = next((t for t in _STAKING_TIERS if t.id == req.tier_id), None)
    if tier is None:
        raise HTTPException(status_code=400, detail="Invalid tier_id")
    if req.amount < tier.min_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum amount for tier {tier.id} is {tier.min_amount}",
        )
    estimated_reward = req.amount * tier.apy / 100.0
    unlock = datetime.now(timezone.utc) + timedelta(days=90 * (req.tier_id + 1))
    return {
        "status": "staked",
        "amount": req.amount,
        "tier_id": req.tier_id,
        "estimated_reward": estimated_reward,
        "unlock_date": unlock.isoformat(),
    }


@router.get("/transactions/{address}")
async def get_transactions(
    address: str,
    limit: int = Query(20, ge=1, le=100),
) -> list[dict[str, Any]]:
    return _MOCK_TXS[:limit]


@router.get("/mining/recent")
async def get_recent_mints(
    limit: int = Query(20, ge=1, le=100),
) -> list[dict[str, Any]]:
    return _MOCK_MINTS[:limit]


@router.post("/verify")
async def verify(
    project_id: str = Query(...),
    verification_hash: str = Query(...),
    credit_type: int = Query(...),
    measured_value: float = Query(...),
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    return {
        "verified": True,
        "project_id": project_id,
        "verification_hash": verification_hash,
        "credit_type": credit_type,
        "measured_value": measured_value,
    }
