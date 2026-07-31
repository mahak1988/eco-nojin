"""Season planner & phenology helpers."""

from __future__ import annotations

from typing import Any

GROWTH_STAGES: dict[str, list[dict[str, Any]]] = {
    "wheat": [
        {"stage": "emergence", "das": 10, "note": "Coleoptile visible"},
        {"stage": "tillering", "das": 30, "note": "Side shoots"},
        {"stage": "stem_elongation", "das": 50, "note": "Jointing"},
        {"stage": "heading", "das": 80, "note": "Ear emergence"},
        {"stage": "grain_fill", "das": 100, "note": "Milk to dough"},
        {"stage": "maturity", "das": 120, "note": "Harvest window"},
    ],
    "default": [
        {"stage": "establishment", "das": 14, "note": "Stand establishment"},
        {"stage": "vegetative", "das": 40, "note": "Canopy growth"},
        {"stage": "reproductive", "das": 70, "note": "Flowering"},
        {"stage": "maturity", "das": 100, "note": "Harvest"},
    ],
}


def season_plan(crop: str, region: str = "central-iran") -> dict[str, Any]:
    key = crop.lower().split()[0]
    stages = GROWTH_STAGES.get(key, GROWTH_STAGES["default"])
    windows = {
        "wheat": {"sow": "Oct-Nov", "harvest": "May-Jun"},
        "corn": {"sow": "Apr-May", "harvest": "Sep-Oct"},
        "tomato": {"sow": "Mar-Apr", "harvest": "Jun-Sep"},
        "default": {"sow": "spring", "harvest": "autumn"},
    }
    w = windows.get(key, windows["default"])
    return {
        "crop": crop,
        "region": region,
        "sow_window": w["sow"],
        "harvest_window": w["harvest"],
        "stages": stages,
        "engine": "calendar-mvp",
    }


def seed_selection(soil_ph: float = 7.0, water_limited: bool = False) -> dict[str, Any]:
    picks = []
    if 6.0 <= soil_ph <= 8.0:
        picks.append({"crop": "wheat", "reason": "pH suitable; staple"})
    if water_limited:
        picks.append({"crop": "barley", "reason": "more drought tolerant"})
        picks.append({"crop": "sorghum", "reason": "C4 water efficient"})
    else:
        picks.append({"crop": "corn", "reason": "adequate water assumed"})
        picks.append({"crop": "tomato", "reason": "high value if market"})
    return {"soil_ph": soil_ph, "water_limited": water_limited, "recommendations": picks}
