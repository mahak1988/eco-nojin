#!/usr/bin/env python3
"""
build_phase_4d.py — فاز ۴.D: یکپارچگی و سناریوهای سازگاری
============================================================
۱. Backend: مدل‌های سناریو و مقایسه
۲. Backend: API endpoints سناریو، مقایسه، زنجیره‌سازی
۳. Frontend: کامپوننت‌های سناریو و مقایسه
۴. Frontend: اتصال به API جدید
"""

import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# ۱. Backend: مدل‌های دیتابیس سناریو
# ═══════════════════════════════════════════════════════════

SCENARIO_MODELS = '''"""
مدل‌های دیتابیس سناریو و مقایسه
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Float, DateTime, ForeignKey, JSON, Text, Boolean, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from apps.shared_core.database.base import Base


class Scenario(Base):
    """سناریوی شبیه‌سازی"""
    __tablename__ = "scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    simulator_id = Column(String(100), nullable=False, index=True)
    base_params = Column(JSON, nullable=False, default=dict)
    scenario_params = Column(JSON, nullable=False, default=dict)
    category = Column(String(100), nullable=True)  # irrigation, climate, soil, management
    is_preset = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    results = relationship("ScenarioResult", back_populates="scenario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scenario {self.name} ({self.simulator_id})>"


class ScenarioResult(Base):
    """نتیجهٔ اجرای سناریو"""
    __tablename__ = "scenario_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("scenarios.id"), nullable=False)
    metrics = Column(JSON, nullable=False, default=dict)
    outputs = Column(JSON, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    status = Column(String(50), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

    scenario = relationship("Scenario", back_populates="results")


class ComparisonSession(Base):
    """جلسهٔ مقایسهٔ سناریوها"""
    __tablename__ = "comparison_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    scenario_ids = Column(JSON, nullable=False, default=list)  # لیست UUID سناریوها
    comparison_type = Column(String(100), default="side_by_side")  # side_by_side, overlay, table
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ComparisonSession {self.name} ({len(self.scenario_ids)} scenarios)>"


class ModelChain(Base):
    """زنجیرهٔ مدل‌ها"""
    __tablename__ = "model_chains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    chain_config = Column(JSON, nullable=False, default=dict)
    # chain_config نمونه:
    # {
    #   "steps": [
    #     {"simulator_id": "climate", "params": {...}, "output_mapping": {"temp_change": "temp_input"}},
    #     {"simulator_id": "aquacrop", "params": {...}, "input_from": "climate"},
    #     {"simulator_id": "cba", "params": {...}, "input_from": "aquacrop"}
    #   ]
    # }
    last_result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ═══════════════════════════════════════════════════════════
# سناریوهای پیش‌فرض (Preset Scenarios)
# ═══════════════════════════════════════════════════════════

PRESET_SCENARIOS = {
    "aquacrop": [
        {
            "id": "drip_irrigation",
            "name": "آبیاری قطره‌ای",
            "name_en": "Drip Irrigation",
            "description": "کاهش ۳۰٪ مصرف آب با سیستم قطره‌ای",
            "category": "irrigation",
            "params": {
                "total_irrigation": 175,  # 250 * 0.7
                "irrigation_efficiency": 0.95,
            },
        },
        {
            "id": "deficit_irrigation",
            "name": "آبیاری کم‌آبی",
            "name_en": "Deficit Irrigation",
            "description": "اعمال ۵۰٪ آبیاری در مرحلهٔ گلدهی",
            "category": "irrigation",
            "params": {
                "total_irrigation": 125,
                "deficit_stage": "flowering",
                "deficit_factor": 0.5,
            },
        },
        {
            "id": "climate_change_rcp45",
            "name": "تغییر اقلیم RCP4.5",
            "name_en": "Climate Change RCP4.5",
            "description": "افزایش ۱.۵ درجه دما و کاهش ۱۰٪ بارندگی",
            "category": "climate",
            "params": {
                "temp_offset": 1.5,
                "precip_factor": 0.9,
                "co2_ppm": 550,
            },
        },
        {
            "id": "climate_change_rcp85",
            "name": "تغییر اقلیم RCP8.5",
            "name_en": "Climate Change RCP8.5",
            "description": "افزایش ۴ درجه دما و کاهش ۲۵٪ بارندگی",
            "category": "climate",
            "params": {
                "temp_offset": 4.0,
                "precip_factor": 0.75,
                "co2_ppm": 900,
            },
        },
        {
            "id": "soil_amendment",
            "name": "اصلاح خاک",
            "name_en": "Soil Amendment",
            "description": "افزایش مادهٔ آلی خاک به ۳٪",
            "category": "soil",
            "params": {
                "field_capacity": 35,
                "wilting_point": 16,
                "organic_matter": 3.0,
            },
        },
        {
            "id": "early_planting",
            "name": "کاشت زودهنگام",
            "name_en": "Early Planting",
            "description": "کاشت ۲ هفته زودتر از تاریخ معمول",
            "category": "management",
            "params": {
                "planting_date": "2024-03-01",
                "planting_offset_days": -14,
            },
        },
        {
            "id": "drought_resistant",
            "name": "رقم مقاوم به خشکی",
            "name_en": "Drought Resistant Variety",
            "description": "استفاده از رقم مقاوم با نیاز آبی کمتر",
            "category": "management",
            "params": {
                "total_irrigation": 150,
                "drought_tolerance": 0.8,
                "root_depth_factor": 1.3,
            },
        },
    ],
    "dssat": [
        {
            "id": "nitrogen_optimization",
            "name": "بهینه‌سازی نیتروژن",
            "name_en": "Nitrogen Optimization",
            "description": "تنظیم مقدار و زمان مصرف نیتروژن",
            "category": "management",
            "params": {
                "n_rate": 180,
                "n_splits": 3,
                "n_timing": "optimized",
            },
        },
        {
            "id": "climate_adaptation",
            "name": "سازگاری اقلیمی",
            "name_en": "Climate Adaptation",
            "description": "تنظیم تاریخ کاشت و رقم بر اساس اقلیم آینده",
            "category": "climate",
            "params": {
                "planting_offset_days": -10,
                "cultivar": "heat_tolerant",
            },
        },
    ],
    "swat": [
        {
            "id": "buffer_strip",
            "name": "نوار حائل",
            "name_en": "Buffer Strip",
            "description": "ایجاد نوار حائل ۱۰ متری در حاشیهٔ رودخانه",
            "category": "management",
            "params": {
                "buffer_width": 10,
                "buffer_efficiency": 0.7,
            },
        },
        {
            "id": "cover_crop",
            "name": "گیاه پوششی",
            "name_en": "Cover Crop",
            "description": "کاشت گیاه پوششی در فصل غیرکشت",
            "category": "soil",
            "params": {
                "cover_crop": True,
                "cover_crop_type": "clover",
                "erosion_reduction": 0.4,
            },
        },
    ],
}
'''

