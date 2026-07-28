"""Crop rotation, yield prediction, disease rules — rule-based MVP."""

from __future__ import annotations

from typing import Any


COMPAT: dict[str, list[str]] = {
    "wheat": ["legume", "fallow", "potato"],
    "barley": ["legume", "fallow"],
    "corn": ["legume", "wheat"],
    "rice": ["legume", "fallow"],
    "tomato": ["legume", "cereal"],
    "potato": ["cereal", "legume"],
    "default": ["legume", "cereal", "fallow"],
}

BASE_YIELD_T_HA: dict[str, float] = {
    "wheat": 4.5,
    "barley": 3.8,
    "corn": 7.0,
    "rice": 5.5,
    "tomato": 45.0,
    "potato": 25.0,
    "default": 3.0,
}

DISEASE_RULES: list[dict[str, Any]] = [
    {
        "id": "dr1",
        "crop": "wheat",
        "disease": "Rust",
        "conditions": "humidity>70 and temp 15-25C",
        "action": "Fungicide protectant; resistant variety",
    },
    {
        "id": "dr2",
        "crop": "tomato",
        "disease": "Late blight",
        "conditions": "cool wet nights",
        "action": "Copper fungicide; improve airflow",
    },
    {
        "id": "dr3",
        "crop": "potato",
        "disease": "Early blight",
        "conditions": "warm dry + leaf wetness",
        "action": "Crop rotation; remove debris",
    },
    {
        "id": "dr4",
        "crop": "rice",
        "disease": "Blast",
        "conditions": "high N + humidity",
        "action": "Balanced fertilizer; resistant cv",
    },
    {
        "id": "dr5",
        "crop": "corn",
        "disease": "Northern leaf blight",
        "conditions": "moderate temp + long dew",
        "action": "Hybrid resistance; residue management",
    },
]


def rotation_plan(current_crop: str, years: int = 3) -> dict[str, Any]:
    key = current_crop.lower().split()[0]
    options = COMPAT.get(key, COMPAT["default"])
    sequence = [current_crop]
    for i in range(years - 1):
        sequence.append(options[i % len(options)])
    return {
        "current": current_crop,
        "years": years,
        "sequence": sequence,
        "rationale": "Break pest/disease cycle; fix nitrogen with legumes; include fallow if arid",
        "engine": "rule-based-mvp",
    }


def yield_prediction(
    crop: str,
    area_ha: float = 1.0,
    water_stress: float = 0.2,
    fertility: float = 0.8,
) -> dict[str, Any]:
    """Simple multiplicative model — not ML."""
    key = crop.lower().split()[0]
    base = BASE_YIELD_T_HA.get(key, BASE_YIELD_T_HA["default"])
    factor = max(0.2, (1.0 - water_stress) * fertility)
    y_ha = round(base * factor, 2)
    return {
        "crop": crop,
        "area_ha": area_ha,
        "yield_t_ha": y_ha,
        "total_t": round(y_ha * area_ha, 2),
        "water_stress": water_stress,
        "fertility": fertility,
        "model": "linear-stress-mvp",
    }


def disease_rules(crop: str | None = None) -> list[dict[str, Any]]:
    if not crop:
        return DISEASE_RULES
    c = crop.lower()
    return [r for r in DISEASE_RULES if r["crop"] in c or c in r["crop"]]
