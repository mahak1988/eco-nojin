"""LogFrame API Router - International Reporting"""
from fastapi import APIRouter, HTTPException
from typing import List
from .services.logframe_service import LogFrameService


router = APIRouter(prefix="/logframe", tags=["LogFrame & International Reporting"])


def get_logframe_service() -> LogFrameService:
    return LogFrameService()


@router.get("/overview")
async def get_logframe_overview(service: LogFrameService = get_logframe_service()):
    """دریافت نمای کلی LogFrame مطابق IRMF GCF/GEF"""
    return service.get_logframe()


@router.get("/sdg/{sdg_number}")
async def get_indicators_by_sdg(
    sdg_number: str,
    service: LogFrameService = get_logframe_service()
):
    """دریافت شاخص‌های مرتبط با یک SDG خاص"""
    if sdg_number not in ["2", "6", "8", "13", "15"]:
        raise HTTPException(status_code=400, detail="Invalid SDG")
    
    indicators = service.get_indicators_by_sdg(sdg_number)
    return {
        "sdg": f"SDG {sdg_number}",
        "indicators_count": len(indicators),
        "indicators": indicators
    }


@router.get("/gef/core-indicators")
async def get_gef_core_indicators(
    service: LogFrameService = get_logframe_service()
):
    """دریافت شاخص‌های Core GEF"""
    indicators = service.get_gef_core_indicators()
    return {
        "framework": "GEF IRMF",
        "indicators_count": len(indicators),
        "indicators": indicators
    }


@router.get("/gcf/core-indicators")
async def get_gcf_core_indicators(
    service: LogFrameService = get_logframe_service()
):
    """دریافت شاخص‌های Core GCF"""
    indicators = service.get_gcf_core_indicators()
    return {
        "framework": "GCF IRMF",
        "indicators_count": len(indicators),
        "indicators": indicators
    }


@router.get("/ndc-report/{project_id}/{year}")
async def get_ndc_report(
    project_id: str,
    year: int,
    service: LogFrameService = get_logframe_service()
):
    """دریافت گزارش NDC آماده برای UNFCCC"""
    return service.generate_ndc_report(project_id, year)


@router.get("/summary")
async def get_summary_dashboard(
    service: LogFrameService = get_logframe_service()
):
    """خلاصه اجرایی برای سیاست‌گذاران"""
    logframe = service.get_logframe()
    gef = service.get_gef_core_indicators()
    gcf = service.get_gcf_core_indicators()
    
    return {
        "total_outcomes": logframe["outcomes"],
        "total_indicators": sum(e["indicators_count"] for e in logframe["entries"]),
        "gef_core_count": len(gef),
        "gcf_core_count": len(gcf),
        "sdgs_covered": ["SDG 2", "SDG 6", "SDG 8", "SDG 13", "SDG 15"],
        "pilot_sites": 12,
        "continents": 4,
        "alignment": {
            "GCF": True,
            "GEF": True,
            "UNFCCC_NDC": True,
            "UNCCD_LDN": True,
            "Paris_Agreement": True
        }
    }
