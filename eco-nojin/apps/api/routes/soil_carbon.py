"""Soil carbon simulation API — RothC companion models."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.simulation.science_analysis import attach_analysis
from apps.simulation.soil_carbon import (
    catalog,
    run_century3,
    run_ensemble,
    run_icbm,
    run_yasso_lite,
)

router = APIRouter(prefix="/api/v1/science/soil-carbon", tags=["Soil Carbon"])


class SoilCBody(BaseModel):
    years: int = Field(20, ge=1, le=100)
    soc_t_ha: float = Field(40.0, ge=5, le=200)
    c_input_t_ha_y: float = Field(1.5, ge=0, le=15)
    temp_c: float = Field(15.0, ge=-10, le=40)
    rain_mm_year: float = Field(650.0, ge=0, le=3000)
    et_mm_year: float = Field(700.0, ge=0, le=3000)
    clay_pct: float = Field(25.0, ge=0, le=80)
    plant_cover: bool = True
    persist: bool = False
    # ICBM extras
    young_frac: float | None = Field(None, ge=0.01, le=0.5)
    humification: float | None = Field(None, ge=0.05, le=0.5)


async def _maybe_persist(session: AsyncSession, name: str, params: dict, result: dict, persist: bool) -> dict:
    if not persist:
        return result
    try:
        from apps.simulation.run_store import save_run_async

        row = await save_run_async(session, name, params, result)
        result["run_id"] = row.id
    except Exception as e:
        result["persist_error"] = str(e)[:200]
    return result


@router.get("/catalog")
async def soil_c_catalog() -> dict[str, Any]:
    return catalog()


@router.post("/icbm")
async def post_icbm(
    body: SoilCBody,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    params = body.model_dump(exclude_none=True)
    persist = params.pop("persist", False)
    raw = run_icbm(params)
    result = attach_analysis("rothc", raw)  # similar SOC narrative
    result["analysis"] = {
        **(result.get("analysis") or {}),
        "model_note_fa": "ICBM دو استخر Young/Old؛ مناسب کالیبراسیون سریع.",
    }
    return await _maybe_persist(session, "icbm", params, result, persist)


@router.post("/century3")
async def post_century3(
    body: SoilCBody,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    params = body.model_dump(exclude_none=True)
    persist = params.pop("persist", False)
    result = attach_analysis("rothc", run_century3(params))
    return await _maybe_persist(session, "century3", params, result, persist)


@router.post("/yasso")
async def post_yasso(
    body: SoilCBody,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    params = body.model_dump(exclude_none=True)
    persist = params.pop("persist", False)
    result = attach_analysis("rothc", run_yasso_lite(params))
    return await _maybe_persist(session, "yasso07_lite", params, result, persist)


@router.post("/ensemble")
async def post_ensemble(
    body: SoilCBody,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    params = body.model_dump(exclude_none=True)
    persist = params.pop("persist", False)
    result = run_ensemble(params)
    return await _maybe_persist(session, "soil_carbon_ensemble", params, result, persist)
