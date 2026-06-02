"""Natural miner — EcoCoin from ecosystem actions (formula-based)."""

from math import log1p

ACTION_WEIGHTS = {
    "green_action": 1.0,
    "compost": 1.25,
    "organic_farming": 1.4,
    "solar_pump": 1.6,
    "water_save": 1.2,
    "reforestation": 1.8,
}

GLOBAL_BONUS_REGIONS = {"iran": 1.05, "global": 1.0}


def mine_natural_tokens(
    action_type: str,
    amount: float,
    *,
    carbon_kg: float = 0,
    water_saved_liters: float = 0,
    region: str = "global",
) -> dict:
    weight = ACTION_WEIGHTS.get(action_type, 1.0)
    region_mult = GLOBAL_BONUS_REGIONS.get(region.lower(), 1.0)
    base = amount * weight * region_mult
    carbon_bonus = log1p(max(carbon_kg, 0)) * 2.5
    water_bonus = log1p(max(water_saved_liters, 0)) * 0.15
    ecosystem_score = round(base + carbon_bonus + water_bonus, 4)
    tokens = round(ecosystem_score * 10, 2)
    return {
        "tokens_earned": tokens,
        "ecosystem_score": ecosystem_score,
        "formula": "tokens = (amount×weight×region + ln(1+carbon)×2.5 + ln(1+water)×0.15) × 10",
        "action_type": action_type,
        "region": region,
    }
