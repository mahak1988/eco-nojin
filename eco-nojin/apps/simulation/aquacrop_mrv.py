"""
Phase B: AquaCrop (conceptual FAO) → quality_from_mrv → EcoCoin mint preview.

Pipeline:
  1) Optional NDVI → canopy_cover series
  2) run_aquacrop_advanced (soil water + Ky yield response)
  3) model yield + optional field yield + NDVI → quality_from_mrv
  4) compute_impact_mint

No external aquacrop package required — uses in-repo process model.
"""

from __future__ import annotations

from typing import Any, Optional

from apps.api.services.ecocoin_engine import compute_impact_mint, quality_from_mrv
from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
from apps.simulation.ndvi_canopy import ndvi_to_canopy


def aquacrop_to_mrv(
    *,
    crop: str = "wheat",
    days: int = 90,
    area_ha: float = 1.0,
    et0_mm_day: Optional[float] = None,
    rain_mm_day: float = 0.5,
    taw_mm: float = 100.0,
    total_irrigation_mm: Optional[float] = None,
    ndvi_values: Optional[list[float]] = None,
    ndvi_observed: Optional[float] = None,
    ndvi_expected: Optional[float] = None,
    field_yield_t_ha: Optional[float] = None,
    credit_type: int = 0,
    measured_value: float = 40.0,
    region_multiplier: float = 1.0,
) -> dict[str, Any]:
    """Pure offline path: params → AquaCrop metrics → Q → mint."""
    canopy: Optional[list[float]] = None
    if ndvi_values:
        canopy = ndvi_to_canopy(ndvi_values)
        if ndvi_observed is None:
            ndvi_observed = sum(ndvi_values) / len(ndvi_values)

    params: dict[str, Any] = {
        "crop": crop,
        "days": days,
        "area_ha": area_ha,
        "rain_mm_day": rain_mm_day,
        "taw_mm": taw_mm,
    }
    if et0_mm_day is not None:
        params["et0_mm_day"] = et0_mm_day
    if canopy is not None:
        params["canopy_cover"] = canopy
    # Approximate irrigation by lowering threshold when total budget given
    if total_irrigation_mm is not None and days > 0:
        params["irrig_threshold_frac"] = 0.45

    sim = run_aquacrop_advanced(params)
    model_yield = float(sim["yield_t_ha"])

    # Expected NDVI from model relative yield (proxy when not provided)
    if ndvi_observed is None:
        ndvi_observed = 0.25 + 0.55 * float(sim["yield_relative"])
    if ndvi_expected is None:
        ndvi_expected = max(0.2, ndvi_observed * 0.95 + 0.05 * float(sim["yield_relative"]))

    mrv = quality_from_mrv(
        ndvi_observed=ndvi_observed,
        ndvi_expected=ndvi_expected,
        model_yield_t_ha=model_yield,
        field_yield_t_ha=field_yield_t_ha,
        field_data_present=field_yield_t_ha is not None,
        satellite_available=bool(ndvi_values) or ndvi_observed is not None,
    )

    mint = compute_impact_mint(
        credit_type=credit_type,
        measured_value=measured_value,
        quality_score=mrv["quality_score"],
        region_multiplier=region_multiplier,
    )

    return {
        "aquacrop": {
            "model": sim["model"],
            "crop": sim["crop"],
            "days": sim["days"],
            "yield_t_ha": sim["yield_t_ha"],
            "yield_relative": sim["yield_relative"],
            "relative_transpiration": sim["relative_transpiration"],
            "etc_mm": sim["etc_mm"],
            "irrigation_need_mm": sim["irrigation_need_mm"],
            "ndvi_calibrated": sim["ndvi_calibrated"],
        },
        "mrv": mrv,
        "mint_preview": mint,
        "pipeline": "aquacrop_advanced → quality_from_mrv → compute_impact_mint",
        "disclaimer": (
            "Conceptual FAO AquaCrop-style process model for decision support; "
            "not the official FAO AquaCrop binary."
        ),
    }


async def aquacrop_mrv_from_location(
    lat: float,
    lon: float,
    *,
    crop: str = "wheat",
    days: int = 90,
    field_yield_t_ha: Optional[float] = None,
    credit_type: int = 0,
    measured_value: float = 40.0,
    region_multiplier: float = 1.0,
) -> dict[str, Any]:
    """Pull NDVI canopy at location then run aquacrop_to_mrv."""
    from apps.simulation.ndvi_canopy import fetch_ndvi_canopy_async

    eo = await fetch_ndvi_canopy_async(lat, lon, days=min(days, 90))
    core = aquacrop_to_mrv(
        crop=crop,
        days=days,
        ndvi_values=eo.get("ndvi") or None,
        field_yield_t_ha=field_yield_t_ha,
        credit_type=credit_type,
        measured_value=measured_value,
        region_multiplier=region_multiplier,
    )
    core["location"] = {
        "lat": lat,
        "lon": lon,
        "provider": eo.get("provider"),
        "ndvi_samples": eo.get("count", 0),
    }
    return core
