"""Scenario / comparison / model-chain API."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.simulation.registry import SimulationRegistry
from apps.simulation.scenario.models import (
    PRESET_SCENARIOS,
    ComparisonSession,
    ModelChain,
    Scenario,
    ScenarioResult,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/simulation", tags=["Scenario & Comparison"])


class ScenarioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    simulator_id: str
    base_params: dict[str, Any] = Field(default_factory=dict)
    scenario_params: dict[str, Any] = Field(default_factory=dict)
    category: str | None = None
    is_preset: bool = False


class ScenarioUpdate(BaseModel):
    """Schema for PATCH /scenarios/{id} - partial updates only."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    base_params: dict[str, Any] | None = None
    scenario_params: dict[str, Any] | None = None
    category: str | None = None


class ScenarioResponse(BaseModel):
    id: str
    name: str
    description: str | None
    simulator_id: str
    base_params: dict[str, Any]
    scenario_params: dict[str, Any]
    category: str | None
    is_preset: bool
    created_at: str


class ScenarioRunRequest(BaseModel):
    scenario_id: str
    override_params: dict[str, Any] | None = None


class ScenarioRunResponse(BaseModel):
    scenario_id: str
    scenario_name: str
    metrics: dict[str, Any]
    outputs: dict[str, Any] | None
    execution_time_ms: float | None
    status: str


class ComparisonCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    scenario_ids: list[str] = Field(..., min_length=2, max_length=6)
    comparison_type: str = "side_by_side"
    notes: str | None = None


class ComparisonResponse(BaseModel):
    id: str
    name: str
    scenarios: list[dict[str, Any]]
    comparison_type: str
    comparison_data: dict[str, Any]
    notes: str | None


class ChainConfig(BaseModel):
    name: str
    steps: list[dict[str, Any]] = Field(..., min_length=2)


class ChainRunResponse(BaseModel):
    chain_id: str
    chain_name: str
    steps: list[dict[str, Any]]
    final_outputs: dict[str, Any]
    total_execution_time_ms: float


class PresetScenarioResponse(BaseModel):
    simulator_id: str
    scenarios: list[dict[str, Any]]


@router.get("/presets/{simulator_id}", response_model=PresetScenarioResponse)
async def get_preset_scenarios(simulator_id: str) -> PresetScenarioResponse:
    presets = PRESET_SCENARIOS.get(simulator_id, [])
    return PresetScenarioResponse(simulator_id=simulator_id, scenarios=presets)


@router.get("/presets", response_model=list[PresetScenarioResponse])
async def get_all_presets() -> list[PresetScenarioResponse]:
    return [
        PresetScenarioResponse(simulator_id=sim_id, scenarios=presets)
        for sim_id, presets in PRESET_SCENARIOS.items()
    ]


@router.post("/scenarios", response_model=ScenarioResponse, status_code=201)
async def create_scenario(
    data: ScenarioCreate,
    db: AsyncSession = Depends(get_db_session),
) -> ScenarioResponse:
    sim = SimulationRegistry.get(data.simulator_id)
    if not sim:
        raise HTTPException(404, f"Simulator '{data.simulator_id}' not found")

    scenario = Scenario(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        name=data.name,
        description=data.description,
        simulator_id=data.simulator_id,
        base_params=data.base_params,
        scenario_params=data.scenario_params,
        category=data.category,
        is_preset=data.is_preset,
    )
    db.add(scenario)
    await db.commit()
    await db.refresh(scenario)

    return ScenarioResponse(
        id=str(scenario.id),
        name=scenario.name,
        description=scenario.description,
        simulator_id=scenario.simulator_id,
        base_params=scenario.base_params,
        scenario_params=scenario.scenario_params,
        category=scenario.category,
        is_preset=scenario.is_preset,
        created_at=scenario.created_at.isoformat(),
    )


@router.get("/scenarios", response_model=list[ScenarioResponse])
async def list_scenarios(
    simulator_id: str | None = Query(None),
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db_session),
) -> list[ScenarioResponse]:
    query = select(Scenario)
    if simulator_id:
        query = query.where(Scenario.simulator_id == simulator_id)
    if category:
        query = query.where(Scenario.category == category)
    query = query.order_by(Scenario.created_at.desc())
    result = await db.execute(query)
    scenarios = result.scalars().all()
    return [
        ScenarioResponse(
            id=str(s.id),
            name=s.name,
            description=s.description,
            simulator_id=s.simulator_id,
            base_params=s.base_params,
            scenario_params=s.scenario_params,
            category=s.category,
            is_preset=s.is_preset,
            created_at=s.created_at.isoformat(),
        )
        for s in scenarios
    ]


