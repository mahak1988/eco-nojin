"""Farm Pydantic schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from apps.shared_core.schemas.pagination import ListMeta


class FarmCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    region: str | None = None
    area_ha: float | None = Field(None, ge=0)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    geojson: str | None = None


class FarmUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    region: str | None = None
    area_ha: float | None = Field(None, ge=0)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    geojson: str | None = None
    is_active: bool | None = None


class FarmResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    owner_id: int | None = None
    region: str | None = None
    area_ha: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    geojson: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class FarmListResponse(BaseModel):
    data: list[FarmResponse]
    meta: ListMeta
