# apps/api/routes/ecocoin.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/ecocoin", tags=["ecocoin"])


# ============================================================
#  Models
# ============================================================
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


class StakingTier(BaseModel):
    id: int
    duration: str
    apy: float
    multiplier: float
    min_amount: float


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
    hectares_covered: int
    co2_sequestered: int


# ============================================================
#  Routes
# ============================================================
@router.get("/balance/{address}")
async def get_balance(address: str) -> BalanceResponse:
    """دریافت موجودودی EcoCoin یک آدرس."""
    # در production: query blockchain via ethers.js
    return BalanceResponse(
        address=address,
        balance=1250.5,  # نمونه
    )


@router.get("/stats")
async def get_stats() -> EcoCoinStats:
    """دریافت آمار کلی EcoCoin."""
    return EcoCoinStats(
        total_supply=312_500_000,
        circulating_supply=287_400_000,
        total_minted=325_600_000,
        total_burned=13_100_000,
        active_stewards=12_847,
        hectares_covered=142_500,
        co2_sequestered=1_842_000,
    )


@router.post("/transfer")
async def transfer(req: TransferRequest) -> TransferResponse:
    """انتقال EcoCoin."""
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # در production: sign and send transaction
    return TransferResponse(
        tx_hash="0x" + "a" * 64,
        status="pending",
        amount=req.amount,
        timestamp=datetime.now().isoformat(),
    )


@router.get("/staking/tiers")
async def get_staking_tiers() -> list[StakingTier]:
    """دریافت سطح‌های استیکینگ."""
    return [
        StakingTier(id=0, duration="3 months", apy=8.0, multiplier=1.2, min_amount=1000),
        StakingTier(id=1, duration="6 months", apy=15.0, multiplier=1.5, min_amount=5000),
        StakingTier(id=2, duration="1 year", apy=25.0, multiplier=2.0, min_amount=10000),
        StakingTier(id=3, duration="2 years", apy=50.0, multiplier=3.0, min_amount=50000),
    ]


@router.post("/staking/stake")
async def stake(req: StakeRequest) -> dict:
    """استیک کردن EcoCoin."""
    tiers = await get_staking_tiers()
    tier = next((t for t in tiers if t.id == req.tier_id), None)
    if not tier:
        raise HTTPException(status_code=400, detail="Invalid tier")

    if req.amount < tier.min_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum amount is {tier.min_amount} ECO"
        )

    return {
        "status": "staked",
        "amount": req.amount,
        "tier": tier.duration,
        "estimated_reward": req.amount * tier.apy / 100,
        "unlock_date": "2026-10-14T00:00:00",
    }


@router.get("/transactions/{address}")
async def get_transactions(address: str, limit: int = 20) -> list[dict]:
    """دریافت تراکنش‌های یک آدرس."""
    # در production: query from subgraph
    return [
        {
            "tx_hash": "0xabc123...",
            "type": "mint",
            "amount": 45.5,
            "project_id": "amazon-north",
            "reason": "stewardship",
            "timestamp": "2026-07-14T07:00:00",
        },
        {
            "tx_hash": "0xdef456...",
            "type": "transfer",
            "amount": -100.0,
            "to": "0x9Bc1...8a3C",
            "timestamp": "2026-07-14T05:00:00",
        },
    ][:limit]


@router.get("/mining/recent")
async def get_recent_mints(limit: int = 20) -> list[dict]:
    """دریافت آخرین رویدادهای ماینینگ."""
    return [
        {
            "block_number": 18923456,
            "minter": "0x7Ae3...4f2B",
            "recipient": "0x9Bc1...8a3C",
            "amount": 45.5,
            "project_id": "amazon-north",
            "project_name": "آمازون شمالی - سکشن ۴۷",
            "region": "برزیل، آمازون",
            "verification_hash": "QmX7Y8...k9Lm2",
            "mint_reason": 0,
            "sources": 4,
            "tx_hash": "0xabc123...def456",
            "timestamp": "2026-07-14T07:45:00",
        },
    ][:limit]


@router.post("/verify")
async def verify_ecological_proof(
    project_id: str,
    verification_hash: str,
    credit_type: int,
    measured_value: float,
) -> dict:
    """تأیید یک پروژه بوم‌شناختی (Oracle only)."""
    return {
        "verified": True,
        "project_id": project_id,
        "verification_hash": verification_hash,
        "credit_type": credit_type,
        "measured_value": measured_value,
        "timestamp": datetime.now().isoformat(),
    }
