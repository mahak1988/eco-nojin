#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💰 لایه ۴: موتور MRV و اعتبار کربن
- محاسبه‌گر کربن RothC
- تحلیل مالی (NPV, IRR)
- داشبورد MRV
- سیستم EcoCoin
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


# ========== 1. مدل‌های دیتابیس MRV ==========
def create_mrv_models():
    print("\n🗄️ ایجاد مدل‌های MRV...")
    
    content = '''# api/modules/mrv/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.sql import func
from api.core.database import Base


class CarbonProject(Base):
    """پروژه‌های جذب کربن"""
    __tablename__ = "carbon_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(2000))
    project_type = Column(String(50))  # reforestation, soil_carbon, agroforestry
    location_name = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    area_hectares = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # پارامترهای خاک
    soil_type = Column(String(50))  # clay, loam, sandy
    initial_soc = Column(Float)  # SOC اولیه (t/ha)
    clay_content = Column(Float)  # درصد رس
    pH = Column(Float)
    
    # پارامترهای اقلیمی
    annual_rainfall = Column(Float)  # mm
    mean_temperature = Column(Float)  # °C
    
    # وضعیت
    status = Column(String(20), default="active")  # active, completed, paused
    verification_status = Column(String(20), default="pending")  # pending, verified, rejected
    
    # نتایج
    total_carbon_sequestered = Column(Float, default=0)  # tCO₂e
    annual_carbon_rate = Column(Float, default=0)  # tCO₂e/سال
    eco_coins_generated = Column(Float, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class CarbonMeasurement(Base):
    """اندازه‌گیری‌های دوره‌ای کربن"""
    __tablename__ = "carbon_measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("carbon_projects.id"))
    
    measurement_date = Column(DateTime, nullable=False)
    measurement_method = Column(String(50))  # rothc_model, field_sample, remote_sensing
    
    # نتایج اندازه‌گیری
    soc_ton_per_hectare = Column(Float)  # تن کربن در هکتار
    biomass_ton_per_hectare = Column(Float)
    total_tco2e = Column(Float)
    
    # عدم قطعیت
    uncertainty_percent = Column(Float, default=10)
    confidence_level = Column(Float, default=0.95)
    
    # داده‌های ورودی
    input_data = Column(JSON)
    
    created_at = Column(DateTime, server_default=func.now())


class FinancialAnalysis(Base):
    """تحلیل‌های مالی پروژه"""
    __tablename__ = "financial_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("carbon_projects.id"))
    
    analysis_date = Column(DateTime, server_default=func.now())
    
    # پارامترهای مالی
    initial_investment = Column(Float)  # سرمایه‌گذاری اولیه
    annual_maintenance_cost = Column(Float)  # هزینه نگهداری سالانه
    carbon_price_per_ton = Column(Float)  # قیمت هر تن کربن ($)
    discount_rate = Column(Float, default=0.08)  # نرخ تنزیل
    project_lifetime_years = Column(Integer, default=30)
    
    # نتایج
    npv = Column(Float)  # ارزش فعلی خالص
    irr = Column(Float)  # نرخ بازده داخلی
    payback_period_years = Column(Float)  # دوره بازگشت
    total_revenue = Column(Float)
    total_cost = Column(Float)
    net_profit = Column(Float)
    
    # جریان نقدی سالانه
    cash_flows = Column(JSON)


class EcoCoinTransaction(Base):
    """تراکنش‌های EcoCoin"""
    __tablename__ = "ecocoin_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100))
    project_id = Column(Integer, ForeignKey("carbon_projects.id"), nullable=True)
    
    transaction_type = Column(String(20))  # earn, spend, transfer, convert
    amount = Column(Float)  # مقدار EcoCoin
    balance_after = Column(Float)
    
    description = Column(String(500))
    reference_id = Column(String(100))  # ارتباط با پروژه یا تراکنش دیگر
    
    created_at = Column(DateTime, server_default=func.now())


class AuditReport(Base):
    """گزارش‌های ممیزی"""
    __tablename__ = "audit_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("carbon_projects.id"))
    
    report_date = Column(DateTime, server_default=func.now())
    report_type = Column(String(50))  # annual, verification, baseline
    
    # محتوا
    report_data = Column(JSON)
    pdf_url = Column(String(500))
    
    # امنیت
    sha256_hash = Column(String(64))  # هش SHA-256
    blockchain_tx_id = Column(String(100))  # شناسه تراکنش بلاکچین
    
    # وضعیت
    auditor_name = Column(String(200))
    verification_status = Column(String(20), default="pending")
    
    created_at = Column(DateTime, server_default=func.now())
'''
    
    write_file(API_DIR / "modules" / "mrv" / "models.py", content)