# ═══════════════════════════════════════════════════════════
# ۲. Backend: API Endpoints سناریو و مقایسه
# ═══════════════════════════════════════════════════════════

SCENARIO_API = '''"""
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
'''

# ═══════════════════════════════════════════════════════════
# ۳. Frontend: هوک‌های API سناریو
# ═══════════════════════════════════════════════════════════

SCENARIO_HOOKS = '''/**
 * هوک‌های API سناریو و مقایسه
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../client";
import { ENDPOINTS } from "../endpoints";
import { toast } from "react-hot-toast";

// ─── Types ──────────────────────────────────────────────────

export interface PresetScenario {
  id: string;
  name: string;
  name_en: string;
  description: string;
  category: string;
  params: Record<string, any>;
}

export interface ScenarioResult {
  scenario_id: string;
  scenario_name: string;
  metrics: Record<string, any>;
  outputs?: Record<string, any>;
  execution_time_ms?: number;
  status: string;
}

export interface ComparisonData {
  metrics_comparison: Record<string, Record<string, number>>;
  charts: Record<string, any>;
}

export interface ComparisonResult {
  id: string;
  name: string;
  scenarios: Array<{
    id: string;
    name: string;
    simulator_id: string;
    metrics: Record<string, any>;
    outputs?: Record<string, any>;
    status: string;
  }>;
  comparison_type: string;
  comparison_data: ComparisonData;
  notes?: string;
}

export interface ChainStep {
  step: number;
  simulator_id: string;
  status: string;
  metrics: Record<string, any>;
  execution_time_ms?: number;
  error?: string;
}

export interface ChainResult {
  chain_id: string;
  chain_name: string;
  steps: ChainStep[];
  final_outputs: Record<string, any>;
  total_execution_time_ms: number;
}

// ─── Hooks: سناریوهای پیش‌فرض ──────────────────────────────

export function usePresetScenarios(simulatorId: string) {
  return useQuery({
    queryKey: ["presets", simulatorId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/v1/simulation/presets/${simulatorId}`);
      return data as { simulator_id: string; scenarios: PresetScenario[] };
    },
    enabled: !!simulatorId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useAllPresets() {
  return useQuery({
    queryKey: ["presets", "all"],
    queryFn: async () => {
      const { data } = await apiClient.get("/api/v1/simulation/presets");
      return data as Array<{ simulator_id: string; scenarios: PresetScenario[] }>;
    },
    staleTime: 5 * 60 * 1000,
  });
}

// ─── Hooks: اجرای سناریو ───────────────────────────────────

export function useRunScenario() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      scenarioId: string;
      overrideParams?: Record<string, any>;
    }) => {
      const { data } = await apiClient.post(
        `/api/v1/simulation/scenarios/${params.scenarioId}/run`,
        { override_params: params.overrideParams }
      );
      return data as ScenarioResult;
    },
    onSuccess: (data) => {
      toast.success(`سناریوی «${data.scenario_name}» با موفقیت اجرا شد`);
      queryClient.invalidateQueries({ queryKey: ["scenario-results"] });
    },
    onError: (error: any) => {
      toast.error(`خطا در اجرای سناریو: ${error.message}`);
    },
  });
}

// ─── Hooks: مقایسه ─────────────────────────────────────────

export function useCreateComparison() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      name: string;
      scenarioIds: string[];
      comparisonType?: string;
      notes?: string;
    }) => {
      const { data } = await apiClient.post("/api/v1/simulation/comparisons", {
        name: params.name,
        scenario_ids: params.scenarioIds,
        comparison_type: params.comparisonType || "side_by_side",
        notes: params.notes,
      });
      return data as ComparisonResult;
    },
    onSuccess: (data) => {
      toast.success(`مقایسهٔ «${data.name}» ایجاد شد`);
      queryClient.invalidateQueries({ queryKey: ["comparisons"] });
    },
    onError: (error: any) => {
      toast.error(`خطا در ایجاد مقایسه: ${error.message}`);
    },
  });
}

export function useComparisons() {
  return useQuery({
    queryKey: ["comparisons"],
    queryFn: async () => {
      const { data } = await apiClient.get("/api/v1/simulation/comparisons");
      return data as any[];
    },
  });
}

// ─── Hooks: زنجیره‌سازی ────────────────────────────────────

export function useRunChain() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (chainId: string) => {
      const { data } = await apiClient.post(
        `/api/v1/simulation/chains/${chainId}/run`
      );
      return data as ChainResult;
    },
    onSuccess: (data) => {
      toast.success(`زنجیرهٔ «${data.chain_name}» اجرا شد`);
      queryClient.invalidateQueries({ queryKey: ["chains"] });
    },
    onError: (error: any) => {
      toast.error(`خطا در اجرای زنجیره: ${error.message}`);
    },
  });
}

export function useCreateChain() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      name: string;
      steps: Array<{
        simulator_id: string;
        params: Record<string, any>;
        input_from?: string;
        output_mapping?: Record<string, string>;
      }>;
    }) => {
      const { data } = await apiClient.post("/api/v1/simulation/chains", params);
      return data;
    },
    onSuccess: () => {
      toast.success("زنجیرهٔ مدل ایجاد شد");
      queryClient.invalidateQueries({ queryKey: ["chains"] });
    },
  });
}

export function useChains() {
  return useQuery({
    queryKey: ["chains"],
    queryFn: async () => {
      const { data } = await apiClient.get("/api/v1/simulation/chains");
      return data as any[];
    },
  });
}
'''

