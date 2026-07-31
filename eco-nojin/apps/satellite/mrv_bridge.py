"""
Phase A: Satellite → EcoCoin MRV bridge.

Offline-safe path:
  bands or observed NDVI → indices → quality_from_mrv → impact mint preview
Live path (optional):
  satellite service NDVI timeseries mean as ndvi_observed
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from apps.api.services.ecocoin_engine import (
    compute_impact_mint,
    quality_from_mrv,
)
from apps.satellite.processors.indices import (
    canopy_cover_from_ndvi,
    compute_all_indices,
)


def mrv_from_bands(
    red: float,
    nir: float,
    *,
    green: float | None = None,
    blue: float | None = None,
    swir1: float | None = None,
    ndvi_expected: float | None = None,
    model_yield_t_ha: float | None = None,
    field_yield_t_ha: float | None = None,
    credit_type: int = 0,
    measured_value: float = 40.0,
    region_multiplier: float = 1.0,
) -> dict[str, Any]:
    """Pure function: reflectance → indices → Q → mint preview."""
    idx = compute_all_indices(red, nir, green, blue, swir1)
    ndvi_obs = idx["ndvi"]
    ndvi_exp = ndvi_expected if ndvi_expected is not None else max(0.2, ndvi_obs * 0.95)

    mrv = quality_from_mrv(
        ndvi_observed=ndvi_obs,
        ndvi_expected=ndvi_exp,
        model_yield_t_ha=model_yield_t_ha,
        field_yield_t_ha=field_yield_t_ha,
        field_data_present=field_yield_t_ha is not None,
        satellite_available=True,
    )

    mint = compute_impact_mint(
        credit_type=credit_type,
        measured_value=measured_value,
        quality_score=mrv["quality_score"],
        region_multiplier=region_multiplier,
    )

    return {
        "indices": idx,
        "canopy_cover": idx.get("canopy_cover", canopy_cover_from_ndvi(ndvi_obs)),
        "mrv": mrv,
        "mint_preview": mint,
        "pipeline": "bands → indices → quality_from_mrv → compute_impact_mint",
    }


def mrv_from_ndvi(
    ndvi_observed: float,
    ndvi_expected: float | None = None,
    *,
    model_yield_t_ha: float | None = None,
    field_yield_t_ha: float | None = None,
    credit_type: int = 0,
    measured_value: float = 40.0,
    region_multiplier: float = 1.0,
) -> dict[str, Any]:
    ndvi_exp = (
        ndvi_expected if ndvi_expected is not None else max(0.2, ndvi_observed * 0.95)
    )
    mrv = quality_from_mrv(
        ndvi_observed=ndvi_observed,
        ndvi_expected=ndvi_exp,
        model_yield_t_ha=model_yield_t_ha,
        field_yield_t_ha=field_yield_t_ha,
        field_data_present=field_yield_t_ha is not None,
        satellite_available=True,
    )
    mint = compute_impact_mint(
        credit_type=credit_type,
        measured_value=measured_value,
        quality_score=mrv["quality_score"],
        region_multiplier=region_multiplier,
    )
    return {
        "ndvi_observed": ndvi_observed,
        "ndvi_expected": ndvi_exp,
        "canopy_cover": canopy_cover_from_ndvi(ndvi_observed),
        "mrv": mrv,
        "mint_preview": mint,
        "pipeline": "ndvi → quality_from_mrv → compute_impact_mint",
    }


async def mrv_from_location(
    lat: float,
    lon: float,
    *,
    days: int = 30,
    ndvi_expected: float | None = None,
    model_yield_t_ha: float | None = None,
    field_yield_t_ha: float | None = None,
    credit_type: int = 0,
    measured_value: float = 40.0,
    region_multiplier: float = 1.0,
) -> dict[str, Any]:
    """Pull NDVI via satellite service (synthetic/GEE/PC chain) then MRV."""
    from apps.satellite.providers.base import BBox
    from apps.satellite.service import get_satellite_service

    end = date.today()
    start = end - timedelta(days=max(7, days))
    # BBox fields are min_lng / max_lng (not min_lon)
    bbox = BBox.from_point(lat, lon, delta=0.02)
    svc = get_satellite_service()
    rows = await svc.get_ndvi_timeseries(0, bbox, start, end)

    if rows:
        mean_ndvi = sum(r.mean_ndvi for r in rows) / len(rows)
        provider = rows[0].provider
        source = "timeseries_mean"
    else:
        try:
            img = await svc.get_ndvi_image(bbox, end - timedelta(days=10))
            mean_ndvi = float(img.mean_ndvi)
            provider = img.provider
            source = "single_image"
        except Exception as e:
            mean_ndvi = 0.55
            provider = "fallback_default"
            source = f"default_after_error:{type(e).__name__}"

    core = mrv_from_ndvi(
        mean_ndvi,
        ndvi_expected,
        model_yield_t_ha=model_yield_t_ha,
        field_yield_t_ha=field_yield_t_ha,
        credit_type=credit_type,
        measured_value=measured_value,
        region_multiplier=region_multiplier,
    )
    core["location"] = {
        "lat": lat,
        "lon": lon,
        "days": days,
        "provider": provider,
        "source": source,
        "samples": len(rows),
    }
    return core
