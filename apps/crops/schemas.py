"""Crop schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from apps.shared_core.schemas.pagination import ListMeta


class CropCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    name_fa: Optional[str] = None
    scientific_name: Optional[str] = None
    category: str = "cereal"
    season: Optional[str] = None
    water_need_mm: Optional[float] = Field(None, ge=0)
    growth_days: Optional[int] = Field(None, ge=1)
    description: Optional[str] = None


class CropResponse(BaseModel):
    id: int
    name: str
    name_fa: Optional[str] = None
    scientific_name: Optional[str] = None
    category: str
    season: Optional[str] = None
    water_need_mm: Optional[float] = None
    growth_days: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CropListResponse(BaseModel):
    data: list[CropResponse]
    meta: ListMeta
