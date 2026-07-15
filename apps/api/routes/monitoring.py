"""پایش ماهواره‌ای و AI Econojin"""
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import math

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


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


_sample_data = [
    {"date": "2026-07-01", "ndvi": 0.65, "ndwi": 0.42, "biomass": 120},
    {"date": "2026-07-05", "ndvi": 0.67, "ndwi": 0.44, "biomass": 122},
    {"date": "2026-07-10", "ndvi": 0.69, "ndwi": 0.46, "biomass": 125},
    {"date": "2026-07-15", "ndvi": 0.71, "ndwi": 0.48, "biomass": 128},
]


@router.post("/satellite/analyze")
async def analyze_satellite(req: SatRequest):
    ndvi = [d["ndvi"] for d in _sample_data]
    avg = sum(ndvi) / len(ndvi)
    trend = ndvi[-1] - ndvi[0]
    return {
        "indices": {
            "ndvi": {"avg": round(avg, 3), "trend": round(trend, 3), "status": "improving" if trend > 0 else "declining"},
            "ndwi": {"avg": 0.45, "trend": 0.02, "status": "stable"},
            "evi": {"avg": 0.58, "trend": 0.01, "status": "improving"},
        },
        "biomass_estimate": {"total_tons": round(req.area_hectares * 125, 2), "per_hectare": 125},
        "health_score": 85,
        "time_series": _sample_data,
        "chart_data": {
            "labels": [d["date"] for d in _sample_data],
            "ndvi": [d["ndvi"] for d in _sample_data],
            "ndwi": [d["ndwi"] for d in _sample_data],
            "biomass": [d["biomass"] for d in _sample_data],
        },
    }


@router.post("/satellite/upload")
async def upload_satellite(file: UploadFile = File(...)):
    return {"status": "uploaded", "filename": file.filename, "analysis_started": True}


@router.post("/ai/analyze")
async def ai_analyze(req: AIRequest):
    return {
        "summary": "وضعیت بوم‌شناختی در حال بهبود است. NDVI 3.2٪ افزایش.",
        "insights": [
            {"type": "positive", "message": "افزایش پوشش گیاهی در ۸۵٪ منطقه", "confidence": 0.92},
            {"type": "warning", "message": "کاهش رطوبت در بخش شمالی", "confidence": 0.78},
        ],
        "predictions": [
            {"metric": "biomass", "next_30d": "+2.5%", "confidence": 0.85},
            {"metric": "biodiversity", "next_90d": "+5.1%", "confidence": 0.79},
        ],
        "recommendations": [
            "افزایش نظارت در بخش شمالی",
            "کاشت گونه‌های مقاوم به خشکی",
        ],
    }


@router.get("/ai/models")
async def get_ai_models():
    return [
        {"id": "biomass", "name": "برآورد زیست‌توده", "accuracy": 0.92},
        {"id": "species", "name": "تشخیص گونه", "accuracy": 0.88},
        {"id": "deforestation", "name": "تشخیص جنگل‌زدایی", "accuracy": 0.95},
        {"id": "carbon", "name": "پیش‌بینی کربن", "accuracy": 0.87},
    ]


@router.get("/alerts")
async def get_alerts():
    return {"alerts": [
        {"id": "AL001", "type": "deforestation", "severity": "high",
         "message": "کاهش پوشش در ۵ هکتار", "timestamp": "2026-07-14T08:00:00"},
        {"id": "AL002", "type": "moisture", "severity": "medium",
         "message": "کاهش رطوبت خاک", "timestamp": "2026-07-14T06:00:00"},
    ]}


@router.get("/projects/overview")
async def get_projects_overview():
    return {"projects": [
        {"id": "amazon-north", "name": "آمازون شمالی", "hectares": 45200, "ndvi": 0.72, "health": 88},
        {"id": "kenya-grassland", "name": "مراتع کنیا", "hectares": 28900, "ndvi": 0.58, "health": 75},
        {"id": "indonesia-mangrove", "name": "حرای اندونزی", "hectares": 18700, "ndvi": 0.81, "health": 92},
    ]}
