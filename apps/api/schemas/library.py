"""
Library Schemas
=================
Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


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
    description: Optional[str] = Field(None, max_length=2000)
    category: LibraryCategoryEnum = LibraryCategoryEnum.RESEARCH
    tags: Optional[List[str]] = Field(default_factory=list)
    author: Optional[str] = Field(None, max_length=255)
    published_year: Optional[int] = Field(None, ge=1900, le=2100)


class LibraryResourceCreate(LibraryResourceBase):
    file_path: Optional[str] = Field(None, max_length=500)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)


class LibraryResourceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[LibraryCategoryEnum] = None
    tags: Optional[List[str]] = None
    author: Optional[str] = None
    published_year: Optional[int] = None
    is_public: Optional[bool] = None


class LibraryResourceResponse(LibraryResourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    is_public: bool
    download_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def model_validate(cls, obj: "LibraryResource") -> "LibraryResourceResponse":
        data = super().model_validate(obj).model_dump()
        # Convert tags string to list
        if hasattr(obj, "tags") and obj.tags:
            data["tags"] = [t.strip() for t in obj.tags.split(",") if t.strip()]
        else:
            data["tags"] = []
        return cls(**data)


class LibraryResourceListResponse(BaseModel):
    items: List[LibraryResourceResponse]
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