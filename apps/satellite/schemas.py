"""Pydantic schemas for satellite API."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, Field


class BBoxQuery(BaseModel):
    min_lng: float = Field(..., ge=-180, le=180)
    min_lat: float = Field(..., ge=-90, le=90)
    max_lng: float = Field(..., ge=-180, le=180)
    max_lat: float = Field(..., ge=-90, le=90)


class NDVIPoint(BaseModel):
    date: str
    mean_ndvi: float
    max_ndvi: float = 0
    min_ndvi: float = 0
    std_ndvi: float = 0
    cloud_free_percentage: float = 100
    source: str = "synthetic"
    provider: str = ""


class TimeseriesResponse(BaseModel):
    farm_id: Optional[int] = None
    data: list[NDVIPoint]
    meta: dict[str, Any] = Field(default_factory=dict)


class ChangeDetectionRequest(BaseModel):
    farm_id: Optional[int] = None
    lat: float = 32.65
    lon: float = 51.67
    period_a_start: date
    period_a_end: date
    period_b_start: date
    period_b_end: date


class ChangeDetectionResult(BaseModel):
    mean_ndvi_a: float
    mean_ndvi_b: float
    delta_ndvi: float
    status: str  # improved | degraded | stable
    provider: Optional[str] = None
