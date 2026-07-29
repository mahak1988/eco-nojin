"""
Crop rotation, yield, disease — parameters from agronomic literature ranges.

Yield potentials: order-of-magnitude irrigated systems (FAOSTAT / FAO crop papers).
Water-limited yield uses FAO33-style relative ET response, not ML.
"""

from __future__ import annotations

from typing import Any

# Break disease/pest cycles; legumes for N (standard extension advice)
COMPAT: dict[str, list[str]] = {
    "wheat": ["chickpea", "lentil", "fallow", "potato"],
    "barley": ["lentil", "fallow", "chickpea"],
    "corn": ["soybean", "wheat", "alfalfa"],
    "maize": ["soybean", "wheat", "alfalfa"],
    "rice": ["legume", "fallow"],
    "tomato": ["wheat", "legume", "fallow"],
    "potato": ["cereal", "legume"],
    "default": ["legume", "cereal", "fallow"],
}

# Irrigated attainable yield t/ha (indicative, good management)
BASE_YIELD_T_HA: dict[str, float] = {
    "wheat": 5.5,
    "barley": 4.2,
    "corn": 9.0,
    "maize": 9.0,
    "rice": 6.5,
    "tomato": 55.0,
    "potato": 30.0,
    "soybean": 2.8,
    "chickpea": 1.8,
    "default": 3.5,
}

# Ky mid-season (FAO Irrigation & Drainage Paper 33)
KY: dict[str, float] = {
    "wheat": 1.15,
    "barley": 1.10,
    "corn": 1.25,
    "maize": 1.25,
    "rice": 1.10,
    "tomato": 1.15,
    "potato": 1.10,
    "default": 1.15,
}

DISEASE_RULES: list[dict[str, Any]] = [
    {
        "id": "dr1",
        "crop": "wheat",
        "disease": "Stripe/Leaf rust (Puccinia)",
        "conditions": "RH>70%, T 12–25°C, prolonged leaf wetness",
        "action": "Resistant cultivars; timely triazole/strobilurin if threshold met",
        "source": "CIMMYT/FAO wheat disease guides",
    },
    {
        "id": "dr2",
        "crop": "tomato",
        "disease": "Late blight (Phytophthora infestans)",
        "conditions": "Cool nights, leaf wetness >10h, T 10–20°C",
        "action": "Copper/protectant fungicides; canopy airflow; avoid overhead night irrigation",
        "source": "EPPO / extension IPM",
    },
    {
        "id": "dr3",
        "crop": "potato",
        "disease": "Early blight (Alternaria)",
        "conditions": "Warm days, alternating wet-dry, senescing tissue",
        "action": "Rotation ≥3 years; remove debris; protectant fungicide at row close",
        "source": "CIP / national IPM",
    },
    {
        "id": "dr4",
        "crop": "rice",
        "disease": "Blast (Magnaporthe)",
        "conditions": "High N, high humidity, T 24–28°C",
        "action": "Split N; resistant variety; avoid excessive canopy density",
        "source": "IRRI blast management",
    },
    {
        "id": "dr5",
        "crop": "corn",
        "disease": "Northern corn leaf blight",
        "conditions": "Moderate T, long dew periods",
        "action": "Hybrid resistance; residue management; fungicide if severe",
        "source": "USDA-ARS / extension",
    },
    {
        "id": "dr6",
        "crop": "wheat",
        "disease": "Fusarium head blight",
        "conditions": "Wetness at anthesis, T 20–30°C",
        "action": "Avoid maize-wheat without tillage break; fungicide at flowering if risk high",
        "source": "FAO mycotoxin guidance",
    },
]


def rotation_plan(current_crop: str, years: int = 3) -> dict[str, Any]:
    key = current_crop.lower().split()[0]
    options = COMPAT.get(key, COMPAT["default"])
    sequence = [current_crop]
    for i in range(max(0, years - 1)):
        sequence.append(options[i % len(options)])
    return {
        "current": current_crop,
        "years": years,
        "sequence": sequence,
        "rationale": "Interrupt host-specific pathogens; legumes fix N; fallow in arid systems",
        "engine": "agronomic-rotation-rules",
        "citation": "Standard extension rotation principles",
    }


def yield_prediction(
    crop: str,
    area_ha: float = 1.0,
    water_stress: float = 0.2,
    fertility: float = 0.85,
) -> dict[str, Any]:
    """
    Y ≈ Yx · (1 - Ky·ws) · fertility
    water_stress ∈ [0,1] as relative ET deficit (1 - Ta/Tc).
    """
    key = crop.lower().split()[0]
    yx = BASE_YIELD_T_HA.get(key, BASE_YIELD_T_HA["default"])
    ky = KY.get(key, KY["default"])
    ws = min(1.0, max(0.0, water_stress))
    fert = min(1.0, max(0.2, fertility))
    y_rel = max(0.0, 1.0 - ky * ws)
    y_ha = round(yx * y_rel * fert, 2)
    return {
        "crop": crop,
        "area_ha": area_ha,
        "yx_t_ha": yx,
        "ky": ky,
        "yield_t_ha": y_ha,
        "total_t": round(y_ha * area_ha, 2),
        "water_stress": ws,
        "fertility": fert,
        "model": "fao33_ky_response",
        "citation": "FAO Irrigation & Drainage Paper 33 (Ky)",
    }


def disease_rules(crop: str | None = None) -> list[dict[str, Any]]:
    if not crop:
        return DISEASE_RULES
    c = crop.lower()
    return [r for r in DISEASE_RULES if r["crop"] in c or c in r["crop"]]
