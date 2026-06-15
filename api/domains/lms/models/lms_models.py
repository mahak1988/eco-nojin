"""LMS Domain Models"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class Language(str, Enum):
    FA = "fa"  # فارسی
    EN = "en"  # English
    AR = "ar"  # العربية
    FR = "fr"  # Français
    ES = "es"  # Español
    SW = "sw"  # Kiswahili
    HI = "hi"  # हिन्दी
    MN = "mn"  # Монгол


class CourseCategory(str, Enum):
    WATER_MANAGEMENT = "water_management"
    SOIL_CONSERVATION = "soil_conservation"
    CLIMATE_SMART_AGRICULTURE = "climate_smart_agriculture"
    AGROFORESTRY = "agroforestry"
    LIVELIHOOD_DIVERSIFICATION = "livelihood_diversification"
    CARBON_MARKET = "carbon_market"
    GOVERNANCE = "governance"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class Course:
    course_id: str
    title: Dict[str, str]  # {language: title}
    description: Dict[str, str]
    category: CourseCategory
    difficulty: DifficultyLevel
    pilot_sites: List[str]
    languages: List[Language]
    modules: List[str] = field(default_factory=list)
    duration_hours: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Module:
    module_id: str
    course_id: str
    title: Dict[str, str]
    content: Dict[str, str]  # Markdown content
    video_url: Optional[str] = None
    quiz_questions: List[Dict] = field(default_factory=list)
    order: int = 0


@dataclass
class Enrollment:
    enrollment_id: str
    user_id: str
    course_id: str
    enrolled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    progress_percent: float = 0.0
    completed_modules: List[str] = field(default_factory=list)
    completed: bool = False
    completed_at: Optional[datetime] = None


@dataclass
class Certificate:
    certificate_id: str
    user_id: str
    course_id: str
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    blockchain_tx_hash: Optional[str] = None
    qr_code_url: Optional[str] = None


@dataclass
class Facilitator:
    facilitator_id: str
    name: str
    pilot_site: str
    languages: List[Language]
    expertise: List[str]
    certified_courses: List[str] = field(default_factory=list)
    active: bool = True
