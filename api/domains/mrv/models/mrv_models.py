"""MRV Domain Models"""
from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime


@dataclass
class MRVReport:
    """گزارش MRV"""
    report_id: str
    project_id: str
    reporting_period_start: datetime
    reporting_period_end: datetime
    area_ha: float
    land_use: str
    climate_zone: str
    soc_change_tCO2: float
    biomass_sequestration_tCO2: float
    n2o_emissions_tCO2e: float
    ch4_emissions_tCO2e: float
    net_carbon_balance_tCO2e: float
    methodology: str
    verified: bool
    created_at: datetime


@dataclass
class CarbonCredit:
    """اعتبار کربن"""
    credit_id: str
    project_id: str
    volume_tCO2e: float
    issuance_date: datetime
    verification_date: datetime
    price_per_ton: float
    currency: str
    status: str  # VERIFIED, ISSUED, RETIRED
    blockchain_tx_hash: Optional[str]
