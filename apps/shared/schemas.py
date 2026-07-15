"""
shared schemas | شِما‌های shared
=====================================
Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class SharedBase(BaseModel):
    """Base schema with shared fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Name")
    description: Optional[str] = Field(None, description="Description")


class SharedCreate(SharedBase):
    """Schema for creating a new shared."""

    pass


class SharedUpdate(BaseModel):
    """Schema for updating an existing shared (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SharedResponse(SharedBase):
    """Schema for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SharedListResponse(BaseModel):
    """Paginated list response."""

    items: list[SharedResponse]
    total: int
    skip: int = 0
    limit: int = 100
