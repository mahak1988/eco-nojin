"""Scenario analysis — compare management options across models."""

from __future__ import annotations

from typing import Any

from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
from apps.simulation.models_swat import run_swat_plus
from apps.simulation.tasks import run_rothc_local


def run_scenarios(scenarios: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """
    Each scenario: {"id", "label", "aquacrop": {...}, "rothc": {...}, "swat": {...}}
    Returns ranked list by composite score (higher better).
    """
    if not scenarios:
        scenarios = [
            {
                "id": "baseline",
                "label": "Baseline irrigation",
                "aquacrop": {"days": 90, "et0_mm_day": 4.5, "rain_mm_day": 0.4},
                "rothc": {"years": 10, "c_input_t_ha_y": 1.2},
                "swat": {"precip_mm_year": 300, "curve_number": 78},
            },
            {
                "id": "deficit_drip",
                "label": "Deficit drip + cover crop",
                "aquacrop": {
                    "days": 90,
                    "et0_mm_day": 4.5,
                    "rain_mm_day": 0.4,
                    "irrig_threshold_frac": 0.75,
                    "kc": 1.0,
                },
                "rothc": {"years": 10, "c_input_t_ha_y": 2.5},
                "swat": {"precip_mm_year": 300, "curve_number": 70, "land_cover": "cropland"},
            },
            {
                "id": "high_input",
                "label": "Full irrigation",
                "aquacrop": {
                    "days": 90,
                    "et0_mm_day": 4.5,
                    "rain_mm_day": 0.4,
                    "irrig_threshold_frac": 0.4,
                },
                "rothc": {"years": 10, "c_input_t_ha_y": 1.0},
                "swat": {"precip_mm_year": 300, "curve_number": 80},
            },
        ]

    results = []
    for sc in scenarios:
        aq = run_aquacrop_advanced(sc.get("aquacrop") or {})
        rt = run_rothc_local(sc.get("rothc") or {})
        sw = run_swat_plus(sc.get("swat") or {})
        # composite: yield↑, irrigation↓, SOC↑, sediment↓
        score = (
            float(aq.get("yield_relative", 0)) * 40
            + max(0.0, 1.0 - float(aq.get("irrigation_need_mm", 0)) / 500.0) * 25
            + max(0.0, float(rt.get("delta", 0)) / 10.0) * 20
            + max(0.0, 1.0 - float(sw["outputs"].get("sediment_t_km2_year", 0)) / 50.0) * 15
        )
        results.append(
            {
                "id": sc.get("id"),
                "label": sc.get("label"),
                "score": round(score, 2),
                "aquacrop": aq,
                "rothc": rt,
                "swat": sw,
            }
        )

    results.sort(key=lambda x: x["score"], reverse=True)
    return {
        "engine": "scenario-mvp",
        "count": len(results),
        "ranking": results,
        "best": results[0]["id"] if results else None,
    }
