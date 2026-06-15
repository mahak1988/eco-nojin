"""Training Domain Models"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TrainingType(str, Enum):
    FFS = "farmer_field_school"
    WORKSHOP = "workshop"
    ONLINE = "online_course"
    FIELD_VISIT = "field_visit"
    COMMUNITY_MEETING = "community_meeting"


class TargetAudience(str, Enum):
    FARMERS = "farmers"
    WOMEN = "women"
    YOUTH = "youth"
    HERDERS = "herders"
    LOCAL_AUTHORITY = "local_authority"
    EXTENSION_WORKERS = "extension_workers"


@dataclass
class TrainingModule:
    module_id: str
    title: str
    description: str
    training_type: TrainingType
    target_audience: List[TargetAudience]
    duration_hours: float
    pilot_sites: List[str]
    topics: List[str]
    materials: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrainingSession:
    session_id: str
    module_id: str
    pilot_site: str
    date: datetime
    location: str
    instructor: str
    participants_count: int
    participants: List[str] = field(default_factory=list)
    feedback_score: Optional[float] = None
    completed: bool = False


@dataclass
class TrainingCertificate:
    certificate_id: str
    participant_id: str
    participant_name: str
    module_id: str
    module_title: str
    completion_date: datetime
    score: float
    pilot_site: str
