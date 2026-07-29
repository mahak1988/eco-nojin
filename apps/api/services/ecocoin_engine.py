"""
EcoCoin economic engine — pure functions, no I/O.
Impact-backed minting, staking math, distribution, indicators.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Constants (SSOT with docs/ECOCOIN_ECONOMIC_DESIGN.md)
# ---------------------------------------------------------------------------

MAX_SUPPLY = 1_000_000_000.0
GENESIS_SUPPLY = 50_000_000.0
IMPACT_MINT_BUDGET = 800_000_000.0
STAKING_POOL = 100_000_000.0
COMMUNITY_POOL = 50_000_000.0

# credit_type → (name, unit, base ECO per unit)
CREDIT_FACTORS: dict[int, tuple[str, str, float]] = {
    0: ("carbon", "tCO2e", 25.0),
    1: ("water", "m3_saved", 0.05),
    2: ("soil_soc", "tC_per_ha", 40.0),
    3: ("biodiversity", "index", 2.0),
}

DISTRIBUTION = {
    "steward": 0.70,
    "verifier": 0.15,
    "treasury": 0.10,
    "community": 0.05,
}

STAKING_TIERS: list[dict[str, Any]] = [
    {"id": 0, "duration": "3 months", "apy": 8.0, "multiplier": 1.0, "min_amount": 1000.0, "days": 90},
    {"id": 1, "duration": "6 months", "apy": 15.0, "multiplier": 1.2, "min_amount": 5000.0, "days": 180},
    {"id": 2, "duration": "12 months", "apy": 25.0, "multiplier": 1.5, "min_amount": 10000.0, "days": 365},
    {"id": 3, "duration": "24 months", "apy": 50.0, "multiplier": 2.0, "min_amount": 25000.0, "days": 730},
]

EARLY_UNSTAKE_FEE_RATE = 0.05
TRANSFER_BURN_RATE = 0.005  # optional protocol burn on transfer


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class WalletState:
    address: str
    available: float = 0.0
    staked: float = 0.0
    pending_rewards: float = 0.0
    impact_credits_tco2e: float = 0.0
    currency: str = "ECO"

    @property
    def total_equity(self) -> float:
        return self.available + self.staked + self.pending_rewards


@dataclass
class ProtocolState:
    total_minted: float = GENESIS_SUPPLY
    total_burned: float = 0.0
    locked_treasury: float = GENESIS_SUPPLY * 0.4
    locked_stake: float = 0.0
    active_stewards: int = 12_847
    hectares_covered: float = 142_500.0
    co2_sequestered: float = 1_842_000.0
    transfer_volume_30d: float = 4_200_000.0
    balances_sample: list[float] = field(default_factory=lambda: [12500.0, 3200.0, 890.0, 45000.0, 120.0, 7800.0, 2100.0])

    @property
    def total_supply(self) -> float:
        return min(MAX_SUPPLY, self.total_minted - self.total_burned)

    @property
    def circulating_supply(self) -> float:
        circ = self.total_minted - self.total_burned - self.locked_treasury - self.locked_stake
        return max(0.0, min(circ, self.total_supply))


# ---------------------------------------------------------------------------
# Mint curve & impact mining
# ---------------------------------------------------------------------------


def remaining_impact_budget(state: ProtocolState) -> float:
    impact_minted = max(0.0, state.total_minted - GENESIS_SUPPLY)
    return max(0.0, IMPACT_MINT_BUDGET - impact_minted)


def mint_scarcity_factor(state: ProtocolState) -> float:
    """Logistic slowdown as impact budget fills (1.0 → ~0.2)."""
    used = max(0.0, state.total_minted - GENESIS_SUPPLY)
    ratio = min(1.0, used / IMPACT_MINT_BUDGET) if IMPACT_MINT_BUDGET else 1.0
    # smoothstep inverse
    return max(0.2, 1.0 - 0.8 * (ratio ** 1.5))


def compute_impact_mint(
    credit_type: int,
    measured_value: float,
    quality_score: float = 1.0,
    region_multiplier: float = 1.0,
    state: Optional[ProtocolState] = None,
) -> dict[str, Any]:
    """Return mint breakdown or error detail."""
    if credit_type not in CREDIT_FACTORS:
        return {"ok": False, "error": "invalid_credit_type", "mint_total": 0.0}
    if measured_value <= 0:
        return {"ok": False, "error": "measured_value_must_be_positive", "mint_total": 0.0}

    quality = max(0.5, min(1.2, quality_score))
    region = max(0.8, min(1.3, region_multiplier))
    name, unit, base = CREDIT_FACTORS[credit_type]
    raw = measured_value * base * quality * region

    st = state or ProtocolState()
    scarcity = mint_scarcity_factor(st)
    budget = remaining_impact_budget(st)
    mint_total = min(raw * scarcity, budget)

    shares = {k: round(mint_total * v, 6) for k, v in DISTRIBUTION.items()}
    return {
        "ok": True,
        "credit_name": name,
        "unit": unit,
        "measured_value": measured_value,
        "quality_score": quality,
        "region_multiplier": region,
        "scarcity_factor": round(scarcity, 4),
        "mint_total": round(mint_total, 6),
        "distribution": shares,
    }


# ---------------------------------------------------------------------------
# Staking
# ---------------------------------------------------------------------------


def get_tier(tier_id: int) -> Optional[dict[str, Any]]:
    return next((t for t in STAKING_TIERS if t["id"] == tier_id), None)


def estimate_stake_reward(amount: float, tier_id: int) -> dict[str, Any]:
    tier = get_tier(tier_id)
    if tier is None:
        return {"ok": False, "error": "invalid_tier"}
    if amount <= 0:
        return {"ok": False, "error": "amount_must_be_positive"}
    if amount < tier["min_amount"]:
        return {
            "ok": False,
            "error": "below_minimum",
            "min_amount": tier["min_amount"],
        }
    estimated = amount * tier["apy"] / 100.0
    unlock = datetime.now(timezone.utc) + timedelta(days=tier["days"])
    return {
        "ok": True,
        "estimated_reward": estimated,
        "unlock_date": unlock.isoformat(),
        "apy": tier["apy"],
        "multiplier": tier["multiplier"],
        "days": tier["days"],
    }


def early_unstake_penalty(principal: float, pending_reward: float) -> dict[str, float]:
    fee = principal * EARLY_UNSTAKE_FEE_RATE
    return {
        "principal_returned": principal - fee,
        "fee_burned": fee,
        "reward_forfeited": pending_reward,
    }


# ---------------------------------------------------------------------------
# Transfer / burn
# ---------------------------------------------------------------------------


def transfer_with_optional_burn(amount: float, apply_burn: bool = False) -> dict[str, float]:
    if amount <= 0:
        raise ValueError("Amount must be positive")
    burn = amount * TRANSFER_BURN_RATE if apply_burn else 0.0
    return {"received": amount - burn, "burned": burn}


# ---------------------------------------------------------------------------
# Challenges
# ---------------------------------------------------------------------------


def challenge_reward(
    pool_eco: float,
    participant_score: float,
    total_score: float,
    curve: str = "proportional",
) -> float:
    if pool_eco <= 0 or total_score <= 0 or participant_score <= 0:
        return 0.0
    share = participant_score / total_score
    if curve == "winner_boost":
        share = share ** 0.7  # slight boost to leaders, still proportional family
        # renormalize not required for single claim demo
    return round(pool_eco * share, 6)


# ---------------------------------------------------------------------------
# Indicators
# ---------------------------------------------------------------------------


def gini(values: list[float]) -> float:
    """Gini coefficient in [0, 1]. Empty → 0."""
    xs = sorted(v for v in values if v >= 0)
    n = len(xs)
    if n == 0:
        return 0.0
    total = sum(xs)
    if total <= 0:
        return 0.0
    cum = 0.0
    for i, x in enumerate(xs, start=1):
        cum += x * (n - i + 1)
    # standard formula
    return max(0.0, min(1.0, (n + 1 - 2 * cum / total) / n))


def compute_indicators(state: ProtocolState) -> dict[str, Any]:
    intensity = (
        (state.total_minted - GENESIS_SUPPLY) / state.co2_sequestered
        if state.co2_sequestered > 0
        else 0.0
    )
    circ = state.circulating_supply or 1.0
    return {
        "impact_intensity_eco_per_tco2e": round(intensity, 4),
        "stake_ratio": round(state.locked_stake / circ, 4),
        "velocity_30d": round(state.transfer_volume_30d / circ, 4),
        "gini_holdings": round(gini(state.balances_sample), 4),
        "circulating_supply": state.circulating_supply,
        "total_supply": state.total_supply,
        "remaining_impact_budget": remaining_impact_budget(state),
        "mint_scarcity_factor": round(mint_scarcity_factor(state), 4),
        "active_stewards": state.active_stewards,
        "co2_sequestered_t": state.co2_sequestered,
        "hectares_covered": state.hectares_covered,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def tx_hash(*parts: Any) -> str:
    raw = "|".join(str(p) for p in parts) + "|" + datetime.now(timezone.utc).isoformat()
    return "0x" + hashlib.sha256(raw.encode()).hexdigest()


def default_wallet(address: str) -> WalletState:
    seed = {
        "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18": WalletState(
            address=address,
            available=12_500.0,
            staked=3_000.0,
            pending_rewards=180.0,
            impact_credits_tco2e=42.5,
        )
    }
    return seed.get(
        address,
        WalletState(address=address, available=100.0),
    )