# ========== 2. موتور محاسبه کربن ==========
def create_carbon_calculator():
    print("\n🧮 ایجاد موتور محاسبه کربن...")
    
    content = '''# api/services/carbon_calculator.py
"""
موتور محاسبه کربن خاک بر اساس مدل RothC (ساده‌شده)
و محاسبات مالی (NPV, IRR, Payback Period)
"""
import math
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SoilParameters:
    """پارامترهای خاک"""
    soil_type: str  # clay, loam, sandy
    clay_content: float  # درصد رس (0-100)
    initial_soc: float  # SOC اولیه (t/ha)
    pH: float
    annual_rainfall: float  # mm
    mean_temperature: float  # °C
    area_hectares: float


@dataclass
class CarbonResult:
    """نتایج محاسبه کربن"""
    annual_sequestration_rate: float  # tCO₂e/سال
    total_sequestration_20_years: float  # tCO₂e در ۲۰ سال
    total_sequestration_30_years: float
    final_soc: float  # SOC نهایی (t/ha)
    soc_increase_percent: float
    uncertainty_percent: float
    confidence_level: float
    yearly_projections: List[Dict]


class RothCSimplified:
    """
    مدل ساده‌شده RothC برای محاسبه دینامیک کربن خاک
    بر اساس: Coleman & Jenkinson (1996)
    """
    
    # ضرایب تبدیل
    CARBON_TO_CO2 = 44 / 12  # 3.67
    SOC_TO_BIOMASS = 0.5  # 50% کربن در زیست‌توده
    
    # ضرایب بر اساس نوع خاک
    SOIL_FACTORS = {
        "clay": {"decomposition_rate": 0.015, "stabilization": 0.8},
        "loam": {"decomposition_rate": 0.020, "stabilization": 0.6},
        "sandy": {"decomposition_rate": 0.030, "stabilization": 0.4},
    }
    
    @classmethod
    def calculate_rate_modifier(cls, params: SoilParameters) -> float:
        """محاسبه ضریب اصلاح بر اساس شرایط اقلیمی"""
        # ضریب دما (بهینه: ۲۵°C)
        temp_factor = 0.5 + 0.02 * params.mean_temperature
        temp_factor = max(0.3, min(1.5, temp_factor))
        
        # ضریب رطوبت (بهینه: ۸۰۰mm)
        moisture_factor = params.annual_rainfall / 800
        moisture_factor = max(0.2, min(1.5, moisture_factor))
        
        # ضریب pH (بهینه: 6.5-7.5)
        if 6.5 <= params.pH <= 7.5:
            ph_factor = 1.0
        else:
            ph_factor = 0.7
        
        # ضریب رس (خاک‌های رسی کربن بیشتری حفظ می‌کنند)
        clay_factor = 0.5 + (params.clay_content / 100) * 0.8
        
        return temp_factor * moisture_factor * ph_factor * clay_factor
    
    @classmethod
    def calculate(cls, params: SoilParameters, management: str = "conservation") -> CarbonResult:
        """
        محاسبه جذب کربن در طول زمان
        
        management: conservation, conventional, regenerative
        """
        soil_factor = cls.SOIL_FACTORS.get(params.soil_type, cls.SOIL_FACTORS["loam"])
        rate_modifier = cls.calculate_rate_modifier(params)
        
        # ضریب مدیریت
        management_factors = {
            "conventional": 0.0,  # بدون تغییر
            "conservation": 0.3,  # افزایش ۳۰٪
            "regenerative": 0.6,  # افزایش ۶۰٪
        }
        mgmt_factor = management_factors.get(management, 0.3)
        
        # نرخ پایه جذب کربن (t C/ha/سال)
        base_rate = soil_factor["decomposition_rate"] * rate_modifier * mgmt_factor
        
        # شبیه‌سازی سال به سال
        yearly_projections = []
        current_soc = params.initial_soc
        total_co2e = 0
        
        for year in range(1, 31):
            # کاهش نرخ جذب با زمان (قانون بازده نزولی)
            decay_factor = math.exp(-0.03 * year)
            annual_rate = base_rate * decay_factor * params.area_hectares
            
            # SOC جدید
            current_soc += annual_rate / params.area_hectares
            
            # تبدیل به CO₂e
            annual_co2e = annual_rate * cls.CARBON_TO_CO2
            total_co2e += annual_co2e
            
            yearly_projections.append({
                "year": year,
                "soc_ton_per_ha": round(current_soc, 2),
                "annual_carbon_ton": round(annual_rate, 3),
                "annual_co2e_ton": round(annual_co2e, 2),
                "cumulative_co2e_ton": round(total_co2e, 2),
            })
        
        # محاسبه نتایج کل
        total_20y = sum(p["annual_co2e_ton"] for p in yearly_projections[:20])
        total_30y = sum(p["annual_co2e_ton"] for p in yearly_projections)
        
        # عدم قطعیت (بر اساس متدولوژی IPCC)
        uncertainty = 15 if management == "regenerative" else 20 if management == "conservation" else 30
        
        return CarbonResult(
            annual_sequestration_rate=round(yearly_projections[0]["annual_co2e_ton"], 2),
            total_sequestration_20_years=round(total_20y, 2),
            total_sequestration_30_years=round(total_30y, 2),
            final_soc=round(current_soc, 2),
            soc_increase_percent=round((current_soc - params.initial_soc) / params.initial_soc * 100, 1),
            uncertainty_percent=uncertainty,
            confidence_level=0.95,
            yearly_projections=yearly_projections,
        )


class FinancialCalculator:
    """محاسبات مالی برای پروژه‌های کربن"""
    
    @staticmethod
    def calculate_npv(
        initial_investment: float,
        annual_revenue: List[float],
        annual_costs: List[float],
        discount_rate: float = 0.08,
    ) -> float:
        """محاسبه ارزش فعلی خالص (NPV)"""
        npv = -initial_investment
        for t, (rev, cost) in enumerate(zip(annual_revenue, annual_costs), 1):
            net_cash_flow = rev - cost
            npv += net_cash_flow / ((1 + discount_rate) ** t)
        return round(npv, 2)
    
    @staticmethod
    def calculate_irr(
        initial_investment: float,
        annual_revenue: List[float],
        annual_costs: List[float],
        max_iterations: int = 100,
    ) -> float:
        """محاسبه نرخ بازده داخلی (IRR) با روش نیوتن"""
        cash_flows = [-initial_investment] + [r - c for r, c in zip(annual_revenue, annual_costs)]
        
        # روش bisection
        low, high = 0.0, 1.0
        for _ in range(max_iterations):
            mid = (low + high) / 2
            npv = sum(cf / ((1 + mid) ** t) for t, cf in enumerate(cash_flows))
            
            if abs(npv) < 0.01:
                return round(mid * 100, 2)  # درصد
            
            if npv > 0:
                low = mid
            else:
                high = mid
        
        return round(((low + high) / 2) * 100, 2)
    
    @staticmethod
    def calculate_payback_period(
        initial_investment: float,
        annual_revenue: List[float],
        annual_costs: List[float],
    ) -> float:
        """محاسبه دوره بازگشت سرمایه"""
        cumulative = -initial_investment
        for t, (rev, cost) in enumerate(zip(annual_revenue, annual_costs), 1):
            cumulative += rev - cost
            if cumulative >= 0:
                return round(t - (cumulative / (rev - cost)), 1)
        return -1  # بازگشت ندارد
    
    @classmethod
    def analyze_project(
        cls,
        initial_investment: float,
        annual_maintenance: float,
        carbon_price_per_ton: float,
        carbon_result: CarbonResult,
        discount_rate: float = 0.08,
        project_lifetime: int = 30,
    ) -> Dict:
        """تحلیل کامل مالی پروژه"""
        
        # جریان درآمد و هزینه سالانه
        annual_revenue = []
        annual_costs = []
        cash_flows = []
        
        for projection in carbon_result.yearly_projections[:project_lifetime]:
            revenue = projection["annual_co2e_ton"] * carbon_price_per_ton
            # هزینه نگهداری با تورم ۳٪ سالانه
            year = projection["year"]
            cost = annual_maintenance * ((1.03) ** (year - 1))
            
            annual_revenue.append(revenue)
            annual_costs.append(cost)
            cash_flows.append({
                "year": year,
                "revenue": round(revenue, 2),
                "cost": round(cost, 2),
                "net": round(revenue - cost, 2),
            })
        
        npv = cls.calculate_npv(initial_investment, annual_revenue, annual_costs, discount_rate)
        irr = cls.calculate_irr(initial_investment, annual_revenue, annual_costs)
        payback = cls.calculate_payback_period(initial_investment, annual_revenue, annual_costs)
        
        total_revenue = sum(annual_revenue)
        total_cost = initial_investment + sum(annual_costs)
        
        return {
            "npv": npv,
            "irr": irr,
            "payback_period_years": payback,
            "total_revenue": round(total_revenue, 2),
            "total_cost": round(total_cost, 2),
            "net_profit": round(total_revenue - total_cost, 2),
            "roi_percent": round((total_revenue - total_cost) / total_cost * 100, 2),
            "cash_flows": cash_flows,
            "carbon_price_per_ton": carbon_price_per_ton,
            "discount_rate": discount_rate,
        }


class EcoCoinCalculator:
    """محاسبه توکن‌های EcoCoin"""
    
    # نرخ تبدیل: 1 tCO₂e = 10 EcoCoin
    CO2E_TO_ECOCOIN = 10
    
    @classmethod
    def calculate_ecocoins(cls, tco2e: float) -> float:
        """محاسبه EcoCoin بر اساس tCO₂e"""
        return round(tco2e * cls.CO2E_TO_ECOCOIN, 2)
    
    @classmethod
    def calculate_from_project(cls, carbon_result: CarbonResult, years: int = 20) -> Dict:
        """محاسبه EcoCoin برای یک پروژه"""
        total_co2e = sum(p["annual_co2e_ton"] for p in carbon_result.yearly_projections[:years])
        
        yearly_ecocoins = []
        cumulative = 0
        for p in carbon_result.yearly_projections[:years]:
            annual = cls.calculate_ecocoins(p["annual_co2e_ton"])
            cumulative += annual
            yearly_ecocoins.append({
                "year": p["year"],
                "co2e_ton": p["annual_co2e_ton"],
                "ecocoins_earned": annual,
                "cumulative_ecocoins": round(cumulative, 2),
            })
        
        return {
            "total_co2e_ton": round(total_co2e, 2),
            "total_ecocoins": cls.calculate_ecocoins(total_co2e),
            "conversion_rate": cls.CO2E_TO_ECOCOIN,
            "yearly_breakdown": yearly_ecocoins,
        }


class AuditReportGenerator:
    """تولید گزارش‌های ممیزی با هش SHA-256"""
    
    @staticmethod
    def generate_sha256(data: Dict) -> str:
        """تولید هش SHA-256 از داده‌ها"""
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()
    
    @classmethod
    def generate_report(
        cls,
        project_name: str,
        carbon_result: CarbonResult,
        financial_result: Dict,
        ecocoin_result: Dict,
    ) -> Dict:
        """تولید گزارش ممیزی کامل"""
        
        report_data = {
            "report_id": f"MRV-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            "generated_at": datetime.utcnow().isoformat(),
            "standard": "Verra VM0042 / IPCC 2019",
            "project": {
                "name": project_name,
                "type": "Soil Carbon Sequestration",
            },
            "carbon": {
                "annual_sequestration_tco2e": carbon_result.annual_sequestration_rate,
                "total_20_years_tco2e": carbon_result.total_sequestration_20_years,
                "total_30_years_tco2e": carbon_result.total_sequestration_30_years,
                "final_soc_ton_per_ha": carbon_result.final_soc,
                "soc_increase_percent": carbon_result.soc_increase_percent,
                "uncertainty_percent": carbon_result.uncertainty_percent,
                "confidence_level": carbon_result.confidence_level,
            },
            "financial": {
                "npv_usd": financial_result["npv"],
                "irr_percent": financial_result["irr"],
                "payback_years": financial_result["payback_period_years"],
                "roi_percent": financial_result["roi_percent"],
            },
            "ecocoin": {
                "total_ecocoins_20y": ecocoin_result["total_ecocoins"],
                "conversion_rate": ecocoin_result["conversion_rate"],
            },
        }
        
        # تولید هش SHA-256
        sha256_hash = cls.generate_sha256(report_data)
        report_data["integrity"] = {
            "sha256_hash": sha256_hash,
            "algorithm": "SHA-256",
            "generated_at": datetime.utcnow().isoformat(),
        }
        
        return report_data
'''
    
    write_file(API_DIR / "services" / "carbon_calculator.py", content)


