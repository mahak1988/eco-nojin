"""
shared_core schemas | شِما‌های shared_core
=====================================
Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class SharedCoreBase(BaseModel):
    """Base schema with shared fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Name")
    description: Optional[str] = Field(None, description="Description")


class SharedCoreCreate(SharedCoreBase):
    """Schema for creating a new shared_core."""

    pass


class SharedCoreUpdate(BaseModel):
    """Schema for updating an existing shared_core (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SharedCoreResponse(SharedCoreBase):
    """Schema for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SharedCoreListResponse(BaseModel):
    """Paginated list response."""

    items: list[SharedCoreResponse]
    total: int
    skip: int = 0
    limit: int = 100
