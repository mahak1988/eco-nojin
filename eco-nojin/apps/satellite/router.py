"""Satellite API routes — EO + AquaCrop + RothC → EcoCoin MRV."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from apps.satellite.gee_status import probe_gee
from apps.satellite.mrv_bridge import mrv_from_bands, mrv_from_location, mrv_from_ndvi
from apps.satellite.processors.indices import indices_from_mean_reflectance
from apps.satellite.providers.base import BBox
from apps.satellite.service import get_satellite_service
from apps.simulation.aquacrop_mrv import aquacrop_mrv_from_location, aquacrop_to_mrv
from apps.simulation.rothc_mrv import rothc_to_mrv

router = APIRouter(prefix="/api/v1/satellite", tags=["Satellite"])


class BandsRequest(BaseModel):
    red: float = Field(..., ge=0, le=1, description="Sentinel-2 B04 reflectance")
    nir: float = Field(..., ge=0, le=1, description="Sentinel-2 B08 reflectance")
    green: float | None = Field(None, ge=0, le=1)
    blue: float | None = Field(None, ge=0, le=1)
    swir1: float | None = Field(None, ge=0, le=1)


class MrvBridgeRequest(BaseModel):
    red: float | None = Field(None, ge=0, le=1)
    nir: float | None = Field(None, ge=0, le=1)
    green: float | None = Field(None, ge=0, le=1)
    blue: float | None = Field(None, ge=0, le=1)
    ndvi_observed: float | None = Field(None, ge=-1, le=1)
    ndvi_expected: float | None = Field(None, ge=-1, le=1)
    lat: float | None = Field(None, ge=-90, le=90)
    lon: float | None = Field(None, ge=-180, le=180)
    days: int = Field(30, ge=7, le=365)
    model_yield_t_ha: float | None = Field(None, ge=0)
    field_yield_t_ha: float | None = Field(None, ge=0)
    credit_type: int = Field(0, ge=0, le=3)
    measured_value: float = Field(40.0, gt=0)
    region_multiplier: float = Field(1.0, ge=0.8, le=1.3)


class AquaCropMrvRequest(BaseModel):
    crop: str = Field("wheat", description="wheat|maize|rice|...")
    days: int = Field(90, ge=30, le=200)
    area_ha: float = Field(1.0, gt=0, le=10000)
    et0_mm_day: float | None = Field(None, ge=0, le=15)
    rain_mm_day: float = Field(0.5, ge=0, le=50)
    taw_mm: float = Field(100.0, ge=20, le=300)
    ndvi_values: list[float] | None = None
    ndvi_observed: float | None = Field(None, ge=-1, le=1)
    field_yield_t_ha: float | None = Field(None, ge=0)
    lat: float | None = Field(None, ge=-90, le=90)
    lon: float | None = Field(None, ge=-180, le=180)
    credit_type: int = Field(0, ge=0, le=3)
    measured_value: float = Field(40.0, gt=0)
    region_multiplier: float = Field(1.0, ge=0.8, le=1.3)


class RothcMrvRequest(BaseModel):
    years: int = Field(10, ge=1, le=100)
    clay_pct: float = Field(25.0, ge=0, le=80)
    temp_c: float = Field(15.0, ge=-10, le=40)
    rain_mm_year: float = Field(500.0, ge=0, le=3000)
    et_mm_year: float = Field(700.0, ge=0, le=3000)
    c_input_t_ha_y: float = Field(1.5, ge=0, le=20)
    soc_t_ha: float = Field(40.0, ge=1, le=200)
    plant_cover: bool = True
    lab_soc_final_t_ha: float | None = Field(None, ge=0)
    region_multiplier: float = Field(1.0, ge=0.8, le=1.3)


@router.get("/gee/status")
async def gee_status() -> dict[str, Any]:
    return probe_gee()


@router.get("/availability")
async def availability(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(60, ge=7, le=365),
) -> dict[str, Any]:
    end = date.today()
    start = end - timedelta(days=days)
    bbox = BBox.from_point(lat, lon, delta=0.05)
    svc = get_satellite_service()
    return await svc.check_availability(bbox, start, end)


@router.get("/timeseries")
async def timeseries(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(90, ge=7, le=365),
    farm_id: int = Query(0),
) -> dict[str, Any]:
    end = date.today()
    start = end - timedelta(days=days)
    bbox = BBox.from_point(lat, lon, delta=0.05)
    svc = get_satellite_service()
    rows = await svc.get_ndvi_timeseries(farm_id, bbox, start, end)
    return {
        "lat": lat,
        "lon": lon,
        "count": len(rows),
        "provider": rows[0].provider if rows else None,
        "data": [r.to_dict() for r in rows],
    }


@router.get("/ndvi")
async def ndvi_point(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
) -> dict[str, Any]:
    bbox = BBox.from_point(lat, lon, delta=0.02)
    svc = get_satellite_service()
    row = await svc.get_ndvi_image(bbox, date.today() - timedelta(days=15))
    return row.to_dict()


@router.get("/indices")
async def indices(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(60, ge=7, le=365),
) -> dict[str, Any]:
    try:
        from apps.satellite.fetchers.sentinel2_fetcher import fetch_indices

        end = date.today()
        start = end - timedelta(days=days)
        rows = fetch_indices(lat, lon, start, end)
        return {
            "lat": lat,
            "lon": lon,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "count": len(rows),
            "data": [r.__dict__ if hasattr(r, "__dict__") else r for r in rows],
        }
    except Exception as e:
        return {
            "lat": lat,
            "lon": lon,
            "count": 0,
            "error": str(e)[:200],
            "data": [],
        }


@router.post("/indices/from-bands")
async def indices_from_bands(req: BandsRequest) -> dict[str, Any]:
    return indices_from_mean_reflectance(
        {
            "red": req.red,
            "nir": req.nir,
            "green": req.green,
            "blue": req.blue,
            "swir1": req.swir1,
        }
    )


@router.post("/mrv-bridge")
async def mrv_bridge(req: MrvBridgeRequest) -> dict[str, Any]:
    if req.red is not None and req.nir is not None:
        return mrv_from_bands(
            req.red,
            req.nir,
            green=req.green,
            blue=req.blue,
            ndvi_expected=req.ndvi_expected,
            model_yield_t_ha=req.model_yield_t_ha,
            field_yield_t_ha=req.field_yield_t_ha,
            credit_type=req.credit_type,
            measured_value=req.measured_value,
            region_multiplier=req.region_multiplier,
        )
    if req.ndvi_observed is not None:
        return mrv_from_ndvi(
            req.ndvi_observed,
            req.ndvi_expected,
            model_yield_t_ha=req.model_yield_t_ha,
            field_yield_t_ha=req.field_yield_t_ha,
            credit_type=req.credit_type,
            measured_value=req.measured_value,
            region_multiplier=req.region_multiplier,
        )
    if req.lat is not None and req.lon is not None:
        return await mrv_from_location(
            req.lat,
            req.lon,
            days=req.days,
            ndvi_expected=req.ndvi_expected,
            model_yield_t_ha=req.model_yield_t_ha,
            field_yield_t_ha=req.field_yield_t_ha,
            credit_type=req.credit_type,
            measured_value=req.measured_value,
            region_multiplier=req.region_multiplier,
        )
    return {
        "error": "provide red+nir, or ndvi_observed, or lat+lon",
        "examples": {
            "bands": {"red": 0.08, "nir": 0.35},
            "ndvi": {"ndvi_observed": 0.72, "ndvi_expected": 0.75},
            "location": {"lat": 32.65, "lon": 51.67, "days": 30},
        },
    }


@router.get("/mrv-bridge")
async def mrv_bridge_get(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(30, ge=7, le=365),
    measured_value: float = Query(40.0, gt=0),
    credit_type: int = Query(0, ge=0, le=3),
) -> dict[str, Any]:
    return await mrv_from_location(
        lat,
        lon,
        days=days,
        measured_value=measured_value,
        credit_type=credit_type,
    )


@router.post("/aquacrop-mrv")
async def aquacrop_mrv_post(req: AquaCropMrvRequest) -> dict[str, Any]:
    if req.lat is not None and req.lon is not None:
        return await aquacrop_mrv_from_location(
            req.lat,
            req.lon,
            crop=req.crop,
            days=req.days,
            field_yield_t_ha=req.field_yield_t_ha,
            credit_type=req.credit_type,
            measured_value=req.measured_value,
            region_multiplier=req.region_multiplier,
        )
    return aquacrop_to_mrv(
        crop=req.crop,
        days=req.days,
        area_ha=req.area_ha,
        et0_mm_day=req.et0_mm_day,
        rain_mm_day=req.rain_mm_day,
        taw_mm=req.taw_mm,
        ndvi_values=req.ndvi_values,
        ndvi_observed=req.ndvi_observed,
        field_yield_t_ha=req.field_yield_t_ha,
        credit_type=req.credit_type,
        measured_value=req.measured_value,
        region_multiplier=req.region_multiplier,
    )


@router.get("/aquacrop-mrv")
async def aquacrop_mrv_get(
    crop: str = Query("wheat"),
    days: int = Query(90, ge=30, le=200),
    measured_value: float = Query(40.0, gt=0),
    credit_type: int = Query(0, ge=0, le=3),
    lat: float | None = Query(None),
    lon: float | None = Query(None),
) -> dict[str, Any]:
    if lat is not None and lon is not None:
        return await aquacrop_mrv_from_location(
            lat,
            lon,
            crop=crop,
            days=days,
            measured_value=measured_value,
            credit_type=credit_type,
        )
    return aquacrop_to_mrv(
        crop=crop,
        days=days,
        measured_value=measured_value,
        credit_type=credit_type,
    )


@router.post("/rothc-mrv")
async def rothc_mrv_post(req: RothcMrvRequest) -> dict[str, Any]:
    """Phase C: RothC ΔSOC → soil_soc (credit_type=2) mint preview."""
    return rothc_to_mrv(
        years=req.years,
        clay_pct=req.clay_pct,
        temp_c=req.temp_c,
        rain_mm_year=req.rain_mm_year,
        et_mm_year=req.et_mm_year,
        c_input_t_ha_y=req.c_input_t_ha_y,
        soc_t_ha=req.soc_t_ha,
        plant_cover=req.plant_cover,
        lab_soc_final_t_ha=req.lab_soc_final_t_ha,
        region_multiplier=req.region_multiplier,
    )


@router.get("/rothc-mrv")
async def rothc_mrv_get(
    years: int = Query(10, ge=1, le=100),
    c_input_t_ha_y: float = Query(1.5, ge=0, le=20),
    clay_pct: float = Query(25.0, ge=0, le=80),
    soc_t_ha: float = Query(40.0, ge=1, le=200),
) -> dict[str, Any]:
    return rothc_to_mrv(
        years=years,
        c_input_t_ha_y=c_input_t_ha_y,
        clay_pct=clay_pct,
        soc_t_ha=soc_t_ha,
    )


@router.post("/change-detection")
async def change_detection(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(120, ge=30, le=365),
) -> dict[str, Any]:
    end = date.today()
    mid = end - timedelta(days=days // 2)
    start = end - timedelta(days=days)
    bbox = BBox.from_point(lat, lon, delta=0.05)
    svc = get_satellite_service()
    a = await svc.get_ndvi_timeseries(0, bbox, start, mid)
    b = await svc.get_ndvi_timeseries(0, bbox, mid, end)
    ma = sum(r.mean_ndvi for r in a) / max(len(a), 1) if a else 0.0
    mb = sum(r.mean_ndvi for r in b) / max(len(b), 1) if b else 0.0
    delta = mb - ma
    return {
        "period_a": {
            "start": start.isoformat(),
            "end": mid.isoformat(),
            "mean_ndvi": round(ma, 4),
        },
        "period_b": {
            "start": mid.isoformat(),
            "end": end.isoformat(),
            "mean_ndvi": round(mb, 4),
        },
        "delta_ndvi": round(delta, 4),
        "signal": (
            "greening"
            if delta > 0.05
            else ("browning" if delta < -0.05 else "stable")
        ),
    }


@router.get("/fields")
async def fields_stub(farm_id: int | None = None) -> dict[str, Any]:
    return {
        "data": [],
        "farm_id": farm_id,
        "message": "Link farm GeoJSON via /api/v1/farms/:id/geojson",
    }
