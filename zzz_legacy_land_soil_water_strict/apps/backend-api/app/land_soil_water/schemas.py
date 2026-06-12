# apps/backend-api/app/land_soil_water/schemas.py

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Literal, Dict

from pydantic import BaseModel, Field, constr, conlist, confloat


class ScenarioType(str, Enum):
    BASELINE = "baseline"
    MANAGEMENT = "management"


class GeometryType(str, Enum):
    POLYGON = "polygon"
    POINT = "point"
    RASTER_CELL = "raster_cell"


class IndicatorCode(str, Enum):
    RUNOFF_MM = "runoff_mm"
    SOIL_LOSS_T_HA = "soil_loss_t_ha"
    SOIL_WATER_CONTENT_MM = "soil_water_content_mm"
    INFILTRATION_MM = "infiltration_mm"
    EROSION_RISK_INDEX = "erosion_risk_index"


class LandUnit(BaseModel):
    id: constr(min_length=1, max_length=64)
    name: constr(min_length=1, max_length=256)
    geometry_type: GeometryType
    area_ha: confloat(ge=0)
    centroid_lat: confloat(ge=-90, le=90)
    centroid_lon: confloat(ge=-180, le=180)
    region_id: Optional[constr(max_length=64)] = None


class SoilProfile(BaseModel):
    land_unit_id: constr(min_length=1, max_length=64)
    depth_cm: confloat(gt=0)
    texture: constr(min_length=1, max_length=64)
    organic_carbon_pct: confloat(ge=0, le=20)
    bulk_density: confloat(gt=0, le=2.5)
    available_water_capacity: confloat(ge=0)


class ClimatePoint(BaseModel):
    date: date
    precipitation_mm: confloat(ge=0)
    tmean_c: Optional[float] = None
    et0_mm: Optional[confloat(ge=0)] = None


class IndicatorTimeseriesPoint(BaseModel):
    date: date
    value: float


class IndicatorTimeseries(BaseModel):
    indicator: IndicatorCode
    unit: constr(min_length=1, max_length=32)
    series: List[IndicatorTimeseriesPoint]


class ScenarioPractice(BaseModel):
    code: constr(min_length=1, max_length=64)
    description: Optional[str] = None


class Scenario(BaseModel):
    id: Optional[constr(min_length=1, max_length=64)] = None
    name: constr(min_length=1, max_length=256)
    description: Optional[str] = None
    scenario_type: ScenarioType = ScenarioType.MANAGEMENT
    land_unit_ids: conlist(str, min_items=1)
    practices: List[ScenarioPractice] = Field(default_factory=list)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    FINALIZED = "finalized"
    ON_CHAIN_REGISTERED = "on_chain_registered"


class AnalysisSummary(BaseModel):
    id: constr(min_length=1, max_length=64)
    user_id: constr(min_length=1, max_length=64)
    land_unit_id: constr(min_length=1, max_length=64)
    scenario_id: Optional[constr(min_length=1, max_length=64)] = None
    scenario_type: ScenarioType
    status: AnalysisStatus
    created_at: datetime
    updated_at: datetime
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    indicators_avg: Dict[IndicatorCode, float] = Field(
        default_factory=dict,
        description="میانگین شاخص‌ها در دوره تحلیل"
    )


class AnalysisDetail(BaseModel):
    summary: AnalysisSummary
    soil_profile: Optional[SoilProfile] = None
    climate: Optional[List[ClimatePoint]] = None
    timeseries: List[IndicatorTimeseries] = Field(default_factory=list)


class LandUnitFilter(BaseModel):
    region_id: Optional[str] = None
    indicator: Optional[IndicatorCode] = None
    indicator_min: Optional[float] = None
    indicator_max: Optional[float] = None


class LandUnitWithIndicators(BaseModel):
    land_unit: LandUnit
    indicators_avg: Dict[IndicatorCode, float] = Field(default_factory=dict)


class LandUnitListResponse(BaseModel):
    items: List[LandUnitWithIndicators]
    total: int


class CreateAnalysisRequest(BaseModel):
    land_unit_id: constr(min_length=1, max_length=64)
    scenario: Scenario
    indicators: Optional[List[IndicatorCode]] = None


class CreateAnalysisResponse(BaseModel):
    analysis_id: constr(min_length=1, max_length=64)
    status: AnalysisStatus


class FinalizeAnalysisRequest(BaseModel):
    store_on_chain: bool = Field(
        default=False,
        description="اگر True باشد، پس از نهایی‌سازی تلاش می‌شود در قرارداد هوشمند ثبت شود."
    )


class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    GEOJSON = "geojson"
    PDF = "pdf"


class IndicatorDefinition(BaseModel):
    code: IndicatorCode
    unit: str
    title_fa: str
    title_en: str
    description_fa: Optional[str] = None
    description_en: Optional[str] = None


class IndicatorListResponse(BaseModel):
    indicators: List[IndicatorDefinition]