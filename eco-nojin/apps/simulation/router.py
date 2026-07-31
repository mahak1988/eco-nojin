"""
Simulation API Router
=====================
Exposes all 28 simulators via REST API endpoints.
"""

import logging

logger = logging.getLogger(__name__)
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from apps.simulation.base import SimulationRegistry
from apps.simulation.registry import register_all_simulators

router = APIRouter(tags=["🔬 Simulation"])


class SimulationRunRequest(BaseModel):
    """Request body for running a simulation."""
    simulator_id: str
    parameters: dict[str, Any]


class SimulationRunResponse(BaseModel):
    """Response from a simulation run."""
    run_id: str
    simulator_id: str
    simulator_name: str
    status: str
    outputs: dict[str, Any] = {}
    metrics: dict[str, float] = {}
    charts: dict[str, list] = {}
    error: str | None = None
    execution_time_ms: float = 0.0


@router.get("/simulators", summary="List all available simulators")
async def list_simulators() -> None:
    """Get metadata for all 28 registered simulators."""
    simulators = register_all_simulators()
    return {
        "total": len(simulators),
        "simulators": simulators,
    }


@router.get("/simulators/{simulator_id}", summary="Get simulator details")
async def get_simulator(simulator_id: str) -> None:
    """Get detailed information about a specific simulator."""
    params = SimulationRegistry.get_parameters(simulator_id)
    if not params:
        raise HTTPException(status_code=404, detail=f"Simulator '{simulator_id}' not found")

    sim_class = SimulationRegistry.get(simulator_id)
    sim = sim_class()

    return {
        "metadata": sim.get_metadata(),
        "parameters": params,
    }


@router.post("/run", summary="Run a simulation")
async def run_simulation(request: SimulationRunRequest) -> SimulationRunResponse:
    """Execute a simulation with the given parameters."""
    sim_class = SimulationRegistry.get(request.simulator_id)
    if not sim_class:
        raise HTTPException(
            status_code=404,
            detail=f"Simulator '{request.simulator_id}' not found. Available: {[s['id'] for s in register_all_simulators()]}",
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
async def list_categories() -> None:
    """Get all simulator categories with counts."""
    simulators = register_all_simulators()
    categories: dict[str, list] = {}
    for sim in simulators:
        cat = sim.get("category", "other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(sim["id"])

    return {
        "total_categories": len(categories),
        "categories": {k: {"count": len(v), "simulators": v} for k, v in categories.items()},
    }