# ═══════════════════════════════════════════════════════════
# ۴. Frontend: کامپوننت سناریو
# ═══════════════════════════════════════════════════════════

SCENARIO_PANEL = '''/**
 * پنل سناریوهای سازگاری
 */
import { useState } from "react";
import { FlaskConical, Play, Loader2, Zap, Droplets, CloudSun, Sprout, Settings } from "lucide-react";
import { usePresetScenarios, useRunScenario, type PresetScenario } from "../../hooks/useScenarioApi";

const CATEGORY_ICONS: Record<string, any> = {
  irrigation: Droplets,
  climate: CloudSun,
  soil: Sprout,
  management: Settings,
};

const CATEGORY_COLORS: Record<string, string> = {
  irrigation: "border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100",
  climate: "border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-100",
  soil: "border-green-200 bg-green-50 text-green-700 hover:bg-green-100",
  management: "border-purple-200 bg-purple-50 text-purple-700 hover:bg-purple-100",
};

interface ScenarioPanelProps {
  simulatorId: string;
  baseParams: Record<string, any>;
  onScenarioResult: (result: any) => void;
}

export function ScenarioPanel({ simulatorId, baseParams, onScenarioResult }: ScenarioPanelProps) {
  const { data: presetsData, isLoading } = usePresetScenarios(simulatorId);
  const runScenario = useRunScenario();
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  const scenarios = presetsData?.scenarios || [];
  const filtered = activeCategory
    ? scenarios.filter((s) => s.category === activeCategory)
    : scenarios;

  const categories = [...new Set(scenarios.map((s) => s.category))];

  const handleRun = async (scenario: PresetScenario) => {
    const result = await runScenario.mutateAsync({
      scenarioId: `preset_${scenario.id}`,
      overrideParams: { ...baseParams, ...scenario.params },
    });
    onScenarioResult(result);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8 text-stone-400">
        <Loader2 className="h-5 w-5 animate-spin ml-2" />
        در حال بارگذاری سناریوها...
      </div>
    );
  }

  if (scenarios.length === 0) {
    return (
      <div className="text-center py-8 text-stone-400">
        <FlaskConical className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">سناریوی پیش‌فرضی برای این شبیه‌ساز تعریف نشده است</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* فیلتر دسته‌بندی */}
      {categories.length > 1 && (
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setActiveCategory(null)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              !activeCategory
                ? "bg-stone-800 text-white"
                : "bg-stone-100 text-stone-600 hover:bg-stone-200"
            }`}
          >
            همه
          </button>
          {categories.map((cat) => {
            const Icon = CATEGORY_ICONS[cat] || Settings;
            return (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activeCategory === cat
                    ? "bg-stone-800 text-white"
                    : "bg-stone-100 text-stone-600 hover:bg-stone-200"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {cat === "irrigation" ? "آبیاری" :
                 cat === "climate" ? "اقلیم" :
                 cat === "soil" ? "خاک" : "مدیریت"}
              </button>
            );
          })}
        </div>
      )}

      {/* کارت‌های سناریو */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {filtered.map((scenario) => {
          const Icon = CATEGORY_ICONS[scenario.category] || Settings;
          const colorClass = CATEGORY_COLORS[scenario.category] || CATEGORY_COLORS.management;
          const isRunning = runScenario.isPending && runScenario.variables?.scenarioId === `preset_${scenario.id}`;

          return (
            <button
              key={scenario.id}
              onClick={() => handleRun(scenario)}
              disabled={runScenario.isPending}
              className={`group relative flex flex-col items-start gap-2 rounded-xl border p-4 text-right transition-all duration-200 ${colorClass} ${
                runScenario.isPending ? "opacity-60 cursor-wait" : "cursor-pointer hover:shadow-md hover:-translate-y-0.5"
              }`}
            >
              <div className="flex items-center gap-2 w-full">
                <Icon className="h-4 w-4 shrink-0" />
                <span className="text-sm font-bold">{scenario.name}</span>
                {isRunning && <Loader2 className="h-3.5 w-3.5 animate-spin mr-auto" />}
                {!isRunning && (
                  <Play className="h-3.5 w-3.5 mr-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                )}
              </div>
              <p className="text-xs opacity-75 leading-relaxed">{scenario.description}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
'''

