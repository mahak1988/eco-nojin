"""Education Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from apps.shared_core.schemas.pagination import ListMeta


class CourseLevelEnum(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CourseCategoryEnum(str, Enum):
    AGRICULTURE = "agriculture"
    WATER_MANAGEMENT = "water-management"
    ENVIRONMENTAL_SCIENCE = "environmental-science"
    ECONOMICS = "economics"
    TECHNOLOGY = "technology"


class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: str = Field(default="agriculture")
    level: str = Field(default="beginner")
    duration_hours: int = Field(0, ge=0)
    instructor: Optional[str] = Field(None, max_length=255)


class CourseCreate(CourseBase):
    lessons: Optional[List[dict]] = Field(default_factory=list)


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    duration_hours: Optional[int] = Field(None, ge=0)
    instructor: Optional[str] = None
    is_active: Optional[bool] = None


class LessonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration_minutes: int = 0
    order: int = 0


class EnrollmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    progress: int = 0
    enrolled_at: datetime
    completed_at: Optional[datetime] = None


class CourseResponse(CourseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    lessons: List[LessonResponse] = Field(default_factory=list)
    enrollments: List[EnrollmentResponse] = Field(default_factory=list)


class CourseListResponse(BaseModel):
    """R14 envelope + legacy fields for existing FE mappers."""

    data: List[CourseResponse] = Field(default_factory=list)
    meta: ListMeta
    # legacy (until all clients migrate)
    items: List[CourseResponse] = Field(default_factory=list)
    total: int = 0
    skip: int = 0
    limit: int = 20


class LessonBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None
    video_url: Optional[str] = Field(None, max_length=500)
    duration_minutes: int = Field(0, ge=0)
    order: int = Field(0, ge=0)


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    order: Optional[int] = Field(None, ge=0)


class EnrollmentBase(BaseModel):
    user_id: int = Field(..., gt=0)


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentUpdate(BaseModel):
    progress: Optional[int] = Field(None, ge=0, le=100)
    completed_at: Optional[datetime] = None


class CourseStats(BaseModel):
    total_courses: int
    total_lessons: int
    total_enrollments: int
    by_category: dict[str, int]
    by_level: dict[str, int]
