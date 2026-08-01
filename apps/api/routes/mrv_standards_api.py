"""MRV standards API — L1/L2/L3 quality and issuable mint preview."""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from apps.api.services.mrv_standards import compute_issuable, quality_from_mrv_v2

router = APIRouter(prefix="/mrv", tags=["mrv-standards"])


class QualityV2Request(BaseModel):
    ndvi_observed: Optional[float] = None
    ndvi_expected: Optional[float] = None
    model_yield_t_ha: Optional[float] = None
    field_yield_t_ha: Optional[float] = None
    model_soc_t_ha: Optional[float] = None
    lab_soc_t_ha: Optional[float] = None
    field_data_present: bool = False
    satellite_available: bool = False
    model_present: bool = False
    additionality_score: float = Field(1.0, ge=0, le=1)
    leakage_risk: float = Field(0.0, ge=0, le=0.5)


class IssuableRequest(BaseModel):
    measured_value: float = Field(..., gt=0)
    credit_factor: float = Field(25.0, gt=0)
    region_multiplier: float = Field(1.0, ge=0.8, le=1.3)
    scarcity: float = Field(1.0, ge=0.2, le=1.0)
    quality: QualityV2Request


@router.post("/quality-v2")
async def post_quality_v2(req: QualityV2Request) -> dict[str, Any]:
    return quality_from_mrv_v2(**req.model_dump())


@router.post("/issuable")
async def post_issuable(req: IssuableRequest) -> dict[str, Any]:
    mrv = quality_from_mrv_v2(**req.quality.model_dump())
    out = compute_issuable(
        measured_value=req.measured_value,
        credit_factor=req.credit_factor,
        mrv=mrv,
        region_multiplier=req.region_multiplier,
        scarcity=req.scarcity,
    )
    return {"mrv": mrv, "issuance": out}
