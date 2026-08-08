"""
Simulation API Router
=====================
Exposes simulators via REST. Supports ?lang=en|fa|ar for localized labels.
"""

import logging
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from apps.simulation.base import SimulationRegistry
from apps.simulation.i18n_catalog import localize_sim_list, localize_sim_meta, normalize_lang
from apps.simulation.registry import register_all_simulators

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Simulation"])


class SimulationRunRequest(BaseModel):
    simulator_id: str
    parameters: dict[str, Any]


class SimulationRunResponse(BaseModel):
    run_id: str
    simulator_id: str
    simulator_name: str
    status: str
    outputs: dict[str, Any] = {}
    metrics: dict[str, float] = {}
    charts: dict[str, list] = {}
    error: str | None = None
    execution_time_ms: float = 0.0


def _resolve_lang(lang: str | None, accept_language: str | None) -> str:
    if lang:
        return normalize_lang(lang)
    if accept_language:
        # e.g. "fa-IR,fa;q=0.9,en;q=0.8"
        first = accept_language.split(",")[0].strip()
        return normalize_lang(first)
    return "en"


@router.get("/simulators", summary="List all available simulators")
async def list_simulators(
    lang: str | None = Query(None, description="en | fa | ar"),
    accept_language: str | None = Header(None, alias="Accept-Language"),
):
    simulators = register_all_simulators()
    locale = _resolve_lang(lang, accept_language)
    localized = localize_sim_list(simulators, locale)
    return {
        "total": len(localized),
        "lang": locale,
        "simulators": localized,
    }


@router.get("/simulators/{simulator_id}", summary="Get simulator details")
async def get_simulator(
    simulator_id: str,
    lang: str | None = Query(None),
    accept_language: str | None = Header(None, alias="Accept-Language"),
):
    params = SimulationRegistry.get_parameters(simulator_id)
    if not params:
        raise HTTPException(status_code=404, detail=f"Simulator '{simulator_id}' not found")

    sim_class = SimulationRegistry.get(simulator_id)
    if not sim_class:
        raise HTTPException(status_code=404, detail=f"Simulator '{simulator_id}' not found")
    sim = sim_class()
    locale = _resolve_lang(lang, accept_language)
    meta = localize_sim_meta(sim.get_metadata(), locale)

    return {
        "metadata": meta,
        "parameters": params,
        "lang": locale,
    }


@router.post("/run", summary="Run a simulation")
async def run_simulation(request: SimulationRunRequest) -> SimulationRunResponse:
    sim_class = SimulationRegistry.get(request.simulator_id)
    if not sim_class:
        raise HTTPException(
            status_code=404,
            detail=f"Simulator '{request.simulator_id}' not found",
        )

    sim = sim_class()
    result = await sim.run(request.parameters)

    return SimulationRunResponse(
        run_id=result.run_id,
        simulator_id=result.simulator_id,
        simulator_name=result.simulator_name,
        status=result.status.value,
        outputs=result.outputs,
        metrics=result.metrics,
        charts=result.charts,
        error=result.error,
        execution_time_ms=result.execution_time_ms,
    )


@router.get("/categories", summary="List simulator categories")
async def list_categories(
    lang: str | None = Query(None),
    accept_language: str | None = Header(None, alias="Accept-Language"),
):
    from apps.simulation.i18n_catalog import CATEGORY_I18N

    simulators = register_all_simulators()
    locale = _resolve_lang(lang, accept_language)
    categories: dict[str, list] = {}
    for sim in simulators:
        cat = sim.get("category", "other")
        categories.setdefault(cat, []).append(sim["id"])

    return {
        "total_categories": len(categories),
        "lang": locale,
        "categories": {
            k: {
                "count": len(v),
                "simulators": v,
                "label": (CATEGORY_I18N.get(k) or CATEGORY_I18N["other"]).get(locale)
                or (CATEGORY_I18N.get(k) or CATEGORY_I18N["other"])["en"],
            }
            for k, v in categories.items()
        },
    }
