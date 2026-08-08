"""Planting & task schemas."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from apps.shared_core.schemas.pagination import ListMeta


class PlantingPlanCreate(BaseModel):
    farm_id: int | None = None
    crop_id: int | None = None
    crop_name: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    season: str | None = None
    planned_start: date | None = None
    planned_end: date | None = None
    area_ha: float | None = Field(None, ge=0)
    seed_rate_kg_ha: float | None = Field(None, ge=0)
    expected_yield_t_ha: float | None = Field(None, ge=0)
    irrigation_method: str | None = None
    notes: str | None = None
    status: str = "planned"


class PlantingPlanResponse(PlantingPlanCreate):
    id: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class PlantingListResponse(BaseModel):
    data: list[PlantingPlanResponse]
    meta: ListMeta


class TaskCreate(BaseModel):
    farm_id: int | None = None
    planting_plan_id: int | None = None
    title: str = Field(..., min_length=1)
    category: str = "general"
    priority: str = "medium"
    status: str = "todo"
    due_date: date | None = None
    assigned_to: str | None = None
    estimated_hours: float | None = Field(None, ge=0)
    description: str | None = None


class TaskResponse(TaskCreate):
    id: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    data: list[TaskResponse]
    meta: ListMeta
