"""
API سناریو، مقایسه و زنجیره‌سازی مدل‌ها
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from apps.shared_core.database.session import get_db_session
from apps.simulation.scenario.models import (
    Scenario, ScenarioResult, ComparisonSession, ModelChain, PRESET_SCENARIOS
)
from apps.simulation.registry import SimulationRegistry

router = APIRouter(prefix="/api/v1/simulation", tags=["🎯 Scenario & Comparison"])


# ─── Pydantic Schemas ───────────────────────────────────────

class ScenarioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    simulator_id: str
    base_params: dict[str, Any] = Field(default_factory=dict)
    scenario_params: dict[str, Any] = Field(default_factory=dict)
    category: Optional[str] = None
    is_preset: bool = False


class ScenarioResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    simulator_id: str
    base_params: dict[str, Any]
    scenario_params: dict[str, Any]
    category: Optional[str]
    is_preset: bool
    created_at: str


class ScenarioRunRequest(BaseModel):
    scenario_id: str
    override_params: Optional[dict[str, Any]] = None


class ScenarioRunResponse(BaseModel):
    scenario_id: str
    scenario_name: str
    metrics: dict[str, Any]
    outputs: Optional[dict[str, Any]]
    execution_time_ms: Optional[float]
    status: str


class ComparisonCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    scenario_ids: list[str] = Field(..., min_length=2, max_length=6)
    comparison_type: str = "side_by_side"
    notes: Optional[str] = None


class ComparisonResponse(BaseModel):
    id: str
    name: str
    scenarios: list[dict[str, Any]]
    comparison_type: str
    comparison_data: dict[str, Any]
    notes: Optional[str]


class ChainConfig(BaseModel):
    name: str
    steps: list[dict[str, Any]] = Field(..., min_length=2)
    # هر step: {"simulator_id": str, "params": dict, "input_from": Optional[str]}


class ChainRunResponse(BaseModel):
    chain_id: str
    chain_name: str
    steps: list[dict[str, Any]]
    final_outputs: dict[str, Any]
    total_execution_time_ms: float


class PresetScenarioResponse(BaseModel):
    simulator_id: str
    scenarios: list[dict[str, Any]]


# ─── Endpoints: سناریوهای پیش‌فرض ──────────────────────────

@router.get("/presets/{simulator_id}", response_model=PresetScenarioResponse)
async def get_preset_scenarios(simulator_id: str):
    """دریافت سناریوهای پیش‌فرض برای یک شبیه‌ساز"""
    presets = PRESET_SCENARIOS.get(simulator_id, [])
    if not presets:
        # اگر پیش‌فرضی نبود، لیست خالی برگردان
        return PresetScenarioResponse(simulator_id=simulator_id, scenarios=[])
    return PresetScenarioResponse(simulator_id=simulator_id, scenarios=presets)


@router.get("/presets", response_model=list[PresetScenarioResponse])
async def get_all_presets():
    """دریافت تمام سناریوهای پیش‌فرض"""
    result = []
    for sim_id, presets in PRESET_SCENARIOS.items():
        result.append(PresetScenarioResponse(simulator_id=sim_id, scenarios=presets))
    return result


# ─── Endpoints: CRUD سناریو ────────────────────────────────

@router.post("/scenarios", response_model=ScenarioResponse, status_code=201)
async def create_scenario(
    data: ScenarioCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """ایجاد سناریوی جدید"""
    # بررسی وجود شبیه‌ساز
    sim = SimulationRegistry.get(data.simulator_id)
    if not sim:
        raise HTTPException(404, f"شبیه‌ساز '{data.simulator_id}' یافت نشد")

    scenario = Scenario(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),  # TODO: از auth واقعی استفاده شود
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
    simulator_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db_session),
):
    """لیست سناریوهای ذخیره‌شده"""
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
async def get_scenario(scenario_id: str, db: AsyncSession = Depends(get_db_session)):
    """دریافت جزئیات یک سناریو"""
    result = await db.execute(
        select(Scenario).where(Scenario.id == uuid.UUID(scenario_id))
    )
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(404, "سناریو یافت نشد")

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
async def delete_scenario(scenario_id: str, db: AsyncSession = Depends(get_db_session)):
    """حذف سناریو"""
    result = await db.execute(
        select(Scenario).where(Scenario.id == uuid.UUID(scenario_id))
    )
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(404, "سناریو یافت نشد")
    await db.delete(scenario)
    await db.commit()


# ─── Endpoints: اجرای سناریو ───────────────────────────────

@router.post("/scenarios/{scenario_id}/run", response_model=ScenarioRunResponse)
async def run_scenario(
    scenario_id: str,
    data: Optional[ScenarioRunRequest] = None,
    db: AsyncSession = Depends(get_db_session),
):
    """اجرای سناریو و ذخیرهٔ نتیجه"""
    # دریافت سناریو
    if scenario_id.startswith("preset_"):
        # سناریوی پیش‌فرض
        preset_id = scenario_id.replace("preset_", "")
        preset = None
        for presets in PRESET_SCENARIOS.values():
            for p in presets:
                if p["id"] == preset_id:
                    preset = p
                    break
        if not preset:
            raise HTTPException(404, "سناریوی پیش‌فرض یافت نشد")
        sim_id = preset.get("simulator_id", "aquacrop")
        params = preset["params"]
        scenario_name = preset["name"]
    else:
        result = await db.execute(
            select(Scenario).where(Scenario.id == uuid.UUID(scenario_id))
        )
        scenario = result.scalar_one_or_none()
        if not scenario:
            raise HTTPException(404, "سناریو یافت نشد")
        sim_id = scenario.simulator_id
        params = {**scenario.base_params, **scenario.scenario_params}
        scenario_name = scenario.name

    # اعمال override
    if data and data.override_params:
        params.update(data.override_params)

    # اجرای شبیه‌سازی
    sim = SimulationRegistry.get(sim_id)
    if not sim:
        raise HTTPException(404, f"شبیه‌ساز '{sim_id}' یافت نشد")

    sim_instance = sim() if isinstance(sim, type) else sim
    sim_result = await sim_instance.run(params)

    # ذخیرهٔ نتیجه
    scenario_result = ScenarioResult(
        id=uuid.uuid4(),
        scenario_id=uuid.UUID(scenario_id) if not scenario_id.startswith("preset_") else uuid.uuid4(),
        metrics=sim_result.metrics or {},
        outputs=sim_result.outputs,
        execution_time_ms=sim_result.execution_time_ms,
        status=sim_result.status.value if hasattr(sim_result.status, 'value') else str(sim_result.status),
    )
    db.add(scenario_result)
    await db.commit()

    return ScenarioRunResponse(
        scenario_id=scenario_id,
        scenario_name=scenario_name,
        metrics=sim_result.metrics or {},
        outputs=sim_result.outputs,
        execution_time_ms=sim_result.execution_time_ms,
        status=sim_result.status.value if hasattr(sim_result.status, 'value') else str(sim_result.status),
    )


# ─── Endpoints: مقایسه ─────────────────────────────────────

@router.post("/comparisons", response_model=ComparisonResponse, status_code=201)
async def create_comparison(
    data: ComparisonCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """ایجاد جلسهٔ مقایسه و اجرای همهٔ سناریوها"""
    comparison_results = []
    comparison_data = {"metrics_comparison": {}, "charts": {}}

    for sid in data.scenario_ids:
        # اجرای هر سناریو
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
            params = preset["params"]
            name = preset["name"]
        else:
            result = await db.execute(
                select(Scenario).where(Scenario.id == uuid.UUID(sid))
            )
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

        scenario_data = {
            "id": sid,
            "name": name,
            "simulator_id": sim_id,
            "metrics": sim_result.metrics or {},
            "outputs": sim_result.outputs,
            "status": sim_result.status.value if hasattr(sim_result.status, 'value') else str(sim_result.status),
        }
        comparison_results.append(scenario_data)

        # جمع‌آوری داده‌های مقایسه
        for metric_key, metric_val in (sim_result.metrics or {}).items():
            if metric_key not in comparison_data["metrics_comparison"]:
                comparison_data["metrics_comparison"][metric_key] = {}
            comparison_data["metrics_comparison"][metric_key][name] = metric_val

    # ذخیرهٔ جلسهٔ مقایسه
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


@router.get("/comparisons", response_model=list[dict])
async def list_comparisons(db: AsyncSession = Depends(get_db_session)):
    """لیست جلسات مقایسه"""
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


# ─── Endpoints: زنجیره‌سازی مدل‌ها ─────────────────────────

@router.post("/chains", response_model=dict, status_code=201)
async def create_chain(data: ChainConfig, db: AsyncSession = Depends(get_db_session)):
    """ایجاد زنجیرهٔ مدل‌ها"""
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
async def run_chain(chain_id: str, db: AsyncSession = Depends(get_db_session)):
    """اجرای زنجیرهٔ مدل‌ها"""
    result = await db.execute(
        select(ModelChain).where(ModelChain.id == uuid.UUID(chain_id))
    )
    chain = result.scalar_one_or_none()
    if not chain:
        raise HTTPException(404, "زنجیره یافت نشد")

    steps = chain.chain_config.get("steps", [])
    step_results = []
    outputs_accumulator = {}
    total_time = 0.0

    for i, step in enumerate(steps):
        sim_id = step.get("simulator_id")
        params = step.get("params", {})
        input_from = step.get("input_from")

        # اعمال خروجی مرحلهٔ قبل به عنوان ورودی
        if input_from and input_from in outputs_accumulator:
            prev_outputs = outputs_accumulator[input_from]
            output_mapping = step.get("output_mapping", {})
            for out_key, in_key in output_mapping.items():
                if out_key in prev_outputs:
                    params[in_key] = prev_outputs[out_key]

        sim = SimulationRegistry.get(sim_id)
        if not sim:
            step_results.append({
                "step": i + 1,
                "simulator_id": sim_id,
                "status": "failed",
                "error": f"شبیه‌ساز '{sim_id}' یافت نشد",
            })
            continue

        sim_instance = sim() if isinstance(sim, type) else sim
        sim_result = await sim_instance.run(params)
        total_time += sim_result.execution_time_ms or 0

        step_result = {
            "step": i + 1,
            "simulator_id": sim_id,
            "status": sim_result.status.value if hasattr(sim_result.status, 'value') else str(sim_result.status),
            "metrics": sim_result.metrics or {},
            "execution_time_ms": sim_result.execution_time_ms,
        }
        step_results.append(step_result)
        outputs_accumulator[sim_id] = sim_result.metrics or {}

    # ذخیرهٔ نتیجه
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


@router.get("/chains", response_model=list[dict])
async def list_chains(db: AsyncSession = Depends(get_db_session)):
    """لیست زنجیره‌های مدل"""
    result = await db.execute(
        select(ModelChain).order_by(ModelChain.created_at.desc())
    )
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
