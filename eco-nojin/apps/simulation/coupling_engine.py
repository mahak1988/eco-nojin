"""Couple AquaCrop conceptual water balance with RothC-26.3 soil C."""

from __future__ import annotations

from typing import Any

from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
from apps.simulation.rothc_model import run_rothc


def run_coupled(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    aq = run_aquacrop_advanced(
        {
            "area_ha": p.get("area_ha", 1.0),
            "et0_mm_day": p.get("et0_mm_day", 4.0),
            "kc": p.get("kc", 1.15),
            "days": p.get("days", 30),
            "rain_mm_day": float(p.get("rain_mm_total", 20.0)) / max(int(p.get("days", 30)), 1),
            "crop": p.get("crop", "wheat"),
        }
    )
    # Link: higher irrigation/residue proxy → slightly higher C input
    c_in = float(p.get("c_input_t_ha_y", 1.5))
    if aq.get("yield_relative", 0) > 0.7:
        c_in *= 1.1
    rt = run_rothc(
        {
            "soc_t_ha": p.get("soc_t_ha", 40.0),
            "clay_pct": p.get("clay_pct", 25.0),
            "temp_c": p.get("temp_c", 18.0),
            "years": p.get("years", 10),
            "c_input_t_ha_y": c_in,
            "rain_mm_year": p.get("rain_mm_year", 400.0),
            "et_mm_year": p.get("et_mm_year", 1200.0),
            "plant_cover": True,
        }
    )
    return {
        "engine": "coupling-aquacrop-rothc",
        "aquacrop": aq,
        "rothc": rt,
        "narrative": (
            "Seasonal water-limited yield from FAO-style balance; "
            "multi-year SOC from RothC compartments; linked via residue C input."
        ),
    }
