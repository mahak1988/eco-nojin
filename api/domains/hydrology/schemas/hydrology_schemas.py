"""Hydrology Domain Schemas - Pydantic Models"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from .models.hydrology_models import ModelType, SimulationStatus


class WatershedCreate(BaseModel):
    """اسکیما برای ایجاد حوضه آبخیز"""
    watershed_id: str
    name: str
    area_km2: float = Field(..., gt=0)
    outlet_lat: float = Field(..., ge=-90, le=90)
    outlet_lon: float = Field(..., ge=-180, le=180)
    pilot_site: Optional[str] = None
    elevation_min: Optional[float] = None
    elevation_max: Optional[float] = None
    avg_slope: Optional[float] = None


class WatershedResponse(BaseModel):
    """اسکیما پاسخ حوضه آبخیز"""
    watershed_id: str
    name: str
    area_km2: float
    outlet_lat: float
    outlet_lon: float
    pilot_site: Optional[str]
    
    class Config:
        from_attributes = True


class ScenarioCreate(BaseModel):
    """اسکیما برای ایجاد سناریو"""
    name: str
    description: str
    model_type: ModelType
    watershed_id: str
    start_date: datetime
    end_date: datetime
    parameters: Dict = {}
    climate_data_source: str = "historical"


class ScenarioResponse(BaseModel):
    """اسکیما پاسخ سناریو"""
    scenario_id: str
    name: str
    model_type: ModelType
    watershed_id: str
    start_date: datetime
    end_date: datetime
    status: SimulationStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class SimulationResultResponse(BaseModel):
    """اسکیما پاسخ نتایج شبیه‌سازی"""
    result_id: str
    scenario_id: str
    model_type: ModelType
    watershed_id: str
    runoff_monthly: List[float]
    baseflow_monthly: List[float]
    evapotranspiration_monthly: List[float]
    water_balance: Dict
    created_at: datetime
    
    class Config:
        from_attributes = True


class WaterBalanceRequest(BaseModel):
    """درخواست محاسبه بیلان آبی"""
    watershed_id: str
    start_date: datetime
    end_date: datetime
    precipitation_mm: float
    temperature_c: float
    land_use: str


class WaterAllocationRequest(BaseModel):
    """درخواست تخصیص آب"""
    watershed_id: str
    scenario_id: str
    sector: str
    demand_m3: float
    priority: int = 1
