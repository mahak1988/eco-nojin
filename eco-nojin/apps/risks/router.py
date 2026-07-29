"""Agricultural risk prediction API."""

from __future__ import annotations

from fastapi import APIRouter

from apps.risks.engine import RiskInput, RiskReport, evaluate_risks

router = APIRouter(prefix="/api/v1/risks", tags=["Risks"])


@router.post("/predict", response_model=RiskReport)
async def predict_risks(body: RiskInput) -> RiskReport:
    return evaluate_risks(body)


@router.get("/predict/demo", response_model=RiskReport)
async def predict_demo() -> RiskReport:
    return evaluate_risks(
        RiskInput(
            soil_moisture_pct=28,
            precip_7d_mm=2,
            et0_7d_mm=35,
            temp_max_c=38,
            humidity_pct=35,
            days_since_rain=12,
            slope_pct=12,
            vegetation_cover_pct=30,
            crop_category="vegetable",
        )
    )
