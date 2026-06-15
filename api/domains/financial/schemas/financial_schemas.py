"""Financial Domain Schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProjectBudgetRequest(BaseModel):
    project_id: str
    capex: float = Field(..., gt=0)
    opex_annual: float = Field(..., ge=0)
    currency: str = Field(default="USD")


class EconomicIndicatorResponse(BaseModel):
    npv: float
    irr: float
    benefit_cost_ratio: float
    payback_period_years: float
    recommendation: str


class CarbonCreditResponse(BaseModel):
    project_id: str
    volume_tco2e: float
    price_per_ton: float
    total_value: float
    status: str