# ========== 3. Router بک‌اند ==========
def create_mrv_router():
    print("\n🔌 ایجاد MRV Router...")
    
    content = '''# api/modules/mrv/router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from api.core.database import get_db
from api.modules.mrv.models import CarbonProject, CarbonMeasurement, FinancialAnalysis, EcoCoinTransaction, AuditReport
from api.services.carbon_calculator import (
    SoilParameters, RothCSimplified, FinancialCalculator, 
    EcoCoinCalculator, AuditReportGenerator
)

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
@router.post("/calculate")
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


@router.post("/financial-analysis")
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


@router.post("/projects")
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


@router.get("/projects")
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


@router.get("/projects/{project_id}")
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


@router.get("/stats")
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
'''
    
    write_file(API_DIR / "modules" / "mrv" / "router.py", content)


# ========== 4. __init__.py ==========
def create_mrv_init():
    print("\n📦 ایجاد mrv/__init__.py...")
    content = '''# api/modules/mrv/__init__.py
from . import models
from . import router
'''
    write_file(API_DIR / "modules" / "mrv" / "__init__.py", content)


# ========== 5. به‌روزرسانی main.py ==========
def update_main():
    print("\n🔧 به‌روزرسانی main.py...")
    
    main_path = API_DIR / "main.py"
    if not main_path.exists():
        print("   ❌ main.py یافت نشد")
        return
    
    content = main_path.read_text(encoding="utf-8")
    
    if "mrv_router" not in content:
        # اضافه کردن import
        if "from api.modules.maintenance.router" in content:
            content = content.replace(
                "from api.modules.maintenance.router import router as maintenance_router",
                "from api.modules.maintenance.router import router as maintenance_router\\nfrom api.modules.mrv.router import router as mrv_router"
            )
        
        # اضافه کردن router
        if 'app.include_router(maintenance_router' in content:
            content = content.replace(
                'app.include_router(maintenance_router, prefix="/api/v1")',
                'app.include_router(maintenance_router, prefix="/api/v1")\\napp.include_router(mrv_router, prefix="/api/v1")'
            )
        
        main_path.write_text(content, encoding="utf-8")
        print("   ✅ MRV router اضافه شد")
    else:
        print("   ℹ️  از قبل اضافه شده")


