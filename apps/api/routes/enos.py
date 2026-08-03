"""ENOS-ISA API — science + fusion + free farmer recommendations."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from apps.core.fusion.hcwf import DataPoint, DataSource, HCWFFusion
from apps.core.models.penman_monteith import WeatherData, calculate_et0
from apps.core.models.scs_cn import calculate_runoff
from apps.core.recommendation.engine import AdaptiveRecommendationEngine

router = APIRouter(prefix="/api/v1/enos", tags=["ENOS-ISA"])


class Et0Request(BaseModel):
    t_max: float
    t_min: float
    rh_mean: float = Field(ge=0, le=100)
    wind_speed_2m: float = Field(ge=0)
    solar_radiation: float = Field(ge=0)
    elevation: float = 1200
    latitude: float = 32.65


class RunoffRequest(BaseModel):
    rainfall_mm: float = Field(ge=0)
    cn: float = Field(ge=30, le=98)
    amc: str = "II"


class FusePoint(BaseModel):
    value: float
    source: str
    confidence: float = 0.7
    spatial_resolution_m: float = 100
    unit: str = "vwc"
    age_hours: float = 0


class FuseRequest(BaseModel):
    points: List[FusePoint]
    target: str = "soil_moisture"
    lat: float = 32.65
    lon: float = 51.67


class RecommendRequest(BaseModel):
    farm_profile: Dict[str, Any] = Field(default_factory=dict)
    model_output: Dict[str, Any] = Field(default_factory=dict)
    weather_forecast: Dict[str, Any] = Field(default_factory=dict)
    data_input: Dict[str, Any] = Field(default_factory=dict)
    language: str = "fa"


@router.get("/health")
async def enos_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "standard": "ENOS-ISA v1.0",
        "modules": ["penman_monteith", "scs_cn", "hcwf", "are"],
        "farmer_cost": "free",
    }


@router.post("/science/et0")
async def science_et0(body: Et0Request) -> Dict[str, Any]:
    w = WeatherData(
        t_max=body.t_max,
        t_min=body.t_min,
        rh_mean=body.rh_mean,
        wind_speed_2m=body.wind_speed_2m,
        solar_radiation=body.solar_radiation,
        elevation=body.elevation,
        latitude=body.latitude,
    )
    et0 = calculate_et0(w)
    return {
        "et0_mm_day": round(et0, 3),
        "method": "FAO-56 Penman-Monteith",
        "reference": "Allen et al. (1998)",
        "confidence": 0.9,
    }


@router.post("/science/runoff")
async def science_runoff(body: RunoffRequest) -> Dict[str, Any]:
    q = calculate_runoff(body.rainfall_mm, body.cn, body.amc)
    return {
        "runoff_mm": round(q, 3),
        "infiltration_mm": round(max(0.0, body.rainfall_mm - q), 3),
        "method": "SCS-CN TR-55",
        "cn": body.cn,
        "amc": body.amc,
        "confidence": 0.78,
    }


@router.post("/fusion/hcwf")
async def fusion_hcwf(body: FuseRequest) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    pts: List[DataPoint] = []
    for p in body.points:
        try:
            src = DataSource(p.source.lower())
        except ValueError:
            src = DataSource.MANUAL
        from datetime import timedelta

        ts = now - timedelta(hours=max(0.0, p.age_hours))
        pts.append(
            DataPoint(
                value=p.value,
                source=src,
                timestamp=ts,
                confidence=p.confidence,
                spatial_resolution_m=p.spatial_resolution_m,
                unit=p.unit,
            )
        )
    fusion = HCWFFusion((body.lat, body.lon))
    result = fusion.fuse(pts, body.target)
    return {
        "value": round(result.value, 5),
        "confidence": round(result.confidence, 4),
        "sources_used": result.sources_used,
        "uncertainty_range": [round(result.uncertainty_range[0], 5), round(result.uncertainty_range[1], 5)],
        "quality_tier": result.quality_tier,
        "algorithm": "HCWF",
        "standard": "ENOS-ISA",
    }


@router.post("/recommendations/generate")
async def recommendations_generate(body: RecommendRequest) -> Dict[str, Any]:
    engine = AdaptiveRecommendationEngine()
    recs = engine.generate_recommendations(
        farm_profile=body.farm_profile,
        data_input=body.data_input,
        model_output=body.model_output,
        weather_forecast=body.weather_forecast,
        language=body.language,
    )
    dicts = [r.to_dict() for r in recs]
    summary = {
        "total_recommendations": len(dicts),
        "critical": sum(1 for r in dicts if r["priority"] == "critical"),
        "urgent": sum(1 for r in dicts if r["priority"] == "urgent"),
        "important": sum(1 for r in dicts if r["priority"] == "important"),
        "routine": sum(1 for r in dicts if r["priority"] == "routine"),
        "farmer_cost": "free",
    }
    return {"recommendations": dicts, "summary": summary}
