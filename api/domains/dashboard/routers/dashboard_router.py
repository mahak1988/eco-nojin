"""Dashboard API Router"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime
from .schemas.dashboard_schemas import (
    DashboardResponse,
    DashboardWidgetResponse,
    AlertNotificationResponse,
    UserPreferenceRequest
)
from .services.dashboard_service import DashboardService
from .services.dss_service import DSSService


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_dashboard_service() -> DashboardService:
    """Dependency Injection"""
    return DashboardService()


def get_dss_service() -> DSSService:
    """Dependency Injection"""
    return DSSService()


# Watershed Manager Dashboard
@router.get("/watershed-manager/{watershed_id}")
async def get_watershed_manager_dashboard(
    watershed_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """دریافت داشبورد مدیر حوضه آبخیز"""
    return service.get_watershed_manager_dashboard(watershed_id)


# Farmer Dashboard
@router.get("/farmer/{farmer_id}/{farm_id}")
async def get_farmer_dashboard(
    farmer_id: str,
    farm_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """دریافت داشبورد کشاورز"""
    return service.get_farmer_dashboard(farmer_id, farm_id)


# Investor Dashboard
@router.get("/investor/{project_id}")
async def get_investor_dashboard(
    project_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """دریافت داشبورد سرمایه‌گذار"""
    return service.get_investor_dashboard(project_id)


# Policy Maker Dashboard
@router.get("/policy-maker/{region_id}")
async def get_policy_maker_dashboard(
    region_id: str,
    service: DashboardService = Depends(get_dashboard_service)
):
    """دریافت داشبورد سیاست‌گذار"""
    return service.get_policy_maker_dashboard(region_id)


# DSS Endpoints
@router.post("/dss/water-assessment")
async def assess_water_stress(
    wue: float,
    groundwater_level_m: float,
    precipitation_anomaly_percent: float,
    dss: DSSService = Depends(get_dss_service)
):
    """ارزیابی تنش آبی"""
    return dss.evaluate_water_stress(wue, groundwater_level_m, precipitation_anomaly_percent)


@router.post("/dss/soil-assessment")
async def assess_soil_health(
    soc_percent: float,
    erosion_rate_t_ha_year: float,
    salinity_ds_m: float,
    dss: DSSService = Depends(get_dss_service)
):
    """ارزیابی سلامت خاک"""
    return dss.evaluate_soil_health(soc_percent, erosion_rate_t_ha_year, salinity_ds_m)


@router.post("/dss/livelihood-assessment")
async def assess_livelihood_resilience(
    income_diversity_index: float,
    food_security_score: float,
    poverty_rate_percent: float,
    dss: DSSService = Depends(get_dss_service)
):
    """ارزیابی تاب‌آوری معیشت"""
    return dss.evaluate_livelihood_resilience(
        income_diversity_index,
        food_security_score,
        poverty_rate_percent
    )


@router.post("/dss/carbon-assessment")
async def assess_carbon_balance(
    net_carbon_balance_tCO2e: float,
    soc_sequestration_tCO2: float,
    emissions_tCO2e: float,
    dss: DSSService = Depends(get_dss_service)
):
    """ارزیابی تراز کربن"""
    return dss.evaluate_carbon_balance(
        net_carbon_balance_tCO2e,
        soc_sequestration_tCO2,
        emissions_tCO2e
    )


@router.post("/dss/comprehensive-recommendation/{watershed_id}")
async def get_comprehensive_recommendation(
    watershed_id: str,
    water_assessment: dict,
    soil_assessment: dict,
    livelihood_assessment: dict,
    carbon_assessment: dict,
    dss: DSSService = Depends(get_dss_service)
):
    """دریافت توصیه جامع مدیریتی"""
    return dss.generate_comprehensive_recommendation(
        watershed_id,
        water_assessment,
        soil_assessment,
        livelihood_assessment,
        carbon_assessment
    )


# Alerts
@router.get("/alerts/active")
async def get_active_alerts(
    dashboard_type: Optional[str] = None,
    service: DashboardService = Depends(get_dashboard_service)
):
    """دریافت هشدارهای فعال"""
    # TODO: اتصال به Repository
    return {
        "alerts": [],
        "count": 0
    }
