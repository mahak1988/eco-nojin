"""Planting & task schemas."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from apps.shared_core.schemas.pagination import ListMeta


class PlantingPlanCreate(BaseModel):
    farm_id: Optional[int] = None
    crop_id: Optional[int] = None
    crop_name: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    season: Optional[str] = None
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    area_ha: Optional[float] = Field(None, ge=0)
    seed_rate_kg_ha: Optional[float] = Field(None, ge=0)
    expected_yield_t_ha: Optional[float] = Field(None, ge=0)
    irrigation_method: Optional[str] = None
    notes: Optional[str] = None
    status: str = "planned"


class PlantingPlanResponse(PlantingPlanCreate):
    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PlantingListResponse(BaseModel):
    data: list[PlantingPlanResponse]
    meta: ListMeta


class TaskCreate(BaseModel):
    farm_id: Optional[int] = None
    planting_plan_id: Optional[int] = None
    title: str = Field(..., min_length=1)
    category: str = "general"
    priority: str = "medium"
    status: str = "todo"
    due_date: Optional[date] = None
    assigned_to: Optional[str] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None


class TaskResponse(TaskCreate):
    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    data: list[TaskResponse]
    meta: ListMeta
