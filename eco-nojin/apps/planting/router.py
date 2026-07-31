"""Planting plans & tasks API + season helpers."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.planting.models import FarmTask, PlantingPlan
from apps.planting.schemas import (
    PlantingListResponse,
    PlantingPlanCreate,
    PlantingPlanResponse,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
)
from apps.planting.season import GROWTH_STAGES, season_plan, seed_selection
from apps.shared_core.database.session import get_db_session
from apps.shared_core.schemas.pagination import build_meta, page_to_offset

router = APIRouter(tags=["Planting"])


@router.get("/api/v1/planting/season-plan")
async def get_season_plan(
    crop: str = Query("wheat"),
    region: str = Query("central-iran"),
):
    return season_plan(crop, region)


@router.post("/api/v1/planting/seed-selection")
async def post_seed_selection(
    soil_ph: float = Query(7.0),
    water_limited: bool = Query(False),
):
    return seed_selection(soil_ph, water_limited)


@router.get("/api/v1/planting/growth-stages")
async def growth_stages(crop: str = Query("wheat")):
    key = crop.lower().split()[0]
    return {"crop": crop, "stages": GROWTH_STAGES.get(key, GROWTH_STAGES["default"])}


@router.get("/api/v1/planting-plans", response_model=PlantingListResponse)
async def list_plans(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    farm_id: int | None = None,
    session: AsyncSession = Depends(get_db_session),
):
    q = select(PlantingPlan).where(PlantingPlan.is_deleted.is_(False))
    cq = select(func.count()).select_from(PlantingPlan).where(PlantingPlan.is_deleted.is_(False))
    if farm_id is not None:
        q = q.where(PlantingPlan.farm_id == farm_id)
        cq = cq.where(PlantingPlan.farm_id == farm_id)
    total = int((await session.execute(cq)).scalar_one())
    rows = (
        await session.execute(
            q.order_by(PlantingPlan.planned_start.desc().nullslast(), PlantingPlan.id.desc())
            .offset(page_to_offset(page, size))
            .limit(size)
        )
    ).scalars().all()
    return PlantingListResponse(
        data=[PlantingPlanResponse.model_validate(r) for r in rows],
        meta=build_meta(total, page, size),
    )


@router.post(
    "/api/v1/planting-plans",
    response_model=PlantingPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_plan(body: PlantingPlanCreate, session: AsyncSession = Depends(get_db_session)):
    plan = PlantingPlan(**body.model_dump())
    session.add(plan)
    await session.flush()
    await session.refresh(plan)
    return PlantingPlanResponse.model_validate(plan)


@router.get("/api/v1/planting-plans/{plan_id}", response_model=PlantingPlanResponse)
async def get_plan(plan_id: int, session: AsyncSession = Depends(get_db_session)):
    r = await session.execute(
        select(PlantingPlan).where(PlantingPlan.id == plan_id, PlantingPlan.is_deleted.is_(False))
    )
    plan = r.scalar_one_or_none()
    if not plan:
        raise HTTPException(404, "Plan not found")
    return PlantingPlanResponse.model_validate(plan)


@router.get("/api/v1/tasks", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    farm_id: int | None = None,
    status_filter: str | None = Query(None, alias="status"),
    session: AsyncSession = Depends(get_db_session),
):
    q = select(FarmTask).where(FarmTask.is_deleted.is_(False))
    cq = select(func.count()).select_from(FarmTask).where(FarmTask.is_deleted.is_(False))
    if farm_id is not None:
        q = q.where(FarmTask.farm_id == farm_id)
        cq = cq.where(FarmTask.farm_id == farm_id)
    if status_filter:
        q = q.where(FarmTask.status == status_filter)
        cq = cq.where(FarmTask.status == status_filter)
    total = int((await session.execute(cq)).scalar_one())
    rows = (
        await session.execute(
            q.order_by(FarmTask.due_date.asc().nullslast(), FarmTask.id.desc())
            .offset(page_to_offset(page, size))
            .limit(size)
        )
    ).scalars().all()
    return TaskListResponse(
        data=[TaskResponse.model_validate(r) for r in rows],
        meta=build_meta(total, page, size),
    )


@router.post("/api/v1/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(body: TaskCreate, session: AsyncSession = Depends(get_db_session)):
    task = FarmTask(**body.model_dump())
    session.add(task)
    await session.flush()
    await session.refresh(task)
    return TaskResponse.model_validate(task)


@router.patch("/api/v1/tasks/{task_id}", response_model=TaskResponse)
async def patch_task(
    task_id: int,
    body: TaskCreate,
    session: AsyncSession = Depends(get_db_session),
):
    r = await session.execute(
        select(FarmTask).where(FarmTask.id == task_id, FarmTask.is_deleted.is_(False))
    )
    task = r.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    await session.flush()
    await session.refresh(task)
    return TaskResponse.model_validate(task)
