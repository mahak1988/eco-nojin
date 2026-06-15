"""Financial Repository with database integration."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from .models.db_models import ProjectBudgetDB, CarbonCreditDB
from .models.financial_models import ProjectBudget, CarbonCredit


class FinancialRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def save_budget(self, budget: ProjectBudget) -> bool:
        """ذخیره بودجه پروژه"""
        db_obj = ProjectBudgetDB(
            project_id=budget.project_id,
            capex=budget.capex,
            opex_annual=budget.opex_annual,
            currency=budget.currency
        )
        self.db.add(db_obj)
        self.db.commit()
        return True
    
    def get_budget(self, project_id: str) -> Optional[ProjectBudget]:
        """دریافت بودجه پروژه"""
        result = self.db.query(ProjectBudgetDB).filter(
            ProjectBudgetDB.project_id == project_id
        ).first()
        
        if result:
            return ProjectBudget(
                project_id=result.project_id,
                capex=result.capex,
                opex_annual=result.opex_annual,
                currency=result.currency,
                breakdown={}
            )
        return None
    
    def issue_carbon_credit(
        self,
        project_id: str,
        volume_tco2e: float,
        price_per_ton: float
    ) -> Optional[CarbonCredit]:
        """صدور اعتبار کربن"""
        db_obj = CarbonCreditDB(
            project_id=project_id,
            volume_tco2e=volume_tco2e,
            verification_date=datetime.utcnow(),
            price_per_ton=price_per_ton,
            status="VERIFIED"
        )
        self.db.add(db_obj)
        self.db.commit()
        
        return CarbonCredit(
            project_id=project_id,
            volume_tco2e=volume_tco2e,
            verification_date=datetime.utcnow(),
            price_per_ton=price_per_ton,
            status="VERIFIED"
        )
    
    def get_carbon_credits(self, project_id: str) -> List[CarbonCredit]:
        """دریافت اعتبارات کربن پروژه"""
        results = self.db.query(CarbonCreditDB).filter(
            CarbonCreditDB.project_id == project_id
        ).all()
        
        return [
            CarbonCredit(
                project_id=r.project_id,
                volume_tco2e=r.volume_tco2e,
                verification_date=r.verification_date,
                price_per_ton=r.price_per_ton,
                status=r.status
            )
            for r in results
        ]
