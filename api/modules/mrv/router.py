from api.services.satellite.sentinel2 import sentinel2
from api.services.satellite.landsat import landsat
from api.services.satellite.modis import modis
from api.services.satellite.gedi import gedi
# api/modules/mrv/router.py
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from api.core.database import get_db
from api.modules.mrv.models import CarbonProject, CarbonMeasurement, FinancialAnalysis, EcoCoinTransaction, AuditReport
from api.services.carbon_calculator import (
    SoilParameters, RothCSimplified, FinancialCalculator, 
    EcoCoinCalculator, AuditReportGenerator
)



class MRVStatsResponse(BaseModel):
    """Auto-generated response model for /stats"""
    total_projects: int = 0
    active_projects: int = 0
    total_carbon_credits: float = 0.0
    total_financial_value: float = 0.0
    verified_projects: int = 0


router = APIRouter(prefix="/mrv", tags=["MRV"])


# ============ Request/Response Models ============
class SoilInput(BaseModel):
    soil_type: str = Field(..., description="clay, loam, sandy")
    clay_content: float = Field(..., ge=0, le=100)
    initial_soc: float = Field(..., ge=0, description="SOC اولیه (t/ha)")
    pH: float = Field(..., ge=0, le=14)
    annual_rainfall: float = Field(..., ge=0, description="بارش سالانه (mm)")
    mean_temperature: float = Field(..., description="دمای میانگین (°C)")
    area_hectares: float = Field(..., ge=0)


class CarbonCalculationRequest(BaseModel):
    soil: SoilInput
    management: str = Field("conservation", description="conservation, conventional, regenerative")


class FinancialInput(BaseModel):
    initial_investment: float = Field(..., ge=0)
    annual_maintenance: float = Field(..., ge=0)
    carbon_price_per_ton: float = Field(50, ge=0, description="قیمت کربن ($/tCO₂e)")
    discount_rate: float = Field(0.08, ge=0, le=1)
    project_lifetime_years: int = Field(30, ge=1, le=100)


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_type: str = "soil_carbon"
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    soil: SoilInput
    management: str = "conservation"
    financial: FinancialInput