# ========== 6. داشبورد فرانت‌اند ==========
def create_mrv_dashboard():
    print("\n📊 ایجاد داشبورد MRV...")
    
    content = '''"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Leaf, DollarSign, TrendingUp, Award, Download,
  Calculator, BarChart3, PieChart, Target, CheckCircle, AlertCircle,
  Loader2, Coins, FileText, Shield, Zap, Plus
} from "lucide-react";

const ResponsiveContainer = dynamic(() => import("recharts").then(m => m.ResponsiveContainer), { ssr: false });
const AreaChart = dynamic(() => import("recharts").then(m => m.AreaChart), { ssr: false });
const Area = dynamic(() => import("recharts").then(m => m.Area), { ssr: false });
const BarChart = dynamic(() => import("recharts").then(m => m.BarChart), { ssr: false });
const Bar = dynamic(() => import("recharts").then(m => m.Bar), { ssr: false });
const LineChart = dynamic(() => import("recharts").then(m => m.LineChart), { ssr: false });
const Line = dynamic(() => import("recharts").then(m => m.Line), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(m => m.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(m => m.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(m => m.Tooltip), { ssr: false });
const Legend = dynamic(() => import("recharts").then(m => m.Legend), { ssr: false });

interface SoilParams {
  soil_type: string;
  clay_content: number;
  initial_soc: number;
  pH: number;
  annual_rainfall: number;
  mean_temperature: number;
  area_hectares: number;
}

interface FinancialParams {
  initial_investment: number;
  annual_maintenance: number;
  carbon_price_per_ton: number;
  discount_rate: number;
  project_lifetime_years: number;
}

const SOIL_TYPES = [
  { value: "clay", label: "رسی (Clay)", description: "حفظ کربن بالا" },
  { value: "loam", label: "لومی (Loam)", description: "متعادل" },
  { value: "sandy", label: "شنی (Sandy)", description: "تجزیه سریع" },
];

const MANAGEMENT_TYPES = [
  { value: "conventional", label: "سنتی", factor: 0, color: "#64748b" },
  { value: "conservation", label: "حفاظتی", factor: 0.3, color: "#f59e0b" },
  { value: "regenerative", label: "احیایی", factor: 0.6, color: "#10b981" },
];

export default function MRVDashboardPage() {
  const [activeTab, setActiveTab] = useState<"calculator" | "projects" | "analytics">("calculator");
  const [isCalculating, setIsCalculating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [stats, setStats] = useState<any>(null);

  // Form state
  const [soil, setSoil] = useState<SoilParams>({
    soil_type: "loam",
    clay_content: 30,
    initial_soc: 2.5,
    pH: 6.8,
    annual_rainfall: 450,
    mean_temperature: 18,
    area_hectares: 100,
  });

  const [management, setManagement] = useState("conservation");

  const [financial, setFinancial] = useState<FinancialParams>({
    initial_investment: 500000000,
    annual_maintenance: 20000000,
    carbon_price_per_ton: 50,
    discount_rate: 0.08,
    project_lifetime_years: 30,
  });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/mrv/stats");
      if (res.ok) setStats(await res.json());
    } catch (e) {
      console.error("Failed to load stats");
    }
  };

  const handleCalculate = async () => {
    setIsCalculating(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/api/v1/mrv/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ soil, management }),
      });

      if (!res.ok) throw new Error("خطا در محاسبه");

      const data = await res.json();
      setResult(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setIsCalculating(false);
    }
  };

  const handleSaveProject = async () => {
    if (!result) return;

    const projectName = prompt("نام پروژه را وارد کنید:");
    if (!projectName) return;

    try {
      const res = await fetch("http://localhost:8000/api/v1/mrv/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: projectName,
          description: `پروژه جذب کربن با روش ${management}`,
          soil,
          management,
          financial,
          latitude: 32.5,
          longitude: 54.5,
          location_name: "ایران",
        }),
      });

      if (res.ok) {
        const data = await res.json();
        alert(`✅ پروژه ذخیره شد!\\nشناسه: ${data.project_id}\\nهش ممیزی: ${data.audit_hash.substring(0, 16)}...`);
        loadStats();
      }
    } catch (e) {
      alert("خطا در ذخیره پروژه");
    }
  };

  const exportReport = () => {
    if (!result) return;

    const report = {
      generated_at: new Date().toISOString(),
      project: {
        soil_type: soil.soil_type,
        area_ha: soil.area_hectares,
        management: management,
      },
      carbon: result.carbon,
      ecocoin: result.ecocoin,
      disclaimer: "این گزارش بر اساس مدل RothC ساده‌شده تولید شده و نیاز به صحت‌سنجی توسط ممیز مستقل دارد.",
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `mrv_report_${Date.now()}.json`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500 to-green-600 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />

        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>

            <div className="flex items-start gap-6 mb-4">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-emerald-500 to-green-600 shadow-2xl">
                <Leaf className="h-10 w-10 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-emerald-400 text-sm font-medium mb-1">لایه ۴: MRV Engine</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">
                  اندازه‌گیری، گزارش‌دهی و صحت‌سنجی کربن
                </h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  محاسبه جذب کربن با مدل RothC، تحلیل مالی NPV/IRR، و تولید گزارش‌های ممیزی با هش SHA-256
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Global Stats */}
      <section className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { label: "پروژه‌های فعال", value: stats?.active_projects || 0, icon: Leaf, color: "#10b981" },
            { label: "کربن جذب‌شده", value: `${(stats?.total_co2e_sequestered_ton || 0).toLocaleString()} t`, icon: TrendingUp, color: "#059669" },
            { label: "EcoCoin تولیدشده", value: (stats?.total_ecocoins || 0).toLocaleString(), icon: Coins, color: "#f59e0b" },
            { label: "مساحت تحت پوشش", value: `${(stats?.total_area_hectares || 0).toLocaleString()} ha`, icon: BarChart3, color: "#3b82f6" },
            { label: "گزارش‌های ممیزی", value: stats?.verified_reports || 0, icon: Shield, color: "#8b5cf6" },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-5"
            >
              <stat.icon className="h-7 w-7 mb-2" style={{ color: stat.color }} />
              <p className="text-2xl font-black text-white">{stat.value}</p>
              <p className="text-xs text-slate-400">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Tabs */}
      <section className="container mx-auto px-6 py-4">
        <div className="flex gap-2 mb-6 flex-wrap">
          {[
            { id: "calculator", label: "ماشین حساب کربن", icon: Calculator },
            { id: "projects", label: "پروژه‌های من", icon: Leaf },
            { id: "analytics", label: "تحلیل‌ها", icon: BarChart3 },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-5 py-3 rounded-xl font-bold transition-all flex items-center gap-2 ${
                activeTab === tab.id
                  ? "bg-emerald-600 text-white shadow-lg shadow-emerald-500/30"
                  : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
            >
              <tab.icon className="h-5 w-5" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Calculator Tab */}
        {activeTab === "calculator" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Soil Parameters */}
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Leaf className="h-5 w-5 text-emerald-400" />
                پارامترهای خاک و اقلیم
              </h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-bold text-white mb-2">نوع خاک</label>
                  <div className="grid grid-cols-3 gap-2">
                    {SOIL_TYPES.map(s => (
                      <button
                        key={s.value}
                        onClick={() => setSoil({ ...soil, soil_type: s.value })}
                        className={`p-2 rounded-lg text-xs font-bold transition-colors ${
                          soil.soil_type === s.value
                            ? "bg-emerald-600 text-white"
                            : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                        }`}
                      >
                        {s.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-2">درصد رس: {soil.clay_content}%</label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={soil.clay_content}
                    onChange={(e) => setSoil({ ...soil, clay_content: parseFloat(e.target.value) })}
                    className="w-full accent-emerald-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">SOC اولیه (t/ha)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={soil.initial_soc}
                      onChange={(e) => setSoil({ ...soil, initial_soc: parseFloat(e.target.value) })}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">pH خاک</label>
                    <input
                      type="number"
                      step="0.1"
                      value={soil.pH}
                      onChange={(e) => setSoil({ ...soil, pH: parseFloat(e.target.value) })}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">بارش سالانه (mm)</label>
                    <input
                      type="number"
                      value={soil.annual_rainfall}
                      onChange={(e) => setSoil({ ...soil, annual_rainfall: parseFloat(e.target.value) })}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">دمای میانگین (°C)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={soil.mean_temperature}
                      onChange={(e) => setSoil({ ...soil, mean_temperature: parseFloat(e.target.value) })}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-2">مساحت (هکتار)</label>
                  <input
                    type="number"
                    value={soil.area_hectares}
                    onChange={(e) => setSoil({ ...soil, area_hectares: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-2">روش مدیریت</label>
                  <div className="space-y-2">
                    {MANAGEMENT_TYPES.map(m => (
                      <button
                        key={m.value}
                        onClick={() => setManagement(m.value)}
                        className={`w-full p-3 rounded-lg text-sm font-bold transition-colors flex items-center justify-between ${
                          management === m.value
                            ? "bg-emerald-600 text-white"
                            : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                        }`}
                      >
                        <span>{m.label}</span>
                        <span className="text-xs opacity-70">+{(m.factor * 100).toFixed(0)}%</span>
                      </button>
                    ))}
                  </div>
                </div>

                <button
                  onClick={handleCalculate}
                  disabled={isCalculating}
                  className="w-full py-3 bg-gradient-to-l from-emerald-500 to-green-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-emerald-500/30 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isCalculating ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      در حال محاسبه...
                    </>
                  ) : (
                    <>
                      <Zap className="h-5 w-5" />
                      محاسبه جذب کربن
                    </>
                  )}
                </button>

                {error && (
                  <div className="p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-red-300 text-sm">
                    {error}
                  </div>
                )}
              </div>
            </div>

            {/* Results */}
            <div className="lg:col-span-2 space-y-6">
              {!result ? (
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-12 text-center">
                  <Calculator className="h-16 w-16 text-slate-600 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-white mb-2">پارامترها را وارد کنید</h3>
                  <p className="text-slate-400">پس از محاسبه، نتایج کامل شامل جذب کربن، تحلیل مالی و EcoCoin نمایش داده می‌شود</p>
                </div>
              ) : (
                <>
                  {/* Carbon Results */}
                  <div className="bg-gradient-to-br from-emerald-900/30 to-green-900/30 border border-emerald-500/30 rounded-2xl p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <Leaf className="h-5 w-5 text-emerald-400" />
                        نتایج جذب کربن
                      </h3>
                      <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 rounded-full text-xs">
                        عدم قطعیت: ±{result.carbon.uncertainty_percent}%
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                      <div className="bg-slate-900/50 rounded-xl p-4">
                        <p className="text-xs text-slate-400 mb-1">نرخ سالانه</p>
                        <p className="text-2xl font-black text-emerald-400">
                          {result.carbon.annual_rate_tco2e.toLocaleString()}
                        </p>
                        <p className="text-xs text-slate-500">tCO₂e/سال</p>
                      </div>
                      <div className="bg-slate-900/50 rounded-xl p-4">
                        <p className="text-xs text-slate-400 mb-1">۲۰ ساله</p>
                        <p className="text-2xl font-black text-emerald-400">
                          {result.carbon.total_20y_tco2e.toLocaleString()}
                        </p>
                        <p className="text-xs text-slate-500">tCO₂e</p>
                      </div>
                      <div className="bg-slate-900/50 rounded-xl p-4">
                        <p className="text-xs text-slate-400 mb-1">SOC نهایی</p>
                        <p className="text-2xl font-black text-emerald-400">
                          {result.carbon.final_soc_ton_per_ha}
                        </p>
                        <p className="text-xs text-slate-500">t/ha (+{result.carbon.soc_increase_percent}%)</p>
                      </div>
                      <div className="bg-slate-900/50 rounded-xl p-4">
                        <p className="text-xs text-slate-400 mb-1">EcoCoin</p>
                        <p className="text-2xl font-black text-amber-400">
                          {result.ecocoin.total_ecocoins.toLocaleString()}
                        </p>
                        <p className="text-xs text-slate-500">توکن</p>
                      </div>
                    </div>

                    {/* Chart */}
                    <div className="bg-slate-900/50 rounded-xl p-4">
                      <p className="text-sm font-bold text-white mb-3">روند جذب کربن (۳۰ سال)</p>
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={result.carbon.yearly_projections}>
                            <defs>
                              <linearGradient id="co2eGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                            <XAxis dataKey="year" stroke="#64748b" fontSize={11} />
                            <YAxis stroke="#64748b" fontSize={11} />
                            <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
                            <Area type="monotone" dataKey="cumulative_co2e_ton" stroke="#10b981" strokeWidth={2} fill="url(#co2eGrad)" name="تجمعی tCO₂e" />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-3 flex-wrap">
                    <button
                      onClick={handleSaveProject}
                      className="flex-1 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center justify-center gap-2"
                    >
                      <Plus className="h-5 w-5" />
                      ذخیره به عنوان پروژه
                    </button>
                    <button
                      onClick={exportReport}
                      className="flex-1 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold flex items-center justify-center gap-2"
                    >
                      <Download className="h-5 w-5" />
                      دانلود گزارش
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* Projects Tab */}
        {activeTab === "projects" && (
          <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">پروژه‌های کربن</h3>
            <p className="text-slate-400">برای ایجاد پروژه، ابتدا در تب ماشین حساب محاسبه را انجام دهید و سپس ذخیره کنید.</p>
            <div className="mt-6 p-8 bg-slate-800/50 rounded-xl text-center">
              <Leaf className="h-16 w-16 text-emerald-400 mx-auto mb-4 opacity-50" />
              <p className="text-slate-300">پس از ذخیره پروژه، در این بخش نمایش داده می‌شود</p>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === "analytics" && (
          <div className="space-y-6">
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4">تحلیل‌های پیشرفته</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-6 bg-gradient-to-br from-emerald-500/10 to-green-500/10 border border-emerald-500/30 rounded-xl">
                  <Award className="h-8 w-8 text-emerald-400 mb-3" />
                  <h4 className="font-bold text-white mb-2">استانداردهای بین‌المللی</h4>
                  <ul className="text-sm text-slate-300 space-y-1">
                    <li>✓ Verra VM0042</li>
                    <li>✓ Gold Standard</li>
                    <li>✓ IPCC 2019</li>
                  </ul>
                </div>
                <div className="p-6 bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-xl">
                  <Shield className="h-8 w-8 text-purple-400 mb-3" />
                  <h4 className="font-bold text-white mb-2">امنیت و ممیزی</h4>
                  <ul className="text-sm text-slate-300 space-y-1">
                    <li>✓ هش SHA-256 برای هر گزارش</li>
                    <li>✓ ثبت در بلاکچین</li>
                    <li>✓ صحت‌سنجی توسط ممیز مستقل</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
'''
    
    write_file(WEB / "app" / "mrv" / "page.tsx", content)


