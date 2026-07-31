"""
shared_core schemas | شِما‌های shared_core
=====================================
Pydantic models for request/response validation.
"""

import logging

logger = logging.getLogger(__name__)
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SharedCoreBase(BaseModel):
    """Base schema with shared fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Name")
    description: str | None = Field(None, description="Description")


class SharedCoreCreate(SharedCoreBase):
    """Schema for creating a new shared_core."""

    pass


class SharedCoreUpdate(BaseModel):
    """Schema for updating an existing shared_core (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    is_active: bool | None = None


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
