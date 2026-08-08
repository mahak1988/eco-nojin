"""
Phase C: RothC ΔSOC (t C ha⁻¹) → quality_from_mrv → EcoCoin soil_soc mint.

measured_value = max(0, delta SOC) in tC/ha (credit_type=2).
Optional lab SOC measurement improves Q via field agreement proxy.
"""

from __future__ import annotations

from typing import Any

from apps.api.services.ecocoin_engine import compute_impact_mint, quality_from_mrv
from apps.simulation.rothc_model import run_rothc


def rothc_to_mrv(
    *,
    years: int = 10,
    clay_pct: float = 25.0,
    temp_c: float = 15.0,
    rain_mm_year: float = 500.0,
    et_mm_year: float = 700.0,
    c_input_t_ha_y: float = 1.5,
    soc_t_ha: float = 40.0,
    plant_cover: bool = True,
    lab_soc_final_t_ha: float | None = None,
    region_multiplier: float = 1.0,
) -> dict[str, Any]:
    sim = run_rothc(
        {
            "years": years,
            "clay_pct": clay_pct,
            "temp_c": temp_c,
            "rain_mm_year": rain_mm_year,
            "et_mm_year": et_mm_year,
            "c_input_t_ha_y": c_input_t_ha_y,
            "soc_t_ha": soc_t_ha,
            "plant_cover": plant_cover,
        }
    )
    delta = float(sim["delta"])
    # Only positive sequestration is mintable under soil_soc policy
    measured = max(0.0, delta)

    # Treat lab final SOC vs model final as "field agreement" analog
    model_final = float(sim["soc_final"])
    mrv = quality_from_mrv(
        model_yield_t_ha=model_final if lab_soc_final_t_ha is not None else None,
        field_yield_t_ha=lab_soc_final_t_ha,
        field_data_present=lab_soc_final_t_ha is not None,
        satellite_available=False,
    )
    # Baseline Q when no lab: still allow mint with conservative score
    if lab_soc_final_t_ha is None:
        mrv = {
            "quality_score": 0.95,
            "components": {"model_only": 0.95},
            "inputs": {
                "model_soc_final": model_final,
                "lab_soc_final": None,
                "field_data_present": False,
            },
        }

    mint = compute_impact_mint(
        credit_type=2,  # soil_soc, Fc=40 ECO / tC/ha
        measured_value=measured if measured > 0 else 0.001,  # avoid zero path error when Δ≤0
        quality_score=mrv["quality_score"],
        region_multiplier=region_multiplier,
    )
    if measured <= 0:
        mint = {
            **mint,
            "ok": True,
            "mint_total": 0.0,
            "distribution": {k: 0.0 for k in mint.get("distribution", {})},
            "note": "no_positive_delta_soc",
            "raw_before_scarcity": 0.0,
        }

    return {
        "rothc": {
            "model": sim["model"],
            "soc_initial": sim["soc_initial"],
            "soc_final": sim["soc_final"],
            "delta_tC_ha": sim["delta"],
            "co2_total_t_ha": sim["co2_total_t_ha"],
            "years": years,
            "c_input_t_ha_y": c_input_t_ha_y,
        },
        "mrv": mrv,
        "mint_preview": mint,
        "credit_type": 2,
        "credit_name": "soil_soc",
        "pipeline": "run_rothc → ΔSOC → quality_from_mrv → compute_impact_mint(soil_soc)",
        "disclaimer": "Open RothC-26.3 reimplementation; not official RothC binary.",
    }