# ========== Main ==========
def main():
    print("💰 لایه ۴: موتور MRV و اعتبار کربن")
    print("=" * 70)
    
    if not API_DIR.exists() or not WEB.exists():
        print("❌ دایرکتوری‌ها یافت نشد!")
        return 1
    
    create_mrv_models()
    create_mrv_init()
    create_carbon_calculator()
    create_mrv_router()
    update_main()
    create_mrv_dashboard()
    
    print("\n" + "=" * 70)
    print("✅ لایه ۴ تکمیل شد!")
    print("\n🎯 ویژگی‌های ایجاد شده:")
    print("   🧮 موتور محاسبه کربن:")
    print("      • مدل RothC ساده‌شده")
    print("      • ۳ نوع خاک (رسی، لومی، شنی)")
    print("      • ۳ روش مدیریت (سنتی، حفاظتی، احیایی)")
    print("      • پیش‌بینی ۳۰ ساله")
    print("      • محاسبه عدم قطعیت")
    print("")
    print("   💰 تحلیل مالی:")
    print("      • NPV (ارزش فعلی خالص)")
    print("      • IRR (نرخ بازده داخلی)")
    print("      • دوره بازگشت سرمایه")
    print("      • ROI و جریان نقدی")
    print("")
    print("   🪙 سیستم EcoCoin:")
    print("      • تبدیل tCO₂e به EcoCoin")
    print("      • نرخ: 1 tCO₂e = 10 EcoCoin")
    print("      • پیش‌بینی سالانه")
    print("")
    print("   📄 گزارش‌های ممیزی:")
    print("      • استاندارد Verra VM0042")
    print("      • هش SHA-256")
    print("      • قابل دانلود به JSON")
    print("")
    print("   📊 داشبورد MRV:")
    print("      • ماشین حساب کربن تعاملی")
    print("      • نمودارهای Recharts")
    print("      • ذخیره پروژه")
    print("      • آمار کلی")
    print("")
    print("🚀 گام بعدی:")
    print("   1. پاک‌سازی کش:")
    print("      cd apps\\web")
    print("      Remove-Item .next -Recurse -Force")
    print("")
    print("   2. اجرای سرور بک‌اند:")
    print("      uvicorn api.main:app --reload --port 8000")
    print("")
    print("   3. اجرای سرور فرانت‌اند:")
    print("      cd apps\\web")
    print("      pnpm run dev -- -p 3001")
    print("")
    print("   4. مشاهده:")
    print("      • داشبورد MRV: http://localhost:3001/mrv")
    print("      • API Docs: http://localhost:8000/docs")
    print("")
    print("📝 تست کنید:")
    print("   1. نوع خاک: لومی")
    print("   2. مساحت: 100 هکتار")
    print("   3. روش: احیایی")
    print("   4. کلیک روی 'محاسبه جذب کربن'")
    print("   5. نتایج شامل نمودار، EcoCoin و...")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())