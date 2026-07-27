"""Farm Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from apps.shared_core.schemas.pagination import ListMeta


class FarmCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    region: Optional[str] = None
    area_ha: Optional[float] = Field(None, ge=0)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    geojson: Optional[str] = None


class FarmUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    region: Optional[str] = None
    area_ha: Optional[float] = Field(None, ge=0)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    geojson: Optional[str] = None
    is_active: Optional[bool] = None


class FarmResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: Optional[int] = None
    region: Optional[str] = None
    area_ha: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    geojson: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class FarmListResponse(BaseModel):
    data: list[FarmResponse]
    meta: ListMeta
