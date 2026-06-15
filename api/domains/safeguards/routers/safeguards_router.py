"""Safeguards API Router - GCF/World Bank Standards"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .services.grm_service import GRMService
from .services.sep_service import SEPService
from .services.esmf_service import ESMFService


router = APIRouter(prefix="/safeguards", tags=["Safeguards & GRM"])


class GrievanceSubmit(BaseModel):
    pilot_site: str
    country: str
    category: str
    severity: str
    description: str
    complainant_type: str = "individual"
    complainant_gender: str = "not_disclosed"
    is_anonymous: bool = False


class EngagementRecord(BaseModel):
    pilot_site: str
    activity_type: str
    participant_count: int
    women_count: int
    youth_count: int
    indigenous_count: int = 0
    vulnerable_groups_count: int = 0
    topics_discussed: List[str]
    feedback_summary: str


class ActivityScreening(BaseModel):
    pilot_site: str
    activity_type: str
    description: str


# GRM Endpoints
@router.post("/grm/submit")
async def submit_grievance(data: GrievanceSubmit):
    """ثبت شکایت در GRM"""
    service = GRMService()
    return service.submit_grievance(
        pilot_site=data.pilot_site,
        country=data.country,
        category=data.category,
        severity=data.severity,
        description=data.description,
        complainant_type=data.complainant_type,
        complainant_gender=data.complainant_gender,
        is_anonymous=data.is_anonymous
    )


@router.post("/grm/{grievance_id}/acknowledge")
async def acknowledge_grievance(grievance_id: str):
    """تأیید دریافت شکایت"""
    service = GRMService()
    return service.acknowledge_grievance(grievance_id)


@router.post("/grm/{grievance_id}/resolve")
async def resolve_grievance(grievance_id: str, resolution_notes: str):
    """حل و فصل شکایت"""
    service = GRMService()
    return service.resolve_grievance(grievance_id, resolution_notes)


@router.get("/grm/statistics")
async def get_grievance_statistics(pilot_site: str = None):
    """آمار شکایات"""
    service = GRMService()
    return service.get_grievance_statistics(pilot_site)


@router.get("/grm/gcf-report/{year}")
async def get_gcf_grievance_report(year: int):
    """گزارش سالانه GRM برای GCF"""
    service = GRMService()
    return service.generate_gcf_grievance_report(year)


# SEP Endpoints
@router.post("/sep/engagement")
async def record_engagement(data: EngagementRecord):
    """ثبت فعالیت مشارکت ذی‌نفعان"""
    service = SEPService()
    return service.record_engagement(
        pilot_site=data.pilot_site,
        activity_type=data.activity_type,
        participant_count=data.participant_count,
        women_count=data.women_count,
        youth_count=data.youth_count,
        indigenous_count=data.indigenous_count,
        vulnerable_groups_count=data.vulnerable_groups_count,
        topics_discussed=data.topics_discussed,
        feedback_summary=data.feedback_summary
    )


@router.get("/sep/inclusion-metrics")
async def get_inclusion_metrics(pilot_site: str = None):
    """شاخص‌های شمول"""
    service = SEPService()
    return service.get_inclusion_metrics(pilot_site)


# ESMF Endpoints
@router.post("/esmf/screen")
async def screen_activity(data: ActivityScreening):
    """غربالگری زیست‌محیطی-اجتماعی"""
    service = ESMFService()
    return service.screen_activity(
        pilot_site=data.pilot_site,
        activity_type=data.activity_type,
        description=data.description
    )


@router.get("/esmf/summary")
async def get_safeguards_summary():
    """خلاصه چارچوب حفاظت‌ها"""
    service = ESMFService()
    return service.get_safeguards_summary()


@router.get("/esmf/performance-standards")
async def get_performance_standards():
    """استانداردهای عملکردی GCF"""
    service = ESMFService()
    return {
        "standard": "GCF Performance Standards",
        "performance_standards": service.gcf_performance_standards,
        "alignment": [
            "IFC Performance Standards",
            "World Bank ESS",
            "Equator Principles IV"
        ]
    }