# ═══════════════════════════════════════════════════════════
# ۵. Frontend: کامپوننت مقایسه
# ═══════════════════════════════════════════════════════════

COMPARISON_PANEL = '''/**
 * پنل مقایسهٔ سناریوها
 */
import { useState } from "react";
import { GitCompareArrows, Loader2, BarChart3, Table, Layers } from "lucide-react";
import { useCreateComparison, type ComparisonResult } from "../../hooks/useScenarioApi";

interface ComparisonPanelProps {
  scenarioResults: Array<{
    id: string;
    name: string;
    metrics: Record<string, any>;
  }>;
}

export function ComparisonPanel({ scenarioResults }: ComparisonPanelProps) {
  const createComparison = useCreateComparison();
  const [viewMode, setViewMode] = useState<"table" | "chart">("table");
  const [comparisonResult, setComparisonResult] = useState<ComparisonResult | null>(null);

  if (scenarioResults.length < 2) {
    return (
      <div className="text-center py-8 text-stone-400">
        <GitCompareArrows className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">حداقل ۲ سناریو برای مقایسه اجرا کنید</p>
      </div>
    );
  }

  const handleCompare = async () => {
    const result = await createComparison.mutateAsync({
      name: `مقایسه ${scenarioResults.length} سناریو`,
      scenarioIds: scenarioResults.map((s) => s.id),
      comparisonType: viewMode === "table" ? "table" : "side_by_side",
    });
    setComparisonResult(result);
  };

  // جمع‌آوری تمام متریک‌های یکتا
  const allMetricKeys = [...new Set(
    scenarioResults.flatMap((s) => Object.keys(s.metrics))
  )];

  return (
    <div className="space-y-4">
      {/* کنترل‌ها */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode("table")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              viewMode === "table" ? "bg-stone-800 text-white" : "bg-stone-100 text-stone-600"
            }`}
          >
            <Table className="h-3.5 w-3.5" /> جدولی
          </button>
          <button
            onClick={() => setViewMode("chart")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              viewMode === "chart" ? "bg-stone-800 text-white" : "bg-stone-100 text-stone-600"
            }`}
          >
            <BarChart3 className="h-3.5 w-3.5" /> نموداری
          </button>
        </div>
        <button
          onClick={handleCompare}
          disabled={createComparison.isPending}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50"
        >
          {createComparison.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <GitCompareArrows className="h-4 w-4" />
          )}
          مقایسه کن
        </button>
      </div>

      {/* نمای جدولی */}
      {viewMode === "table" && (
        <div className="overflow-x-auto rounded-xl border border-stone-200">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-stone-50 border-b border-stone-200">
                <th className="px-4 py-3 text-right font-medium text-stone-500">متریک</th>
                {scenarioResults.map((s) => (
                  <th key={s.id} className="px-4 py-3 text-center font-medium text-stone-700">
                    {s.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {allMetricKeys.map((key) => {
                const values = scenarioResults.map((s) => s.metrics[key]);
                const maxVal = Math.max(...values.filter((v) => typeof v === "number"));
                return (
                  <tr key={key} className="border-b border-stone-100 hover:bg-stone-50">
                    <td className="px-4 py-2.5 text-stone-600 font-medium">{key}</td>
                    {scenarioResults.map((s, i) => {
                      const val = s.metrics[key];
                      const isMax = typeof val === "number" && val === maxVal;
                      return (
                        <td
                          key={s.id}
                          className={`px-4 py-2.5 text-center ${
                            isMax ? "font-bold text-emerald-700 bg-emerald-50" : "text-stone-700"
                          }`}
                        >
                          {typeof val === "number" ? val.toFixed(2) : val ?? "—"}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* نمای نموداری */}
      {viewMode === "chart" && (
        <div className="space-y-4">
          {allMetricKeys.slice(0, 4).map((key) => (
            <div key={key} className="rounded-xl border border-stone-200 p-4">
              <h4 className="text-sm font-medium text-stone-600 mb-3">{key}</h4>
              <div className="space-y-2">
                {scenarioResults.map((s) => {
                  const val = s.metrics[key] || 0;
                  const maxVal = Math.max(...scenarioResults.map((r) => r.metrics[key] || 0));
                  const pct = maxVal > 0 ? (val / maxVal) * 100 : 0;
                  return (
                    <div key={s.id} className="flex items-center gap-3">
                      <span className="text-xs text-stone-500 w-24 truncate">{s.name}</span>
                      <div className="flex-1 h-6 bg-stone-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium text-stone-700 w-16 text-left">
                        {typeof val === "number" ? val.toFixed(1) : "—"}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* نتیجهٔ مقایسه */}
      {comparisonResult && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <h4 className="text-sm font-bold text-emerald-800 mb-2">
            ✅ مقایسهٔ «{comparisonResult.name}» ذخیره شد
          </h4>
          <p className="text-xs text-emerald-600">
            {comparisonResult.scenarios.length} سناریو مقایسه شد
          </p>
        </div>
      )}
    </div>
  );
}
'''