# ============ Endpoints ============
@router.post("/calculate", response_model=Dict[str, Any])
async def calculate_carbon(request: CarbonCalculationRequest):
    """محاسبه جذب کربن بر اساس پارامترهای خاک"""
    try:
        params = SoilParameters(
            soil_type=request.soil.soil_type,
            clay_content=request.soil.clay_content,
            initial_soc=request.soil.initial_soc,
            pH=request.soil.pH,
            annual_rainfall=request.soil.annual_rainfall,
            mean_temperature=request.soil.mean_temperature,
            area_hectares=request.soil.area_hectares,
        )
        
        result = RothCSimplified.calculate(params, request.management)
        ecocoin = EcoCoinCalculator.calculate_from_project(result)
        
        return {
            "status": "success",
            "management": request.management,
            "carbon": {
                "annual_rate_tco2e": result.annual_sequestration_rate,
                "total_20y_tco2e": result.total_sequestration_20_years,
                "total_30y_tco2e": result.total_sequestration_30_years,
                "final_soc_ton_per_ha": result.final_soc,
                "soc_increase_percent": result.soc_increase_percent,
                "uncertainty_percent": result.uncertainty_percent,
                "confidence_level": result.confidence_level,
                "yearly_projections": result.yearly_projections,
            },
            "ecocoin": ecocoin,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در محاسبه: {str(e)}")


@router.post("/financial-analysis", response_model=Dict[str, Any])
async def financial_analysis(request: FinancialInput, soil: SoilInput, management: str = "conservation"):
    """تحلیل مالی کامل پروژه"""
    try:
        params = SoilParameters(
            soil_type=soil.soil_type,
            clay_content=soil.clay_content,
            initial_soc=soil.initial_soc,
            pH=soil.pH,
            annual_rainfall=soil.annual_rainfall,
            mean_temperature=soil.mean_temperature,
            area_hectares=soil.area_hectares,
        )
        
        carbon_result = RothCSimplified.calculate(params, management)
        financial_result = FinancialCalculator.analyze_project(
            initial_investment=request.initial_investment,
            annual_maintenance=request.annual_maintenance,
            carbon_price_per_ton=request.carbon_price_per_ton,
            carbon_result=carbon_result,
            discount_rate=request.discount_rate,
            project_lifetime=request.project_lifetime_years,
        )
        
        return {
            "status": "success",
            "financial": financial_result,
            "carbon_summary": {
                "annual_rate_tco2e": carbon_result.annual_sequestration_rate,
                "total_20y_tco2e": carbon_result.total_sequestration_20_years,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects", response_model=Dict[str, Any])
async def create_project(request: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد پروژه جدید"""
    try:
        params = SoilParameters(
            soil_type=request.soil.soil_type,
            clay_content=request.soil.clay_content,
            initial_soc=request.soil.initial_soc,
            pH=request.soil.pH,
            annual_rainfall=request.soil.annual_rainfall,
            mean_temperature=request.soil.mean_temperature,
            area_hectares=request.soil.area_hectares,
        )
        
        carbon_result = RothCSimplified.calculate(params, request.management)
        financial_result = FinancialCalculator.analyze_project(
            initial_investment=request.financial.initial_investment,
            annual_maintenance=request.financial.annual_maintenance,
            carbon_price_per_ton=request.financial.carbon_price_per_ton,
            carbon_result=carbon_result,
            discount_rate=request.financial.discount_rate,
            project_lifetime=request.financial.project_lifetime_years,
        )
        ecocoin_result = EcoCoinCalculator.calculate_from_project(carbon_result)
        
        # ایجاد پروژه
        project = CarbonProject(
            name=request.name,
            description=request.description,
            project_type=request.project_type,
            location_name=request.location_name,
            latitude=request.latitude,
            longitude=request.longitude,
            area_hectares=request.soil.area_hectares,
            soil_type=request.soil.soil_type,
            initial_soc=request.soil.initial_soc,
            clay_content=request.soil.clay_content,
            pH=request.soil.pH,
            annual_rainfall=request.soil.annual_rainfall,
            mean_temperature=request.soil.mean_temperature,
            total_carbon_sequestered=carbon_result.total_sequestration_20_years,
            annual_carbon_rate=carbon_result.annual_sequestration_rate,
            eco_coins_generated=ecocoin_result["total_ecocoins"],
        )
        db.add(project)
        await db.flush()
        
        # ایجاد تحلیل مالی
        financial = FinancialAnalysis(
            project_id=project.id,
            initial_investment=request.financial.initial_investment,
            annual_maintenance_cost=request.financial.annual_maintenance,
            carbon_price_per_ton=request.financial.carbon_price_per_ton,
            discount_rate=request.financial.discount_rate,
            project_lifetime_years=request.financial.project_lifetime_years,
            npv=financial_result["npv"],
            irr=financial_result["irr"],
            payback_period_years=financial_result["payback_period_years"],
            total_revenue=financial_result["total_revenue"],
            total_cost=financial_result["total_cost"],
            net_profit=financial_result["net_profit"],
            cash_flows=financial_result["cash_flows"],
        )
        db.add(financial)
        
        # ایجاد گزارش ممیزی
        audit_report = AuditReportGenerator.generate_report(
            project_name=request.name,
            carbon_result=carbon_result,
            financial_result=financial_result,
            ecocoin_result=ecocoin_result,
        )
        audit = AuditReport(
            project_id=project.id,
            report_type="baseline",
            report_data=audit_report,
            sha256_hash=audit_report["integrity"]["sha256_hash"],
            auditor_name="Auto-generated by Econojin MRV Engine",
            verification_status="pending",
        )
        db.add(audit)
        
        await db.commit()
        
        return {
            "status": "success",
            "project_id": project.id,
            "project_name": project.name,
            "carbon": {
                "annual_rate_tco2e": carbon_result.annual_sequestration_rate,
                "total_20y_tco2e": carbon_result.total_sequestration_20_years,
                "final_soc": carbon_result.final_soc,
            },
            "financial": {
                "npv": financial_result["npv"],
                "irr": financial_result["irr"],
                "payback_years": financial_result["payback_period_years"],
            },
            "ecocoin": ecocoin_result["total_ecocoins"],
            "audit_hash": audit_report["integrity"]["sha256_hash"],
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects", response_model=IDResponse)
async def list_projects(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """لیست پروژه‌ها"""
    query = select(CarbonProject)
    if status:
        query = query.where(CarbonProject.status == status)
    query = query.order_by(desc(CarbonProject.created_at)).limit(limit)
    
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "type": p.project_type,
            "location": p.location_name,
            "area_ha": p.area_hectares,
            "status": p.status,
            "annual_co2e_ton": p.annual_carbon_rate,
            "total_co2e_ton": p.total_carbon_sequestered,
            "eco_coins": p.eco_coins_generated,
            "created_at": p.created_at,
        }
        for p in projects
    ]


@router.get("/projects/{project_id}", response_model=Dict[str, Any])
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """جزئیات پروژه"""
    result = await db.execute(
        select(CarbonProject).where(CarbonProject.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="پروژه یافت نشد")
    
    # دریافت تحلیل مالی
    fin_result = await db.execute(
        select(FinancialAnalysis).where(FinancialAnalysis.project_id == project_id)
    )
    financial = fin_result.scalar_one_or_none()
    
    # دریافت گزارش ممیزی
    audit_result = await db.execute(
        select(AuditReport).where(AuditReport.project_id == project_id)
    )
    audit = audit_result.scalars().first()
    
    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "type": project.project_type,
            "location": project.location_name,
            "coordinates": [project.latitude, project.longitude] if project.latitude else None,
            "area_ha": project.area_hectares,
            "soil_type": project.soil_type,
            "initial_soc": project.initial_soc,
            "status": project.status,
        },
        "carbon": {
            "annual_rate_tco2e": project.annual_carbon_rate,
            "total_co2e_ton": project.total_carbon_sequestered,
            "eco_coins": project.eco_coins_generated,
        },
        "financial": {
            "npv": financial.npv if financial else None,
            "irr": financial.irr if financial else None,
            "payback_years": financial.payback_period_years if financial else None,
            "roi_percent": (financial.net_profit / financial.total_cost * 100) if financial and financial.total_cost else None,
            "cash_flows": financial.cash_flows if financial else None,
        } if financial else None,
        "audit": {
            "hash": audit.sha256_hash,
            "status": audit.verification_status,
            "auditor": audit.auditor_name,
            "date": audit.report_date,
        } if audit else None,
    }


@router.get("/stats", response_model=MRVStatsResponse)
async def mrv_stats(db: AsyncSession = Depends(get_db)):
    """آمار کلی MRV"""
    from sqlalchemy import func
    
    total_projects = (await db.execute(select(func.count(CarbonProject.id)))).scalar() or 0
    active_projects = (await db.execute(
        select(func.count(CarbonProject.id)).where(CarbonProject.status == "active")
    )).scalar() or 0
    
    total_co2e = (await db.execute(
        select(func.sum(CarbonProject.total_carbon_sequestered))
    )).scalar() or 0
    
    total_ecocoins = (await db.execute(
        select(func.sum(CarbonProject.eco_coins_generated))
    )).scalar() or 0
    
    total_area = (await db.execute(
        select(func.sum(CarbonProject.area_hectares))
    )).scalar() or 0
    
    verified_reports = (await db.execute(
        select(func.count(AuditReport.id)).where(AuditReport.verification_status == "verified")
    )).scalar() or 0
    
    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "total_co2e_sequestered_ton": round(total_co2e, 2),
        "total_ecocoins": round(total_ecocoins, 2),
        "total_area_hectares": round(total_area, 2),
        "verified_reports": verified_reports,
    }
