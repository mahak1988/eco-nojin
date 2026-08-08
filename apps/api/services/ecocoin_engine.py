"""
EcoCoin economic engine — pure functions, no I/O.
Impact-backed minting, staking math, distribution, indicators.
MRV quality from NDVI / model / field agreement + sensitivity analysis.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

MAX_SUPPLY = 1_000_000_000.0
GENESIS_SUPPLY = 50_000_000.0
IMPACT_MINT_BUDGET = 800_000_000.0
STAKING_POOL = 100_000_000.0
COMMUNITY_POOL = 50_000_000.0

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
    {
        "id": 0,
        "duration": "3 months",
        "apy": 8.0,
        "multiplier": 1.0,
        "min_amount": 1000.0,
        "days": 90,
    },
    {
        "id": 1,
        "duration": "6 months",
        "apy": 15.0,
        "multiplier": 1.2,
        "min_amount": 5000.0,
        "days": 180,
    },
    {
        "id": 2,
        "duration": "12 months",
        "apy": 25.0,
        "multiplier": 1.5,
        "min_amount": 10000.0,
        "days": 365,
    },
    {
        "id": 3,
        "duration": "24 months",
        "apy": 50.0,
        "multiplier": 2.0,
        "min_amount": 25000.0,
        "days": 730,
    },
]

EARLY_UNSTAKE_FEE_RATE = 0.05
TRANSFER_BURN_RATE = 0.005


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
    balances_sample: list[float] = field(
        default_factory=lambda: [12500.0, 3200.0, 890.0, 45000.0, 120.0, 7800.0, 2100.0]
    )

    @property
    def total_supply(self) -> float:
        return min(MAX_SUPPLY, self.total_minted - self.total_burned)

    @property
    def circulating_supply(self) -> float:
        circ = self.total_minted - self.total_burned - self.locked_treasury - self.locked_stake
        return max(0.0, min(circ, self.total_supply))


def remaining_impact_budget(state: ProtocolState) -> float:
    impact_minted = max(0.0, state.total_minted - GENESIS_SUPPLY)
    return max(0.0, IMPACT_MINT_BUDGET - impact_minted)


def mint_scarcity_factor(state: ProtocolState) -> float:
    used = max(0.0, state.total_minted - GENESIS_SUPPLY)
    ratio = min(1.0, used / IMPACT_MINT_BUDGET) if IMPACT_MINT_BUDGET else 1.0
    return max(0.2, 1.0 - 0.8 * (ratio**1.5))


def scarcity_at_ratio(ratio: float) -> float:
    r = max(0.0, min(1.0, ratio))
    return max(0.2, 1.0 - 0.8 * (r**1.5))


def quality_from_mrv(
    ndvi_observed: float | None = None,
    ndvi_expected: float | None = None,
    model_yield_t_ha: float | None = None,
    field_yield_t_ha: float | None = None,
    field_data_present: bool = False,
    satellite_available: bool = False,
) -> dict[str, Any]:
    components: dict[str, float] = {}
    base = 0.85

    if ndvi_observed is not None and ndvi_expected is not None and ndvi_expected != 0:
        rel_err = abs(ndvi_observed - ndvi_expected) / max(abs(ndvi_expected), 1e-6)
        ndvi_score = max(0.0, 1.0 - rel_err)
        components["ndvi_agreement"] = round(ndvi_score, 4)
        base = 0.9 + 0.2 * ndvi_score
        satellite_available = True

    if model_yield_t_ha is not None and field_yield_t_ha is not None and model_yield_t_ha > 0:
        rel_err = abs(model_yield_t_ha - field_yield_t_ha) / max(model_yield_t_ha, 1e-6)
        model_score = max(0.0, 1.0 - rel_err)
        components["model_field_agreement"] = round(model_score, 4)
        base = (base + (0.9 + 0.25 * model_score)) / 2.0
        field_data_present = True

    bonus = 0.0
    if satellite_available:
        bonus += 0.05
        components["satellite_bonus"] = 0.05
    if field_data_present:
        bonus += 0.08
        components["field_bonus"] = 0.08
    if satellite_available and field_data_present and "model_field_agreement" in components:
        bonus += 0.05
        components["triple_source_bonus"] = 0.05

    q = max(0.5, min(1.2, base + bonus))
    return {
        "quality_score": round(q, 4),
        "components": components,
        "inputs": {
            "ndvi_observed": ndvi_observed,
            "ndvi_expected": ndvi_expected,
            "model_yield_t_ha": model_yield_t_ha,
            "field_yield_t_ha": field_yield_t_ha,
            "field_data_present": field_data_present,
            "satellite_available": satellite_available,
        },
    }


def compute_impact_mint(
    credit_type: int,
    measured_value: float,
    quality_score: float = 1.0,
    region_multiplier: float = 1.0,
    state: ProtocolState | None = None,
    credit_factor_override: float | None = None,
    scarcity_override: float | None = None,
) -> dict[str, Any]:
    if credit_type not in CREDIT_FACTORS:
        return {"ok": False, "error": "invalid_credit_type", "mint_total": 0.0}
    if measured_value <= 0:
        return {"ok": False, "error": "measured_value_must_be_positive", "mint_total": 0.0}

    quality = max(0.5, min(1.2, quality_score))
    region = max(0.8, min(1.3, region_multiplier))
    name, unit, base = CREDIT_FACTORS[credit_type]
    if credit_factor_override is not None:
        base = credit_factor_override
    raw = measured_value * base * quality * region

    st = state or ProtocolState()
    scarcity = scarcity_override if scarcity_override is not None else mint_scarcity_factor(st)
    scarcity = max(0.2, min(1.0, scarcity))
    budget = remaining_impact_budget(st)
    mint_total = min(raw * scarcity, budget)

    shares = {k: round(mint_total * v, 6) for k, v in DISTRIBUTION.items()}
    return {
        "ok": True,
        "credit_name": name,
        "unit": unit,
        "measured_value": measured_value,
        "credit_factor": base,
        "quality_score": quality,
        "region_multiplier": region,
        "scarcity_factor": round(scarcity, 4),
        "raw_before_scarcity": round(raw, 6),
        "mint_total": round(mint_total, 6),
        "distribution": shares,
    }


def _elasticity(m0: float, m1: float, x0: float, x1: float) -> float:
    """(ΔM/M) / (Δx/x); 0 if x is at a clamp (no movement)."""
    if abs(x0) < 1e-15 or abs(x1 - x0) < 1e-15 or abs(m0) < 1e-15:
        return 0.0
    return round(((m1 - m0) / m0) / ((x1 - x0) / x0), 4)


def sensitivity_analysis(
    credit_type: int = 0,
    measured_value: float = 40.0,
    quality_score: float = 1.0,
    region_multiplier: float = 1.0,
    state: ProtocolState | None = None,
) -> dict[str, Any]:
    st = state or ProtocolState()
    base = compute_impact_mint(credit_type, measured_value, quality_score, region_multiplier, st)
    if not base["ok"]:
        return base

    m0 = base["mint_total"] if base["mint_total"] else 1e-12
    _, _, fc0 = CREDIT_FACTORS[credit_type]
    s0 = float(base["scarcity_factor"])

    fc_hi_x = fc0 * 1.1
    fc_lo_x = fc0 * 0.9
    s_hi_x = min(1.0, s0 * 1.1)
    s_lo_x = max(0.2, s0 * 0.9)
    # If S is already at ceiling, step down from baseline for a measurable Δ
    if abs(s_hi_x - s0) < 1e-12:
        s_hi_x = max(0.2, s0 - 0.1)
    q_hi_x = min(1.2, quality_score * 1.1)
    q_lo_x = max(0.5, quality_score * 0.9)
    if abs(q_hi_x - quality_score) < 1e-12:
        q_hi_x = max(0.5, quality_score - 0.1)
    r_hi_x = min(1.3, region_multiplier * 1.1)
    r_lo_x = max(0.8, region_multiplier * 0.9)
    if abs(r_hi_x - region_multiplier) < 1e-12:
        r_hi_x = max(0.8, region_multiplier - 0.1)

    fc_hi = compute_impact_mint(
        credit_type,
        measured_value,
        quality_score,
        region_multiplier,
        st,
        credit_factor_override=fc_hi_x,
    )
    fc_lo = compute_impact_mint(
        credit_type,
        measured_value,
        quality_score,
        region_multiplier,
        st,
        credit_factor_override=fc_lo_x,
    )
    s_hi = compute_impact_mint(
        credit_type,
        measured_value,
        quality_score,
        region_multiplier,
        st,
        scarcity_override=s_hi_x,
    )
    s_lo = compute_impact_mint(
        credit_type,
        measured_value,
        quality_score,
        region_multiplier,
        st,
        scarcity_override=s_lo_x,
    )
    q_hi = compute_impact_mint(credit_type, measured_value, q_hi_x, region_multiplier, st)
    q_lo = compute_impact_mint(credit_type, measured_value, q_lo_x, region_multiplier, st)
    r_hi = compute_impact_mint(credit_type, measured_value, quality_score, r_hi_x, st)
    r_lo = compute_impact_mint(credit_type, measured_value, quality_score, r_lo_x, st)

    scarcity_curve = [
        {"ratio": round(r, 2), "S": round(scarcity_at_ratio(r), 4)}
        for r in [i / 10 for i in range(11)]
    ]

    return {
        "baseline": base,
        "parameters": {
            "Fc": fc0,
            "S": s0,
            "Q": quality_score,
            "R": region_multiplier,
            "V": measured_value,
        },
        "sensitivity": {
            "Fc": {
                "plus_10pct_mint": fc_hi["mint_total"],
                "minus_10pct_mint": fc_lo["mint_total"],
                "elasticity_approx": _elasticity(m0, fc_hi["mint_total"], fc0, fc_hi_x),
                "note": "Linear in Fc before budget cap",
            },
            "S": {
                "plus_10pct_mint": s_hi["mint_total"],
                "minus_10pct_mint": s_lo["mint_total"],
                "elasticity_approx": _elasticity(m0, s_hi["mint_total"], s0, s_hi_x),
                "note": "S falls as impact budget fills; floor 0.2, ceiling 1.0",
            },
            "Q": {
                "plus_10pct_mint": q_hi["mint_total"],
                "minus_10pct_mint": q_lo["mint_total"],
                "elasticity_approx": _elasticity(m0, q_hi["mint_total"], quality_score, q_hi_x),
                "note": "Clamped to [0.5, 1.2]",
            },
            "R": {
                "plus_10pct_mint": r_hi["mint_total"],
                "minus_10pct_mint": r_lo["mint_total"],
                "elasticity_approx": _elasticity(m0, r_hi["mint_total"], region_multiplier, r_hi_x),
                "note": "Clamped to [0.8, 1.3]",
            },
        },
        "scarcity_curve": scarcity_curve,
        "formula": "M = min(V * Fc * Q * R * S, B)",
    }


def get_tier(tier_id: int) -> dict[str, Any] | None:
    return next((t for t in STAKING_TIERS if t["id"] == tier_id), None)


def estimate_stake_reward(amount: float, tier_id: int) -> dict[str, Any]:
    tier = get_tier(tier_id)
    if tier is None:
        return {"ok": False, "error": "invalid_tier"}
    if amount <= 0:
        return {"ok": False, "error": "amount_must_be_positive"}
    if amount < tier["min_amount"]:
        return {"ok": False, "error": "below_minimum", "min_amount": tier["min_amount"]}
    estimated = amount * tier["apy"] / 100.0
    unlock = datetime.now(UTC) + timedelta(days=tier["days"])
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


def transfer_with_optional_burn(amount: float, apply_burn: bool = False) -> dict[str, float]:
    if amount <= 0:
        raise ValueError("Amount must be positive")
    burn = amount * TRANSFER_BURN_RATE if apply_burn else 0.0
    return {"received": amount - burn, "burned": burn}


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
        share = share**0.7
    return round(pool_eco * share, 6)


def gini(values: list[float]) -> float:
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


def tx_hash(*parts: Any) -> str:
    raw = "|".join(str(p) for p in parts) + "|" + datetime.now(UTC).isoformat()
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
    return seed.get(address, WalletState(address=address, available=100.0))
