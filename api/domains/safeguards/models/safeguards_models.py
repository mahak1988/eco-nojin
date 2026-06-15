"""Safeguards Domain Models - Aligned with International Standards"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime, timezone
from enum import Enum


class GrievanceCategory(str, Enum):
    """دسته‌بندی شکایات مطابق GCF GRM"""
    ENVIRONMENTAL = "environmental"  # آسیب زیست‌محیطی
    SOCIAL = "social"  # مسائل اجتماعی
    GENDER = "gender"  # مسائل جنسیتی
    LAND_RIGHTS = "land_rights"  # حقوق زمین
    INDIGENOUS_PEOPLES = "indigenous_peoples"  # حقوق بومیان
    LABOR = "labor"  # مسائل کارگری
    FINANCIAL = "financial"  # مسائل مالی
    CORRUPTION = "corruption"  # فساد
    OTHER = "other"


class GrievanceSeverity(str, Enum):
    """سطح شدت شکایت"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GrievanceStatus(str, Enum):
    """وضعیت رسیدگی به شکایت"""
    RECEIVED = "received"
    ACKNOWLEDGED = "acknowledged"
    UNDER_INVESTIGATION = "under_investigation"
    RESOLUTION_PROPOSED = "resolution_proposed"
    RESOLVED = "resolved"
    APPEALED = "appealed"
    CLOSED = "closed"


@dataclass
class Grievance:
    """شکایت ثبت‌شده در GRM"""
    grievance_id: str
    pilot_site: str
    country: str
    category: GrievanceCategory
    severity: GrievanceSeverity
    status: GrievanceStatus = GrievanceStatus.RECEIVED
    description: str = ""
    complainant_type: str = "individual"  # individual, community, ngo
    complainant_gender: str = "not_disclosed"
    is_anonymous: bool = False
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""
    sla_days: int = 30  # Service Level Agreement


@dataclass
class SafeguardAssessment:
    """ارزیابی حفاظت‌های زیست‌محیطی-اجتماعی"""
    assessment_id: str
    pilot_site: str
    activity_type: str
    environmental_risk: str = "low"
    social_risk: str = "low"
    gender_risk: str = "low"
    indigenous_peoples_involved: bool = False
    resettlement_required: bool = False
    ifc_performance_standards: List[str] = field(default_factory=list)
    world_bank_ess: List[str] = field(default_factory=list)
    mitigation_measures: List[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class StakeholderEngagement:
    """ثبت فعالیت مشارکت ذی‌نفعان"""
    engagement_id: str
    pilot_site: str
    activity_type: str  # consultation, workshop, fgd, pra
    participant_count: int
    women_count: int
    youth_count: int
    indigenous_count: int = 0
    vulnerable_groups_count: int = 0
    topics_discussed: List[str] = field(default_factory=list)
    feedback_summary: str = ""
    conducted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ESMPAction:
    """اقدام برنامه مدیریت زیست‌محیطی-اجتماعی"""
    action_id: str
    pilot_site: str
    impact_type: str
    mitigation_measure: str
    responsible_party: str
    timeline: str
    budget_usd: float = 0.0
    status: str = "planned"
    monitoring_indicator: str = ""