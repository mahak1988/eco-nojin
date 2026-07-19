"""
Agriculture Schools Schemas
============================
Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class SchoolTypeEnum(str, Enum):
    UNIVERSITY = "university"
    INSTITUTE = "institute"
    TRAINING_CENTER = "training-center"


class AgricultureSchoolBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    province: str = Field(..., min_length=1, max_length=128)
    city: str = Field(..., min_length=1, max_length=128)
    school_type: SchoolTypeEnum = SchoolTypeEnum.UNIVERSITY
    established: Optional[int] = Field(None, ge=1900, le=2100)
    students_count: int = Field(0, ge=0)
    website: Optional[str] = Field(None, max_length=500)
    logo: str = Field("📣", max_length=10)


class AgricultureSchoolCreate(AgricultureSchoolBase):
    fields: Optional[List[str]] = Field(default_factory=list)


class AgricultureSchoolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    province: Optional[str] = None
    city: Optional[str] = None
    school_type: Optional[SchoolTypeEnum] = None
    established: Optional[int] = None
    students_count: Optional[int] = None
    website: Optional[str] = None
    logo: Optional[str] = None
    is_active: Optional[bool] = None


class AgricultureSchoolResponse(AgricultureSchoolBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Flatten fields to list of strings
    @classmethod
    def model_validate(cls, obj: "AgricultureSchool") -> "AgricultureSchoolResponse":
        data = super().model_validate(obj).model_dump()
        # Extract field names as list
        data["fields"] = [f.field_name for f in obj.fields] if hasattr(obj, "fields") and obj.fields else []
        return cls(**data)


class AgricultureSchoolListResponse(BaseModel):
    items: List[AgricultureSchoolResponse]
    total: int
    skip: int = 0
    limit: int = 100


class SchoolStats(BaseModel):
    total_schools: int
    total_students: int
    provinces_count: int
    by_type: dict[str, int]