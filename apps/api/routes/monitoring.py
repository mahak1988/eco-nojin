"""Monitoring / satellite sample endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel

from apps.shared_core.deps import require_write_auth

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])

_sample_data = [
    {"date": "2026-07-01", "ndvi": 0.65, "ndwi": 0.42, "biomass": 120},
    {"date": "2026-07-05", "ndvi": 0.67, "ndwi": 0.44, "biomass": 122},
    {"date": "2026-07-10", "ndvi": 0.69, "ndwi": 0.46, "biomass": 125},
    {"date": "2026-07-15", "ndvi": 0.71, "ndwi": 0.48, "biomass": 128},
]


class SatRequest(BaseModel):
    project_id: str
    lat: float
    lng: float
    area_hectares: float
    start_date: str
    end_date: str


class AIRequest(BaseModel):
    project_id: str
    data_type: str
    timeframe: str


@router.post("/satellite/analyze")
async def analyze_satellite(
    req: SatRequest,
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    ndvi = [d["ndvi"] for d in _sample_data]
    avg = sum(ndvi) / len(ndvi)
    trend = ndvi[-1] - ndvi[0]
    return {
        "indices": {
            "ndvi": {
                "avg": round(avg, 3),
                "trend": round(trend, 3),
                "status": "improving" if trend > 0 else "declining",
            },
            "ndwi": {"avg": 0.45, "trend": 0.02, "status": "stable"},
            "evi": {"avg": 0.58, "trend": 0.01, "status": "improving"},
        },
        "biomass_estimate": {
            "total_tons": round(req.area_hectares * 125, 2),
            "per_hectare": 125,
        },
        "health_score": 85,
        "time_series": _sample_data,
    }


@router.post("/satellite/upload")
async def upload_satellite(
    file: UploadFile = File(...),
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    return {"status": "uploaded", "filename": file.filename, "analysis_started": True}


@router.post("/ai/analyze")
async def ai_analyze(
    req: AIRequest,
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    return {
        "summary": "Ecological status improving",
        "insights": [],
        "predictions": [],
        "recommendations": [],
        "project_id": req.project_id,
    }


@router.get("/ai/models")
async def get_ai_models() -> list[dict[str, Any]]:
    return [
        {"id": "biomass", "name": "Biomass estimate", "accuracy": 0.92},
        {"id": "species", "name": "Species detection", "accuracy": 0.88},
    ]


@router.get("/alerts")
async def get_alerts() -> dict[str, Any]:
    return {"alerts": []}


@router.get("/projects/overview")
async def get_projects_overview() -> dict[str, Any]:
    return {"projects": []}
