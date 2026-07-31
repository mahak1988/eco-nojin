"""
shared_knowledge schemas | شِما‌های shared_knowledge
=====================================
Pydantic models for request/response validation.
"""

import logging

logger = logging.getLogger(__name__)
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SharedKnowledgeBase(BaseModel):
    """Base schema with shared fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Name")
    description: str | None = Field(None, description="Description")


class SharedKnowledgeCreate(SharedKnowledgeBase):
    """Schema for creating a new shared_knowledge."""

    pass


class SharedKnowledgeUpdate(BaseModel):
    """Schema for updating an existing shared_knowledge (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    is_active: bool | None = None


class SharedKnowledgeResponse(SharedKnowledgeBase):
    """Schema for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SharedKnowledgeListResponse(BaseModel):
    """Paginated list response."""

    items: list[SharedKnowledgeResponse]
    total: int
    skip: int = 0
    limit: int = 100
