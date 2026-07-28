"""Lightweight multi-model coupling (AquaCrop + RothC) — MVP, not genetic optimizer."""

from __future__ import annotations

from typing import Any

from apps.simulation.tasks import run_aquacrop_local, run_rothc_local


def run_coupled(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    aq = run_aquacrop_local(
        {
            "area_ha": p.get("area_ha", 1.0),
            "et0_mm_day": p.get("et0_mm_day", 4.0),
            "kc": p.get("kc", 1.15),
            "days": p.get("days", 30),
            "rain_mm_total": p.get("rain_mm_total", 20.0),
        }
    )
    rt = run_rothc_local(
        {
            "soc_t_ha": p.get("soc_t_ha", 40.0),
            "clay_pct": p.get("clay_pct", 25.0),
            "temp_c": p.get("temp_c", 18.0),
            "years": p.get("years", 10),
            "c_input_t_ha_y": p.get("c_input_t_ha_y", 1.5),
        }
    )
    return {
        "engine": "coupling-mvp",
        "aquacrop": aq,
        "rothc": rt,
        "narrative": "Irrigation demand from AquaCrop; soil C trajectory from RothC; not a full SWAT+ couple.",
    }