@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: str, db: AsyncSession = Depends(get_db_session)
) -> ScenarioResponse:
    result = await db.execute(select(Scenario).where(Scenario.id == uuid.UUID(scenario_id)))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(404, "Scenario not found")
    return ScenarioResponse(
        id=str(scenario.id),
        name=scenario.name,
        description=scenario.description,
        simulator_id=scenario.simulator_id,
        base_params=scenario.base_params,
        scenario_params=scenario.scenario_params,
        category=scenario.category,
        is_preset=scenario.is_preset,
        created_at=scenario.created_at.isoformat(),
    )


@router.delete("/scenarios/{scenario_id}", status_code=204)
async def delete_scenario(scenario_id: str, db: AsyncSession = Depends(get_db_session)) -> None:
    result = await db.execute(select(Scenario).where(Scenario.id == uuid.UUID(scenario_id)))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(404, "Scenario not found")
    await db.delete(scenario)
    await db.commit()


@router.patch("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: str,
    data: ScenarioUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> ScenarioResponse:
    """Partially update a scenario (PATCH semantics)."""
    result = await db.execute(select(Scenario).where(Scenario.id == uuid.UUID(scenario_id)))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(404, "Scenario not found")
    if scenario.is_preset:
        raise HTTPException(403, "Cannot modify preset scenarios")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scenario, field, value)
    scenario.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(scenario)
    return ScenarioResponse(
        id=str(scenario.id),
        name=scenario.name,
        description=scenario.description,
        simulator_id=scenario.simulator_id,
        base_params=scenario.base_params,
        scenario_params=scenario.scenario_params,
        category=scenario.category,
        is_preset=scenario.is_preset,
        created_at=scenario.created_at.isoformat(),
    )


@router.post("/scenarios/{scenario_id}/run", response_model=ScenarioRunResponse)
async def run_scenario(
    scenario_id: str,
    data: ScenarioRunRequest | None = None,
    db: AsyncSession = Depends(get_db_session),
) -> ScenarioRunResponse:
    if scenario_id.startswith("preset_"):
        preset_id = scenario_id.replace("preset_", "")
        preset = None
        for presets in PRESET_SCENARIOS.values():
            for p in presets:
                if p["id"] == preset_id:
                    preset = p
                    break
        if not preset:
            raise HTTPException(404, "Preset not found")
        sim_id = preset.get("simulator_id", "aquacrop")
        params = dict(preset["params"])
        scenario_name = preset["name"]
    else:
        result = await db.execute(select(Scenario).where(Scenario.id == uuid.UUID(scenario_id)))
        scenario = result.scalar_one_or_none()
        if not scenario:
            raise HTTPException(404, "Scenario not found")
        sim_id = scenario.simulator_id
        params = {**scenario.base_params, **scenario.scenario_params}
        scenario_name = scenario.name

    if data and data.override_params:
        params.update(data.override_params)

    sim = SimulationRegistry.get(sim_id)
    if not sim:
        raise HTTPException(404, f"Simulator '{sim_id}' not found")

    sim_instance = sim() if isinstance(sim, type) else sim
    sim_result = await sim_instance.run(params)

    status_val = (
        sim_result.status.value if hasattr(sim_result.status, "value") else str(sim_result.status)
    )

    scenario_result = ScenarioResult(
        id=uuid.uuid4(),
        scenario_id=uuid.UUID(scenario_id)
        if not scenario_id.startswith("preset_")
        else uuid.uuid4(),
        metrics=sim_result.metrics or {},
        outputs=sim_result.outputs,
        execution_time_ms=sim_result.execution_time_ms,
        status=status_val,
    )
    db.add(scenario_result)
    await db.commit()

    return ScenarioRunResponse(
        scenario_id=scenario_id,
        scenario_name=scenario_name,
        metrics=sim_result.metrics or {},
        outputs=sim_result.outputs,
        execution_time_ms=sim_result.execution_time_ms,
        status=status_val,
    )


