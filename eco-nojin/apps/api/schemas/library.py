"""
Library Schemas
=================
Pydantic models for request/response validation.
"""

import logging

logger = logging.getLogger(__name__)
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class LibraryCategoryEnum(str, Enum):
    RESEARCH = "research"
    GUIDES = "guides"
    POLICIES = "policies"
    REPORTS = "reports"
    TRAINING = "training"


class ResourceCategoryEnum(str, Enum):
    AGRICULTURE = "agriculture"
    WATER = "water"
    ENVIRONMENT = "environment"
    ECONOMICS = "economics"
    TECHNOLOGY = "technology"


class LibraryResourceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    category: LibraryCategoryEnum = LibraryCategoryEnum.RESEARCH
    tags: list[str] | None = Field(default_factory=list)
    author: str | None = Field(None, max_length=255)
    published_year: int | None = Field(None, ge=1900, le=2100)


class LibraryResourceCreate(LibraryResourceBase):
    file_path: str | None = Field(None, max_length=500)
    file_size: int | None = Field(None, ge=0)
    mime_type: str | None = Field(None, max_length=100)


class LibraryResourceUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    category: LibraryCategoryEnum | None = None
    tags: list[str] | None = None
    author: str | None = None
    published_year: int | None = None
    is_public: bool | None = None


class LibraryResourceResponse(LibraryResourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_path: str | None = None
    file_size: int | None = None
    mime_type: str | None = None
    is_public: bool
    download_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def model_validate(cls, obj: "LibraryResource") -> "LibraryResourceResponse":
        """Handle model_validate (cls, obj)."""
        data = super().model_validate(obj).model_dump()
        # Convert tags string to list
        if hasattr(obj, "tags") and obj.tags:
            data["tags"] = [t.strip() for t in obj.tags.split(",") if t.strip()]
        else:
            data["tags"] = []
        return cls(**data)


class LibraryResourceListResponse(BaseModel):
    items: list[LibraryResourceResponse]
    total: int
    skip: int = 0
    limit: int = 100


class LibraryStats(BaseModel):
    total_resources: int
    total_downloads: int
    by_category: dict[str, int]


class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    resource_id: int
