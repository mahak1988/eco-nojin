"""
api schemas | شِما‌های api
=====================================
Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ApiBase(BaseModel):
    """Base schema with shared fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Name")
    description: Optional[str] = Field(None, description="Description")


class ApiCreate(ApiBase):
    """Schema for creating a new api."""

    pass


class ApiUpdate(BaseModel):
    """Schema for updating an existing api (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ApiResponse(ApiBase):
    """Schema for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ApiListResponse(BaseModel):
    """Paginated list response."""

    items: list[ApiResponse]
    total: int
    skip: int = 0
    limit: int = 100