# ═══════════════════════════════════════════════════════════
# ۶. Frontend: کامپوننت زنجیره‌سازی
# ═══════════════════════════════════════════════════════════

CHAIN_PANEL = '''/**
 * پنل زنجیره‌سازی مدل‌ها
 */
import { useState } from "react";
import { Link2, Play, Loader2, ArrowDown, CheckCircle2, XCircle, Clock } from "lucide-react";
import { useCreateChain, useRunChain, type ChainResult, type ChainStep } from "../../hooks/useScenarioApi";

interface ChainPanelProps {
  defaultChain?: {
    name: string;
    steps: Array<{
      simulator_id: string;
      params: Record<string, any>;
      input_from?: string;
      output_mapping?: Record<string, string>;
    }>;
  };
}

const SIMULATOR_LABELS: Record<string, string> = {
  climate: "اقلیم",
  aquacrop: "محصول (AquaCrop)",
  dssat: "محصول (DSSAT)",
  cba: "تحلیل اقتصادی (CBA)",
  swat: "آبخیزداری (SWAT)",
  rusle2: "فرسایش خاک (RUSLE2)",
};

export function ChainPanel({ defaultChain }: ChainPanelProps) {
  const createChain = useCreateChain();
  const runChain = useRunChain();
  const [chainId, setChainId] = useState<string | null>(null);
  const [chainResult, setChainResult] = useState<ChainResult | null>(null);

  const chain = defaultChain || {
    name: "زنجیرهٔ اقلیم ← محصول ← اقتصاد",
    steps: [
      {
        simulator_id: "climate",
        params: { scenario: "rcp45", years: 30 },
        output_mapping: { temp_change: "temp_offset" },
      },
      {
        simulator_id: "aquacrop",
        params: { crop: "wheat", total_irrigation: 250 },
        input_from: "climate",
      },
      {
        simulator_id: "cba",
        params: { initial_investment: 1000, annual_cost: 500, discount_rate: 5, years: 10 },
        input_from: "aquacrop",
        output_mapping: { yield_t_ha: "annual_benefit" },
      },
    ],
  };

  const handleCreateAndRun = async () => {
    const created = await createChain.mutateAsync(chain);
    setChainId(created.id);
    const result = await runChain.mutateAsync(created.id);
    setChainResult(result);
  };

  const isRunning = createChain.isPending || runChain.isPending;

  const StepIcon = ({ status }: { status: string }) => {
    if (status === "completed") return <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
    if (status === "failed") return <XCircle className="h-4 w-4 text-red-500" />;
    return <Clock className="h-4 w-4 text-stone-400" />;
  };

  return (
    <div className="space-y-4">
      {/* عنوان و دکمهٔ اجرا */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Link2 className="h-5 w-5 text-stone-500" />
          <h3 className="text-sm font-bold text-stone-700">{chain.name}</h3>
        </div>
        <button
          onClick={handleCreateAndRun}
          disabled={isRunning}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50"
        >
          {isRunning ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          اجرای زنجیره
        </button>
      </div>

      {/* نمایش مراحل */}
      <div className="space-y-0">
        {chain.steps.map((step, i) => {
          const stepResult = chainResult?.steps?.[i];
          return (
            <div key={i}>
              <div className={`flex items-center gap-3 rounded-xl border p-4 ${
                stepResult?.status === "completed" ? "border-emerald-200 bg-emerald-50" :
                stepResult?.status === "failed" ? "border-red-200 bg-red-50" :
                "border-stone-200 bg-white"
              }`}>
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-stone-100 text-xs font-bold text-stone-500">
                  {i + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-stone-700">
                      {SIMULATOR_LABELS[step.simulator_id] || step.simulator_id}
                    </span>
                    {stepResult && <StepIcon status={stepResult.status} />}
                  </div>
                  {step.input_from && (
                    <p className="text-xs text-stone-400 mt-0.5">
                      ← ورودی از: {SIMULATOR_LABELS[step.input_from] || step.input_from}
                    </p>
                  )}
                  {stepResult?.execution_time_ms && (
                    <p className="text-xs text-stone-400 mt-0.5">
                      ⏱ {stepResult.execution_time_ms.toFixed(0)} ms
                    </p>
                  )}
                </div>
                {stepResult?.metrics && Object.keys(stepResult.metrics).length > 0 && (
                  <div className="text-left">
                    {Object.entries(stepResult.metrics).slice(0, 2).map(([k, v]) => (
                      <p key={k} className="text-xs text-stone-500">
                        {k}: <span className="font-medium">{typeof v === "number" ? (v as number).toFixed(2) : v}</span>
                      </p>
                    ))}
                  </div>
                )}
              </div>
              {i < chain.steps.length - 1 && (
                <div className="flex justify-center py-1">
                  <ArrowDown className="h-4 w-4 text-stone-300" />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* نتیجهٔ نهایی */}
      {chainResult && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <h4 className="text-sm font-bold text-emerald-800 mb-2">✅ زنجیره با موفقیت اجرا شد</h4>
          <p className="text-xs text-emerald-600">
            زمان کل: {chainResult.total_execution_time_ms.toFixed(0)} ms |
            مراحل: {chainResult.steps.filter(s => s.status === "completed").length}/{chainResult.steps.length}
          </p>
        </div>
      )}
    </div>
  );
}
'''

