"""
simulation schemas | شِما‌های simulation
=====================================
Pydantic models for request/response validation.
"""

import logging

logger = logging.getLogger(__name__)
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SimulationBase(BaseModel):
    """Base schema with shared fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Name")
    description: str | None = Field(None, description="Description")


class SimulationCreate(SimulationBase):
    """Schema for creating a new simulation."""


class SimulationUpdate(BaseModel):
    """Schema for updating an existing simulation (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    is_active: bool | None = None


class SimulationResponse(SimulationBase):
    """Schema for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SimulationListResponse(BaseModel):
    """Paginated list response."""

    items: list[SimulationResponse]
    total: int
    skip: int = 0
    limit: int = 100
