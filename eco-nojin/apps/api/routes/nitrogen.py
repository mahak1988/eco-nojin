"""Soil nitrogen cycle + evaluation metrics API."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from apps.simulation.evaluation_metrics import evaluate_series, metrics_catalog
from apps.simulation.nitrogen_cycle import evaluate_n_series, run_nitrogen_cycle

router = APIRouter(prefix="/api/v1/science", tags=["Nitrogen & Metrics"])


class NCycleBody(BaseModel):
    years: int = Field(10, ge=1, le=50)
    steps_per_year: int = Field(12, ge=1, le=24)
    soc_t_ha: float = Field(40.0, ge=5, le=200)
    cn_ratio: float = Field(12.0, ge=5, le=30)
    n_org_t_ha: float | None = Field(None, ge=0.1, le=30)
    nh4_t_ha: float = Field(0.02, ge=0, le=1)
    no3_t_ha: float = Field(0.05, ge=0, le=1)
    k_mineralization: float = Field(0.04, ge=0.005, le=0.2)
    k_nitrification: float = Field(8.0, ge=0.5, le=30)
    k_denitrification: float = Field(0.3, ge=0.01, le=5)
    k_leaching: float = Field(0.4, ge=0.0, le=5)
    fertilizer_n_t_ha_y: float = Field(0.12, ge=0, le=0.5)
    residue_n_t_ha_y: float = Field(0.03, ge=0, le=0.2)
    max_uptake_t_ha_y: float = Field(0.18, ge=0, le=0.4)
    temp_c: float = Field(15.0, ge=-5, le=40)
    moisture_frac: float = Field(0.55, ge=0.1, le=1.0)
    c_input_t_ha_y: float = Field(1.0, ge=0, le=10)


class EvaluateBody(BaseModel):
    observed: list[float] = Field(..., min_length=2)
    simulated: list[float] = Field(..., min_length=2)
    variable: str = "value"


class NEvaluateBody(BaseModel):
    """Run N cycle then score against annual observations."""
    run: NCycleBody = Field(default_factory=NCycleBody)
    observed: dict[str, list[float]] = Field(
        ...,
        description="e.g. {\"no3\": [0.05, 0.04, ...], \"n_org\": [...]} annual",
    )


@router.get("/metrics/catalog")
async def get_metrics_catalog() -> dict[str, Any]:
    return metrics_catalog()


@router.post("/metrics/evaluate")
async def post_evaluate(body: EvaluateBody) -> dict[str, Any]:
    return evaluate_series(body.observed, body.simulated, variable=body.variable)


@router.post("/nitrogen/run")
async def nitrogen_run(body: NCycleBody) -> dict[str, Any]:
    params = body.model_dump(exclude_none=True)
    return run_nitrogen_cycle(params)


@router.post("/nitrogen/evaluate")
async def nitrogen_evaluate(body: NEvaluateBody) -> dict[str, Any]:
    params = body.run.model_dump(exclude_none=True)
    result = run_nitrogen_cycle(params)
    metrics = evaluate_n_series(result, body.observed)
    return {"run": result, "evaluation": metrics}
