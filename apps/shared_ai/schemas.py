"""
shared_ai schemas | شِما‌های shared_ai
=====================================
Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class SharedAiBase(BaseModel):
    """Base schema with shared fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Name")
    description: Optional[str] = Field(None, description="Description")


class SharedAiCreate(SharedAiBase):
    """Schema for creating a new shared_ai."""

    pass


class SharedAiUpdate(BaseModel):
    """Schema for updating an existing shared_ai (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SharedAiResponse(SharedAiBase):
    """Schema for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SharedAiListResponse(BaseModel):
    """Paginated list response."""

    items: list[SharedAiResponse]
    total: int
    skip: int = 0
    limit: int = 100