# ═══════════════════════════════════════════════════════════
# ۷. به‌روزرسانی endpoints.ts
# ═══════════════════════════════════════════════════════════

ENDPOINTS_ADDITION = '''
  // ─── Scenario & Comparison ────────────────────────────────
  SCENARIO: {
    PRESETS: (simulatorId: string) => `/api/v1/simulation/presets/${simulatorId}`,
    ALL_PRESETS: "/api/v1/simulation/presets",
    SCENARIOS: "/api/v1/simulation/scenarios",
    SCENARIO: (id: string) => `/api/v1/simulation/scenarios/${id}`,
    RUN: (id: string) => `/api/v1/simulation/scenarios/${id}/run`,
    COMPARISONS: "/api/v1/simulation/comparisons",
    CHAINS: "/api/v1/simulation/chains",
    CHAIN_RUN: (id: string) => `/api/v1/simulation/chains/${id}/run`,
  },
'''

# ═══════════════════════════════════════════════════════════
# اجرای اصلی
# ═══════════════════════════════════════════════════════════

def write_file(path: Path, content: str, desc: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  ✓ {desc}")


def update_endpoints(root: Path):
    """افزودن endpointهای سناریو به endpoints.ts"""
    ep_file = root / "packages" / "lib" / "src" / "api" / "endpoints.ts"
    if not ep_file.exists():
        print("  ⚠ endpoints.ts یافت نشد")
        return

    content = ep_file.read_text(encoding="utf-8")
    if "SCENARIO:" in content:
        print("  · endpoints.ts: endpointهای سناریو ازقبل وجود دارد")
        return

    # یافتن آخرین } قبل از export
    # افزودن قبل از آخرین };
    if "};" in content:
        # یافتن آخرین occurrence
        idx = content.rfind("};")
        if idx > 0:
            content = content[:idx] + ENDPOINTS_ADDITION + "\n" + content[idx:]
            ep_file.write_text(content, encoding="utf-8")
            print("  ✓ endpoints.ts: endpointهای سناریو اضافه شد")
    else:
        print("  ⚠ endpoints.ts: ساختار قابل شناسایی نیست")


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

    print("=" * 64)
    print("  فاز ۴.D: یکپارچگی و سناریوهای سازگاری")
    print("=" * 64)

    # ─── Backend ──────────────────────────────────────────────
    print("\n  ── Backend ──")

    # مدل‌های سناریو
    scenario_dir = root / "apps" / "simulation" / "scenario"
    write_file(
        scenario_dir / "__init__.py",
        '"""ماژول سناریو و مقایسه"""\n',
        "apps/simulation/scenario/__init__.py"
    )
    write_file(
        scenario_dir / "models.py",
        SCENARIO_MODELS,
        "apps/simulation/scenario/models.py — مدل‌های سناریو"
    )

    # API سناریو
    write_file(
        scenario_dir / "router.py",
        SCENARIO_API,
        "apps/simulation/scenario/router.py — API سناریو و مقایسه"
    )

    # ─── Frontend ─────────────────────────────────────────────
    print("\n  ── Frontend ──")

    hooks_dir = root / "packages" / "lib" / "src" / "api" / "hooks"
    write_file(
        hooks_dir / "useScenarioApi.ts",
        SCENARIO_HOOKS,
        "packages/lib/src/api/hooks/useScenarioApi.ts — هوک‌های سناریو"
    )

    components_dir = root / "apps" / "web" / "src" / "components" / "scenario"
    write_file(
        components_dir / "ScenarioPanel.tsx",
        SCENARIO_PANEL,
        "apps/web/src/components/scenario/ScenarioPanel.tsx — پنل سناریو"
    )
    write_file(
        components_dir / "ComparisonPanel.tsx",
        COMPARISON_PANEL,
        "apps/web/src/components/scenario/ComparisonPanel.tsx — پنل مقایسه"
    )
    write_file(
        components_dir / "ChainPanel.tsx",
        CHAIN_PANEL,
        "apps/web/src/components/scenario/ChainPanel.tsx — پنل زنجیره‌سازی"
    )
    write_file(
        components_dir / "index.ts",
        'export { ScenarioPanel } from "./ScenarioPanel";\n'
        'export { ComparisonPanel } from "./ComparisonPanel";\n'
        'export { ChainPanel } from "./ChainPanel";\n',
        "apps/web/src/components/scenario/index.ts"
    )

    # ─── به‌روزرسانی endpoints ────────────────────────────────
    print("\n  ─── به‌روزرسانی ───")
    update_endpoints(root)

    # ─── ثبت روتر در main.py ──────────────────────────────────
    main_py = root / "apps" / "main.py"
    if main_py.exists():
        main_content = main_py.read_text(encoding="utf-8")
        if "scenario.router" not in main_content:
            # یافتن محل مناسب برای افزودن
            insert_marker = "# ماژول Validation"
            if insert_marker in main_content:
                scenario_import = '''
# ماژول Scenario & Comparison
try:
    from apps.simulation.scenario.router import router as scenario_router
    app.include_router(scenario_router)
    logger.info("✅ scenario: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  scenario: {e}")

'''
                main_content = main_content.replace(insert_marker, scenario_import + insert_marker)
                main_py.write_text(main_content, encoding="utf-8")
                print("  ✓ main.py: روتر سناریو ثبت شد")
            else:
                print("  ⚠ main.py: محل درج یافت نشد — روتر را دستی اضافه کنید")
        else:
            print("  · main.py: روتر سناریو ازقبل ثبت شده")

    print("\n" + "=" * 64)
    print("  ✅ فاز ۴.D با موفقیت اعمال شد!")
    print("=" * 64)
    print("""
  فایل‌های ایجادشده:
  ├── apps/simulation/scenario/models.py    (مدل‌های سناریو)
  ├── apps/simulation/scenario/router.py    (API سناریو و مقایسه)
  ├── packages/lib/src/api/hooks/useScenarioApi.ts  (هوک‌ها)
  ├── apps/web/src/components/scenario/ScenarioPanel.tsx
  ├── apps/web/src/components/scenario/ComparisonPanel.tsx
  └── apps/web/src/components/scenario/ChainPanel.tsx

  مراحل بعدی:
  ۱. سرور را Restart کنید
  ۲. در SimulatorDetailPage.tsx کامپوننت ScenarioPanel را اضافه کنید
  ۳. در صفحهٔ مقایسه، ComparisonPanel را اضافه کنید
  ۴. تست کنید: GET /api/v1/simulation/presets/aquacrop
""")


if __name__ == "__main__":
    main()