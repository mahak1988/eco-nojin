"""Simulation job API — Celery when available, sync fallback."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from apps.simulation.tasks import run_aquacrop_local, run_rothc_local

router = APIRouter(prefix="/api/v1/simulations", tags=["Simulations"])


class AquaCropParams(BaseModel):
    area_ha: float = 1.0
    et0_mm_day: float = 4.0
    kc: float = 1.15
    days: int = Field(30, ge=1, le=365)
    rain_mm_total: float = 20.0
    async_mode: bool = False


class RothCParams(BaseModel):
    soc_t_ha: float = 40.0
    clay_pct: float = 25.0
    temp_c: float = 18.0
    years: int = Field(10, ge=1, le=100)
    c_input_t_ha_y: float = 1.5
    async_mode: bool = False


@router.post("/aquacrop")
async def start_aquacrop(body: AquaCropParams) -> dict[str, Any]:
    params = body.model_dump()
    async_mode = params.pop("async_mode", False)
    if async_mode:
        try:
            from apps.simulation.tasks import run_aquacrop

            task = run_aquacrop.delay(params)
            return {"status": "queued", "task_id": task.id, "model": "aquacrop"}
        except Exception as e:
            result = run_aquacrop_local(params)
            result["celery_error"] = str(e)[:120]
            return result
    return run_aquacrop_local(params)


@router.post("/rothc")
async def start_rothc(body: RothCParams) -> dict[str, Any]:
    params = body.model_dump()
    async_mode = params.pop("async_mode", False)
    if async_mode:
        try:
            from apps.simulation.tasks import run_rothc

            task = run_rothc.delay(params)
            return {"status": "queued", "task_id": task.id, "model": "rothc"}
        except Exception as e:
            result = run_rothc_local(params)
            result["celery_error"] = str(e)[:120]
            return result
    return run_rothc_local(params)


@router.get("/jobs/{task_id}")
async def job_status(task_id: str) -> dict[str, Any]:
    try:
        from apps.shared_core.celery_app import celery_app

        res = celery_app.AsyncResult(task_id)
        out: dict[str, Any] = {"task_id": task_id, "status": res.status}
        if res.successful():
            out["result"] = res.result
        elif res.failed():
            out["error"] = str(res.result)
        return out
    except Exception as e:
        return {"task_id": task_id, "status": "unavailable", "error": str(e)[:120]}
