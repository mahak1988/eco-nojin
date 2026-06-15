"""Financial Domain Models."""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class ProjectBudget:
    project_id: str
    capex: float
    opex_annual: float
    currency: str
    breakdown: dict


@dataclass
class EconomicIndicator:
    npv: float
    irr: float
    benefit_cost_ratio: float
    payback_period_years: float


@dataclass
class CarbonCredit:
    project_id: str
    volume_tco2e: float
    verification_date: datetime
    price_per_ton: float
    status: str
