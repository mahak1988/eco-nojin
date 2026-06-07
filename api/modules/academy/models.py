"""
Academy Models - سیستم آکادمی اکو نوین
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Course(BaseModel):
    id: int
    code: str
    title: str
    title_en: str
    category: str  # hydrology, carbon, soil, remote_sensing, sustainable_agriculture
    level: str  # beginner, intermediate, advanced
    duration_hours: int
    lessons_count: int
    instructor: str
    standards: List[str]  # FAO, IPCC, SDGs
    description: str
    description_en: str
    objectives: List[str]
    prerequisites: List[str]
    thumbnail: str
    rating: float = 0.0
    students_count: int = 0
    is_certified: bool = True
    created_at: str = ""


class Lesson(BaseModel):
    id: int
    course_id: int
    title: str
    duration_minutes: int
    order: int
    is_free: bool = False
    video_url: Optional[str] = None
    content: str


class Enrollment(BaseModel):
    id: int
    user_id: int
    course_id: int
    enrolled_at: str
    progress: float = 0.0
    completed_lessons: List[int] = []
    certificate_id: Optional[str] = None


class Certificate(BaseModel):
    id: str
    user_id: int
    course_id: int
    issued_at: str
    score: float
    verification_code: str
    standards: List[str]