@router.post("/comparisons", response_model=ComparisonResponse, status_code=201)
async def create_comparison(
    data: ComparisonCreate,
    db: AsyncSession = Depends(get_db_session),
) -> ComparisonResponse:
    comparison_results: list[dict[str, Any]] = []
    comparison_data: dict[str, Any] = {"metrics_comparison": {}, "charts": {}}

    for sid in data.scenario_ids:
        if sid.startswith("preset_"):
            preset_id = sid.replace("preset_", "")
            preset = None
            sim_id = "aquacrop"
            for sim_key, presets in PRESET_SCENARIOS.items():
                for p in presets:
                    if p["id"] == preset_id:
                        preset = p
                        sim_id = sim_key
                        break
            if not preset:
                continue
            params = dict(preset["params"])
            name = preset["name"]
        else:
            result = await db.execute(select(Scenario).where(Scenario.id == uuid.UUID(sid)))
            scenario = result.scalar_one_or_none()
            if not scenario:
                continue
            sim_id = scenario.simulator_id
            params = {**scenario.base_params, **scenario.scenario_params}
            name = scenario.name

        sim = SimulationRegistry.get(sim_id)
        if not sim:
            continue
        sim_instance = sim() if isinstance(sim, type) else sim
        sim_result = await sim_instance.run(params)
        status_val = (
            sim_result.status.value
            if hasattr(sim_result.status, "value")
            else str(sim_result.status)
        )
        comparison_results.append(
            {
                "id": sid,
                "name": name,
                "simulator_id": sim_id,
                "metrics": sim_result.metrics or {},
                "outputs": sim_result.outputs,
                "status": status_val,
            }
        )
        for metric_key, metric_val in (sim_result.metrics or {}).items():
            comparison_data["metrics_comparison"].setdefault(metric_key, {})[name] = metric_val

    session = ComparisonSession(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        name=data.name,
        scenario_ids=data.scenario_ids,
        comparison_type=data.comparison_type,
        notes=data.notes,
    )
    db.add(session)
    await db.commit()

    return ComparisonResponse(
        id=str(session.id),
        name=data.name,
        scenarios=comparison_results,
        comparison_type=data.comparison_type,
        comparison_data=comparison_data,
        notes=data.notes,
    )


@router.get("/comparisons")
async def list_comparisons(db: AsyncSession = Depends(get_db_session)) -> list[dict[str, Any]]:
    result = await db.execute(
        select(ComparisonSession).order_by(ComparisonSession.created_at.desc())
    )
    sessions = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "scenario_ids": s.scenario_ids,
            "comparison_type": s.comparison_type,
            "notes": s.notes,
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]


@router.post("/chains", status_code=201)
async def create_chain(
    data: ChainConfig, db: AsyncSession = Depends(get_db_session)
) -> dict[str, Any]:
    chain = ModelChain(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        name=data.name,
        chain_config={"steps": data.steps},
    )
    db.add(chain)
    await db.commit()
    return {"id": str(chain.id), "name": data.name, "steps": len(data.steps)}


@router.post("/chains/{chain_id}/run", response_model=ChainRunResponse)
async def run_chain(chain_id: str, db: AsyncSession = Depends(get_db_session)) -> ChainRunResponse:
    result = await db.execute(select(ModelChain).where(ModelChain.id == uuid.UUID(chain_id)))
    chain = result.scalar_one_or_none()
    if not chain:
        raise HTTPException(404, "Chain not found")

    steps = chain.chain_config.get("steps", [])
    step_results: list[dict[str, Any]] = []
    outputs_accumulator: dict[str, Any] = {}
    total_time = 0.0

    for i, step in enumerate(steps):
        sim_id = step.get("simulator_id")
        params = dict(step.get("params", {}))
        input_from = step.get("input_from")
        if input_from and input_from in outputs_accumulator:
            prev = outputs_accumulator[input_from]
            for out_key, in_key in step.get("output_mapping", {}).items():
                if out_key in prev:
                    params[in_key] = prev[out_key]

        sim = SimulationRegistry.get(sim_id)
        if not sim:
            step_results.append(
                {
                    "step": i + 1,
                    "simulator_id": sim_id,
                    "status": "failed",
                    "error": f"Simulator '{sim_id}' not found",
                }
            )
            continue

        sim_instance = sim() if isinstance(sim, type) else sim
        sim_result = await sim_instance.run(params)
        total_time += sim_result.execution_time_ms or 0
        status_val = (
            sim_result.status.value
            if hasattr(sim_result.status, "value")
            else str(sim_result.status)
        )
        step_results.append(
            {
                "step": i + 1,
                "simulator_id": sim_id,
                "status": status_val,
                "metrics": sim_result.metrics or {},
                "execution_time_ms": sim_result.execution_time_ms,
            }
        )
        outputs_accumulator[sim_id] = sim_result.metrics or {}

    chain.last_result = {
        "steps": step_results,
        "total_execution_time_ms": total_time,
        "executed_at": datetime.utcnow().isoformat(),
    }
    await db.commit()

    return ChainRunResponse(
        chain_id=str(chain.id),
        chain_name=chain.name,
        steps=step_results,
        final_outputs=outputs_accumulator,
        total_execution_time_ms=total_time,
    )


@router.get("/chains")
async def list_chains(db: AsyncSession = Depends(get_db_session)) -> list[dict[str, Any]]:
    result = await db.execute(select(ModelChain).order_by(ModelChain.created_at.desc()))
    chains = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "steps": len(c.chain_config.get("steps", [])),
            "created_at": c.created_at.isoformat(),
            "last_result": c.last_result,
        }
        for c in chains
    ]
