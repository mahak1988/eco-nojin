"""Phase 5 routes mounted from science package — e2e MRV.

Imported by apps.api.routes.science if present; also loadable standalone.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(tags=["Phase5 E2E MRV"])


class E2EBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    crop: str = "wheat"
    lat: float = 32.65
    lon: float = 51.67
    days: int = Field(90, ge=7, le=365)
    area_ha: float = 1.0
    et0_mm_day: float = 5.2
    rain_mm_day: float = 0.3
    soc_t_ha: float = 38.0
    c_input_t_ha_y: float = 1.8
    clay_pct: float = 28.0
    rothc_years: int = Field(10, ge=1, le=100)
    engine: str = "conceptual"
    use_live_ndvi: bool = False
    field_yield_t_ha: Optional[float] = None
    lab_soc_t_ha: Optional[float] = None
    measured_value: float = 40.0
    credit_type_factor: float = 25.0
    region_multiplier: float = 1.0
    scarcity: float = 1.0


@router.post("/e2e-mrv")
async def e2e_mrv(request: Request) -> dict[str, Any]:
    from apps.simulation.science_pipeline_e2e import run_pipeline_async, run_pipeline_sync

    try:
        raw = await request.json()
    except Exception:
        raw = {}
    if not isinstance(raw, dict):
        raw = {}
    body = E2EBody.model_validate(raw)
    params = body.model_dump()
    if params.get("use_live_ndvi"):
        return await run_pipeline_async(params)
    return run_pipeline_sync(params)


@router.get("/e2e-mrv/isfahan-wheat")
async def e2e_isfahan_wheat(use_live_ndvi: bool = False, engine: str = "conceptual") -> dict[str, Any]:
    from apps.simulation.science_pipeline_e2e import ISFAHAN_WHEAT, run_pipeline_async, run_pipeline_sync

    params = {**ISFAHAN_WHEAT, "use_live_ndvi": use_live_ndvi, "engine": engine}
    if use_live_ndvi:
        return await run_pipeline_async(params)
    return run_pipeline_sync(params)
