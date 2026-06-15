"""Hydrology Domain Models - Watershed & Simulation"""
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class ModelType(str, Enum):
    """انواع مدل‌های هیدرولوژیک"""
    SWAT = "swat"
    WEAP = "weap"
    AQUACROP = "aquacrop"
    CUSTOM = "custom"


class SimulationStatus(str, Enum):
    """وضعیت شبیه‌سازی"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Watershed:
    """نماینده یک حوضه آبخیز"""
    watershed_id: str
    name: str
    area_km2: float
    outlet_lat: float
    outlet_lon: float
    pilot_site: Optional[str] = None
    elevation_min: Optional[float] = None
    elevation_max: Optional[float] = None
    avg_slope: Optional[float] = None
    soil_types: List[str] = field(default_factory=list)
    land_uses: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HydrologicalScenario:
    """نماینده یک سناریوی هیدرولوژیک"""
    scenario_id: str
    name: str
    description: str
    model_type: ModelType
    watershed_id: str
    start_date: datetime
    end_date: datetime
    parameters: Dict = field(default_factory=dict)
    climate_data_source: str = "historical"
    status: SimulationStatus = SimulationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass
class SimulationResult:
    """نتایج شبیه‌سازی هیدرولوژیک"""
    result_id: str
    scenario_id: str
    model_type: ModelType
    watershed_id: str
    start_date: datetime
    end_date: datetime
    runoff_monthly: List[float] = field(default_factory=list)
    baseflow_monthly: List[float] = field(default_factory=list)
    evapotranspiration_monthly: List[float] = field(default_factory=list)
    soil_moisture_monthly: List[float] = field(default_factory=list)
    groundwater_recharge_monthly: List[float] = field(default_factory=list)
    water_balance: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WaterAllocation:
    """تخصیص آب بین مصرف‌کنندگان"""
    allocation_id: str
    watershed_id: str
    scenario_id: str
    sector: str  # agriculture, domestic, industrial, environmental
    allocation_m3: float
    priority: int
    efficiency: float = 0.7
    timestamp: datetime = field(default_factory=datetime.utcnow)
