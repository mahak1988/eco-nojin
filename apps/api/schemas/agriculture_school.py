"""
Agriculture Schools Schemas
============================
Pydantic models for request/response validation.
"""

import logging

logger = logging.getLogger(__name__)
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SchoolTypeEnum(str, Enum):
    UNIVERSITY = "university"
    INSTITUTE = "institute"
    TRAINING_CENTER = "training-center"


class AgricultureSchoolBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    province: str = Field(..., min_length=1, max_length=128)
    city: str = Field(..., min_length=1, max_length=128)
    school_type: SchoolTypeEnum = SchoolTypeEnum.UNIVERSITY
    established: int | None = Field(None, ge=1900, le=2100)
    students_count: int = Field(0, ge=0)
    website: str | None = Field(None, max_length=500)
    logo: str = Field("📣", max_length=10)


class AgricultureSchoolCreate(AgricultureSchoolBase):
    fields: list[str] | None = Field(default_factory=list)


class AgricultureSchoolUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    province: str | None = None
    city: str | None = None
    school_type: SchoolTypeEnum | None = None
    established: int | None = None
    students_count: int | None = None
    website: str | None = None
    logo: str | None = None
    is_active: bool | None = None


class AgricultureSchoolResponse(AgricultureSchoolBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Flatten fields to list of strings
    @classmethod
    def model_validate(cls, obj: "AgricultureSchool") -> "AgricultureSchoolResponse":
        """Handle model_validate (cls, obj)."""
        data = super().model_validate(obj).model_dump()
        # Extract field names as list
        data["fields"] = (
            [f.field_name for f in obj.fields] if hasattr(obj, "fields") and obj.fields else []
        )
        return cls(**data)


class AgricultureSchoolListResponse(BaseModel):
    items: list[AgricultureSchoolResponse]
    total: int
    skip: int = 0
    limit: int = 100


class SchoolStats(BaseModel):
    total_schools: int
    total_students: int
    provinces_count: int
    by_type: dict[str, int]
