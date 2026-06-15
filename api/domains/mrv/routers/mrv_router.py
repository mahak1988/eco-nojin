"""MRV API Router"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime


router = APIRouter(prefix="/mrv", tags=["MRV"])


class MRVCalculationRequest(BaseModel):
    project_id: str
    area_ha: float
    land_use: str
    climate_zone: str
    initial_soc: float
    final_soc: float
    nitrogen_inputs: Dict[str, float]
    livestock_counts: Dict[str, int]
    initial_biomass: float
    final_biomass: float
    reporting_period_years: int = 1


class CarbonCreditRequest(BaseModel):
    project_id: str
    volume_tCO2e: float
    price_per_ton: float = 25.0
    currency: str = "USD"


@router.post("/calculate")
async def calculate_mrv(request: MRVCalculationRequest):
    """محاسبه MRV برای یک پروژه"""
    from api.services.mrv.mrv_calculator import MRVCalculator
    
    calculator = MRVCalculator()
    
    report = calculator.generate_mrv_report(
        project_id=request.project_id,
        area_ha=request.area_ha,
        land_use=request.land_use,
        climate_zone=request.climate_zone,
        initial_soc=request.initial_soc,
        final_soc=request.final_soc,
        nitrogen_inputs=request.nitrogen_inputs,
        livestock_counts=request.livestock_counts,
        initial_biomass=request.initial_biomass,
        final_biomass=request.final_biomass,
        reporting_period_years=request.reporting_period_years
    )
    
    return report


@router.post("/issue-credit")
async def issue_carbon_credit(request: CarbonCreditRequest):
    """صدور اعتبار کربن"""
    from api.services.mrv.carbon_credit_service import CarbonCreditService
    
    service = CarbonCreditService()
    
    credit = service.issue_carbon_credit(
        project_id=request.project_id,
        volume_tCO2e=request.volume_tCO2e,
        verification_date=datetime.utcnow(),
        price_per_ton=request.price_per_ton,
        currency=request.currency
    )
    
    return credit


@router.get("/project/{project_id}/credits")
async def get_project_credits(project_id: str):
    """دریافت اعتبارات کربن یک پروژه"""
    from api.services.mrv.carbon_credit_service import CarbonCreditService
    
    service = CarbonCreditService()
    credits = service.get_project_credits(project_id)
    
    return {
        "project_id": project_id,
        "credits": credits,
        "total_volume_tCO2e": service.get_total_issued_volume(project_id)
    }


@router.get("/project/{project_id}/reports")
async def get_project_reports(
    project_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """دریافت گزارش‌های MRV یک پروژه"""
    # TODO: اتصال به Repository
    return {
        "project_id": project_id,
        "reports": [],
        "message": "Not implemented yet"
    }
