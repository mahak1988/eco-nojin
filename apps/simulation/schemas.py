"""
simulation schemas | شِما‌های simulation
=====================================
Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class SimulationBase(BaseModel):
    """Base schema with shared fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Name")
    description: Optional[str] = Field(None, description="Description")


class SimulationCreate(SimulationBase):
    """Schema for creating a new simulation."""

    pass


class SimulationUpdate(BaseModel):
    """Schema for updating an existing simulation (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


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
