"""
EcoCoin API — impact-backed utility token for Econojin.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.services.ecocoin_engine import (
    CREDIT_FACTORS,
    DISTRIBUTION,
    MAX_SUPPLY,
    ProtocolState,
    STAKING_TIERS,
    challenge_reward,
    compute_impact_mint,
    compute_indicators,
    default_wallet,
    early_unstake_penalty,
    estimate_stake_reward,
    get_tier,
    quality_from_mrv,
    sensitivity_analysis,
    tx_hash,
)
from apps.api.services.oracle_sign import sign_mint_payload
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


class EcoCoinStats(BaseModel):
    total_supply: float
    circulating_supply: float
    total_minted: float
    total_burned: float
    active_stewards: int
    hectares_covered: float
    co2_sequestered: float


class UnstakeRequest(BaseModel):
    address: str
    amount: float
    tier_id: int
    early: bool = False
    pending_reward: float = 0.0


class ImpactMintRequest(BaseModel):
    recipient: str
    project_id: str
    credit_type: int = Field(..., ge=0, le=3)
    measured_value: float
    quality_score: float = 1.0
    region_multiplier: float = 1.0
    verification_hash: str


class BurnRequest(BaseModel):
    address: str
    amount: float
    reason: str = "voluntary_retirement"


class ChallengeJoinRequest(BaseModel):
    address: str


class ChallengeClaimRequest(BaseModel):
    address: str
    score: float = Field(..., gt=0)


class RewardClaimRequest(BaseModel):
    address: str
    amount: Optional[float] = None


class MrvQualityRequest(BaseModel):
    ndvi_observed: Optional[float] = Field(None, ge=0, le=1)
    ndvi_expected: Optional[float] = Field(None, ge=0, le=1)
    model_yield_t_ha: Optional[float] = Field(None, ge=0)
    field_yield_t_ha: Optional[float] = Field(None, ge=0)
    field_data_present: bool = False
    satellite_available: bool = False


_STATE = ProtocolState()

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

_CHALLENGES: list[dict[str, Any]] = [
    {
        "id": "ch-water-2026q3",
        "title": "Save 10,000 m³ irrigation water",
        "metric": "water_m3_saved",
        "target": 10_000.0,
        "pool_eco": 50_000.0,
        "starts_at": "2026-07-01T00:00:00Z",
        "ends_at": "2026-09-30T23:59:59Z",
        "status": "active",
        "participants": 0,
        "total_score": 0.0,
    },
    {
        "id": "ch-carbon-amazon",
        "title": "Amazon North sequester 500 tCO₂e",
        "metric": "tco2e",
        "target": 500.0,
        "pool_eco": 100_000.0,
        "starts_at": "2026-06-01T00:00:00Z",
        "ends_at": "2026-12-31T23:59:59Z",
        "status": "active",
        "participants": 0,
        "total_score": 0.0,
    },
    {
        "id": "ch-school-modules",
        "title": "Complete 5 agriculture school modules",
        "metric": "modules_completed",
        "target": 5.0,
        "pool_eco": 5_000.0,
        "starts_at": "2026-07-15T00:00:00Z",
        "ends_at": "2026-08-31T23:59:59Z",
        "status": "active",
        "participants": 0,
        "total_score": 0.0,
    },
]

_PENDING_REWARDS: dict[str, float] = {
    "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18": 180.0,
}


def _try_db():
    """Optional DB dependency — tests without session still work."""
    try:
        from apps.shared_core.database.session import get_db_session

        return Depends(get_db_session)
    except Exception:
        return None


@router.get("/balance/{address}", response_model=BalanceResponse)
async def get_balance(address: str) -> BalanceResponse:
    w = default_wallet(address)
    balance = _MOCK_BALANCES.get(address, w.available)
    return BalanceResponse(address=address, balance=balance)


@router.get("/stats", response_model=EcoCoinStats)
async def get_stats() -> EcoCoinStats:
    return EcoCoinStats(
        total_supply=_STATE.total_supply,
        circulating_supply=_STATE.circulating_supply,
        total_minted=_STATE.total_minted,
        total_burned=_STATE.total_burned,
        active_stewards=_STATE.active_stewards,
        hectares_covered=_STATE.hectares_covered,
        co2_sequestered=_STATE.co2_sequestered,
    )


@router.post("/transfer", response_model=TransferResponse)
async def transfer(
    req: TransferRequest,
    _: None = Depends(require_write_auth),
) -> TransferResponse:
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    h = tx_hash(req.from_address, req.to_address, req.amount, req.project_id)
    _MOCK_TXS.insert(
        0,
        {
            "tx_hash": h,
            "type": "transfer",
            "amount": req.amount,
            "from": req.from_address,
            "to": req.to_address,
            "project_id": req.project_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
    return TransferResponse(
        tx_hash=h,
        status="pending",
        amount=req.amount,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/staking/tiers")
async def get_staking_tiers() -> list[dict[str, Any]]:
    return [
        {
            "id": t["id"],
            "duration": t["duration"],
            "apy": t["apy"],
            "multiplier": t["multiplier"],
            "min_amount": t["min_amount"],
        }
        for t in STAKING_TIERS
    ]


@router.post("/staking/stake")
async def stake(
    req: StakeRequest,
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    result = estimate_stake_reward(req.amount, req.tier_id)
    if not result.get("ok"):
        err = result.get("error", "invalid")
        if err == "invalid_tier":
            raise HTTPException(status_code=400, detail="Invalid tier_id")
        if err == "below_minimum":
            raise HTTPException(
                status_code=400,
                detail=f"Minimum amount for tier {req.tier_id} is {result['min_amount']}",
            )
        raise HTTPException(status_code=400, detail=err)
    _STATE.locked_stake += req.amount
    return {
        "status": "staked",
        "amount": req.amount,
        "tier_id": req.tier_id,
        "estimated_reward": result["estimated_reward"],
        "unlock_date": result["unlock_date"],
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


@router.get("/wallet/{address}")
async def get_wallet(address: str) -> dict[str, Any]:
    w = default_wallet(address)
    if address in _MOCK_BALANCES:
        w.available = _MOCK_BALANCES[address]
    w.pending_rewards = _PENDING_REWARDS.get(address, w.pending_rewards)
    return {
        "address": w.address,
        "currency": w.currency,
        "available": w.available,
        "staked": w.staked,
        "pending_rewards": w.pending_rewards,
        "impact_credits_tco2e": w.impact_credits_tco2e,
        "total_equity": w.total_equity,
    }


@router.post("/staking/unstake")
async def unstake(
    req: UnstakeRequest,
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if get_tier(req.tier_id) is None:
        raise HTTPException(status_code=400, detail="Invalid tier_id")
    if req.early:
        penalty = early_unstake_penalty(req.amount, req.pending_reward)
        _STATE.total_burned += penalty["fee_burned"]
        _STATE.locked_stake = max(0.0, _STATE.locked_stake - req.amount)
        return {
            "status": "unstaked_early",
            **penalty,
            "tx_hash": tx_hash("unstake", req.address, req.amount),
        }
    _STATE.locked_stake = max(0.0, _STATE.locked_stake - req.amount)
    return {
        "status": "unstaked",
        "principal_returned": req.amount,
        "reward_paid": req.pending_reward,
        "tx_hash": tx_hash("unstake", req.address, req.amount),
    }


@router.post("/mining/impact-mint")
async def impact_mint(
    req: ImpactMintRequest,
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    result = compute_impact_mint(
        credit_type=req.credit_type,
        measured_value=req.measured_value,
        quality_score=req.quality_score,
        region_multiplier=req.region_multiplier,
        state=_STATE,
    )
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result["error"])

    mint_total = result["mint_total"]
    _STATE.total_minted += mint_total
    if req.credit_type == 0:
        _STATE.co2_sequestered += req.measured_value

    h = tx_hash(req.recipient, req.project_id, req.verification_hash, mint_total)
    oracle = sign_mint_payload(
        {
            "tx_hash": h,
            "recipient": req.recipient,
            "project_id": req.project_id,
            "credit_type": req.credit_type,
            "measured_value": req.measured_value,
            "quality_score": req.quality_score,
            "mint_total": mint_total,
            "verification_hash": req.verification_hash,
        }
    )

    entry = {
        "block_number": 1_234_567 + len(_MOCK_MINTS),
        "minter": "0xOracle",
        "recipient": req.recipient,
        "amount": mint_total,
        "project_id": req.project_id,
        "tx_hash": h,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "credit_type": req.credit_type,
        "distribution": result["distribution"],
        "oracle_signature": oracle["signature"],
        "oracle_algorithm": oracle["algorithm"],
    }
    _MOCK_MINTS.insert(0, entry)
    steward_share = result["distribution"]["steward"]
    _MOCK_BALANCES[req.recipient] = _MOCK_BALANCES.get(req.recipient, 100.0) + steward_share

    # Best-effort DB persist (table via create_all / Alembic)
    try:
        from apps.shared_core.database.session import async_session_maker
        from apps.api.services.mint_persistence import persist_mint_event

        async with async_session_maker() as session:
            await persist_mint_event(
                session,
                tx_hash=h,
                recipient=req.recipient,
                project_id=req.project_id,
                credit_type=req.credit_type,
                credit_name=result["credit_name"],
                measured_value=req.measured_value,
                quality_score=result["quality_score"],
                region_multiplier=result["region_multiplier"],
                scarcity_factor=result["scarcity_factor"],
                mint_total=mint_total,
                distribution=result["distribution"],
                verification_hash=req.verification_hash,
            )
            await session.commit()
            entry["persisted"] = True
    except Exception as e:
        entry["persisted"] = False
        entry["persist_error"] = type(e).__name__

    return {"status": "minted", "tx_hash": h, "oracle_signature": oracle["signature"], **result, "persisted": entry.get("persisted")}


@router.get("/challenges")
async def list_challenges(status: Optional[str] = Query(None)) -> dict[str, Any]:
    items = _CHALLENGES
    if status:
        items = [c for c in items if c["status"] == status]
    return {"challenges": items, "total": len(items)}


@router.post("/challenges/{challenge_id}/join")
async def join_challenge(
    challenge_id: str,
    req: ChallengeJoinRequest,
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    ch = next((c for c in _CHALLENGES if c["id"] == challenge_id), None)
    if ch is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if ch["status"] != "active":
        raise HTTPException(status_code=400, detail="Challenge not active")
    ch["participants"] += 1
    return {
        "status": "joined",
        "challenge_id": challenge_id,
        "address": req.address,
        "participants": ch["participants"],
    }


@router.post("/challenges/{challenge_id}/claim")
async def claim_challenge(
    challenge_id: str,
    req: ChallengeClaimRequest,
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    ch = next((c for c in _CHALLENGES if c["id"] == challenge_id), None)
    if ch is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    ch["total_score"] += req.score
    reward = challenge_reward(ch["pool_eco"], req.score, max(ch["total_score"], req.score))
    _PENDING_REWARDS[req.address] = _PENDING_REWARDS.get(req.address, 0.0) + reward
    return {
        "status": "claimed",
        "challenge_id": challenge_id,
        "score": req.score,
        "reward_eco": reward,
        "pending_rewards": _PENDING_REWARDS[req.address],
    }


@router.get("/rewards/{address}")
async def get_rewards(address: str) -> dict[str, Any]:
    pending = _PENDING_REWARDS.get(address, 0.0)
    return {
        "address": address,
        "pending_rewards": pending,
        "claimable": pending > 0,
        "currency": "ECO",
    }


@router.post("/rewards/claim")
async def claim_rewards(
    req: RewardClaimRequest,
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    pending = _PENDING_REWARDS.get(req.address, 0.0)
    if pending <= 0:
        raise HTTPException(status_code=400, detail="No pending rewards")
    amount = pending if req.amount is None else min(req.amount, pending)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    _PENDING_REWARDS[req.address] = pending - amount
    _MOCK_BALANCES[req.address] = _MOCK_BALANCES.get(req.address, 100.0) + amount
    h = tx_hash("claim", req.address, amount)
    return {
        "status": "claimed",
        "amount": amount,
        "remaining_pending": _PENDING_REWARDS[req.address],
        "tx_hash": h,
    }


@router.get("/indicators")
async def get_indicators() -> dict[str, Any]:
    return compute_indicators(_STATE)


@router.get("/economics")
async def get_economics() -> dict[str, Any]:
    return {
        "token": {
            "symbol": "ECO",
            "max_supply": MAX_SUPPLY,
            "total_minted": _STATE.total_minted,
            "total_burned": _STATE.total_burned,
            "circulating_supply": _STATE.circulating_supply,
        },
        "distribution_on_mint": DISTRIBUTION,
        "credit_types": {
            str(k): {"name": v[0], "unit": v[1], "base_eco_per_unit": v[2]}
            for k, v in CREDIT_FACTORS.items()
        },
        "staking_tiers": STAKING_TIERS,
        "value_creation": {
            "model": "impact_backed",
            "description": (
                "ECO is minted against verified environmental outcomes; "
                "70% to stewards, 15% verifiers, 10% treasury, 5% community."
            ),
            "anchors": [
                "tCO2e",
                "m3_water_saved",
                "soil_organic_carbon",
                "biodiversity_index",
            ],
        },
        "indicators": compute_indicators(_STATE),
    }


@router.get("/economics/sensitivity")
async def get_sensitivity(
    credit_type: int = Query(0, ge=0, le=3),
    measured_value: float = Query(40.0, gt=0),
    quality_score: float = Query(1.0, ge=0.5, le=1.2),
    region_multiplier: float = Query(1.0, ge=0.8, le=1.3),
) -> dict[str, Any]:
    return sensitivity_analysis(
        credit_type=credit_type,
        measured_value=measured_value,
        quality_score=quality_score,
        region_multiplier=region_multiplier,
        state=_STATE,
    )


@router.post("/mrv/quality-score")
async def post_mrv_quality(req: MrvQualityRequest) -> dict[str, Any]:
    return quality_from_mrv(
        ndvi_observed=req.ndvi_observed,
        ndvi_expected=req.ndvi_expected,
        model_yield_t_ha=req.model_yield_t_ha,
        field_yield_t_ha=req.field_yield_t_ha,
        field_data_present=req.field_data_present,
        satellite_available=req.satellite_available,
    )


@router.post("/burn")
async def burn(
    req: BurnRequest,
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    bal = _MOCK_BALANCES.get(req.address, 0.0)
    if bal >= req.amount:
        _MOCK_BALANCES[req.address] = bal - req.amount
    _STATE.total_burned += req.amount
    h = tx_hash("burn", req.address, req.amount, req.reason)
    return {
        "status": "burned",
        "amount": req.amount,
        "reason": req.reason,
        "tx_hash": h,
        "total_burned": _STATE.total_burned,
    }
