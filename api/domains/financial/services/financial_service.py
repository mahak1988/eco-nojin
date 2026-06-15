"""Financial Service with real NPV and IRR calculations."""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from .repositories.financial_repository import FinancialRepository
from .models.financial_models import ProjectBudget, CarbonCredit


class FinancialService:
    def __init__(self, repository: FinancialRepository):
        self.repo = repository
    
    def calculate_npv(
        self,
        initial_investment: float,
        cash_flows: List[float],
        discount_rate: float
    ) -> float:
        """محاسبه واقعی NPV (Net Present Value)"""
        npv = -initial_investment
        for year, cash_flow in enumerate(cash_flows, 1):
            npv += cash_flow / ((1 + discount_rate) ** year)
        return round(npv, 2)
    
    def calculate_irr(self, cash_flows: List[float], max_iterations: int = 100) -> float:
        """محاسبه IRR با روش نیوتن-رافسون"""
        if not cash_flows or cash_flows[0] >= 0:
            return 0.0
        
        # حدس اولیه
        irr = 0.1
        
        for _ in range(max_iterations):
            # محاسبه NPV و مشتق آن
            npv = sum(cf / ((1 + irr) ** t) for t, cf in enumerate(cash_flows))
            derivative = sum(-t * cf / ((1 + irr) ** (t + 1)) for t, cf in enumerate(cash_flows))
            
            if abs(derivative) < 1e-10:
                break
            
            # به‌روزرسانی با روش نیوتن
            new_irr = irr - npv / derivative
            
            if abs(new_irr - irr) < 1e-6:
                return round(new_irr, 4)
            
            irr = new_irr
        
        return round(irr, 4)
    
    def calculate_benefit_cost_ratio(
        self,
        benefits: List[float],
        costs: List[float],
        discount_rate: float
    ) -> float:
        """محاسبه نسبت منافع به هزینه‌ها"""
        pv_benefits = sum(b / ((1 + discount_rate) ** t) for t, b in enumerate(benefits, 1))
        pv_costs = sum(c / ((1 + discount_rate) ** t) for t, c in enumerate(costs, 1))
        
        if pv_costs == 0:
            return 0.0
        
        return round(pv_benefits / pv_costs, 2)
    
    def calculate_payback_period(
        self,
        initial_investment: float,
        annual_cash_flows: List[float]
    ) -> float:
        """محاسبه دوره بازگشت سرمایه"""
        cumulative = -initial_investment
        
        for year, cash_flow in enumerate(annual_cash_flows, 1):
            cumulative += cash_flow
            if cumulative >= 0:
                # بازگشت در میانه سال
                previous = cumulative - cash_flow
                fraction = abs(previous) / cash_flow
                return round(year - 1 + fraction, 2)
        
        return -1  # بازگشت نشده
    
    def evaluate_project(
        self,
        project_id: str,
        initial_investment: float,
        cash_flows: List[float],
        discount_rate: float = 0.1
    ) -> dict:
        """ارزیابی کامل اقتصادی پروژه"""
        npv = self.calculate_npv(initial_investment, cash_flows, discount_rate)
        irr = self.calculate_irr([-initial_investment] + cash_flows)
        payback = self.calculate_payback_period(initial_investment, cash_flows)
        bcr = self.calculate_benefit_cost_ratio(cash_flows, [initial_investment] + [0] * (len(cash_flows) - 1), discount_rate)
        
        # تصمیم‌گیری
        if npv > 0 and irr > discount_rate and payback > 0 and payback < 10:
            recommendation = "STRONG_INVEST"
        elif npv > 0 and irr > discount_rate:
            recommendation = "INVEST"
        elif npv > 0:
            recommendation = "CONDITIONAL_INVEST"
        else:
            recommendation = "DO_NOT_INVEST"
        
        return {
            "project_id": project_id,
            "npv": npv,
            "irr": irr,
            "payback_period_years": payback,
            "benefit_cost_ratio": bcr,
            "recommendation": recommendation,
            "analysis_date": datetime.utcnow().isoformat()
        }
    
    def issue_carbon_credit(
        self,
        project_id: str,
        volume_tco2e: float,
        price_per_ton: float = 25.0
    ) -> dict:
        """صدور اعتبار کربن"""
        credit = self.repo.issue_carbon_credit(project_id, volume_tco2e, price_per_ton)
        
        if credit:
            return {
                "project_id": project_id,
                "volume_tco2e": volume_tco2e,
                "price_per_ton": price_per_ton,
                "total_value": round(volume_tco2e * price_per_ton, 2),
                "status": credit.status,
                "issued_at": datetime.utcnow().isoformat()
            }
        
        return {"error": "Failed to issue carbon credit"}
