# api/services/carbon_calculator.py
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
