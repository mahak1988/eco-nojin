"""
Soil & Water Schemas - Complete Version with CRUD
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


# ============================================================================
# Index Result Types
# ============================================================================
class LDNResult(BaseModel):
    ldn_score: float
    status: str
    soil_organic_carbon: float
    vegetation_cover: float
    erosion_risk: float


class NDVIResult(BaseModel):
    ndvi: float
    vegetation_health: str


class NDWIResult(BaseModel):
    ndwi: float
    water_presence: bool


class RUSLEResult(BaseModel):
    soil_loss_tons_per_ha: float
    erosion_risk_category: str
    r_factor: float
    k_factor: float
    ls_factor: float
    c_factor: float
    p_factor: float


class WaterBalanceResult(BaseModel):
    precipitation: float
    evapotranspiration: float
    runoff: float
    net_water: float
    soil_moisture_initial: float
    soil_moisture_final: float
    soil_moisture_change: float
    water_surplus: bool


class IrrigationResult(BaseModel):
    water_requirement_mm: float
    irrigation_interval_days: int
    efficiency_percentage: float
    depletion_fraction: float
    crop_type: str
    recommended_date: str


class DroughtResult(BaseModel):
    spi: float
    drought_category: str


class CarbonResult(BaseModel):
    carbon_stock_tons_per_ha: float
    soil_organic_carbon_pct: float
    bulk_density: float
    depth_cm: float


# ============================================================================
# Comprehensive Analysis
# ============================================================================
class ComprehensiveIndices(BaseModel):
    ldn: Optional[LDNResult] = None
    ndvi: Optional[NDVIResult] = None
    ndwi: Optional[NDWIResult] = None
    rusle: Optional[RUSLEResult] = None
    water_balance: Optional[WaterBalanceResult] = None
    irrigation: Optional[IrrigationResult] = None
    drought: Optional[DroughtResult] = None
    carbon: Optional[CarbonResult] = None


class ComprehensiveAnalysisRequest(BaseModel):
    ldn: Optional[dict] = None
    ndvi: Optional[dict] = None
    ndwi: Optional[dict] = None
    rusle: Optional[dict] = None
    water_balance: Optional[dict] = None
    irrigation: Optional[dict] = None
    drought: Optional[dict] = None
    carbon: Optional[dict] = None


class ComprehensiveAnalysisResponse(BaseModel):
    indices: ComprehensiveIndices
    overall_health: str
    overall_score: float
    recommendations: List[str]
    timestamp: str


# ============================================================================
# Project CRUD
# ============================================================================
class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    farmer_id: Optional[int] = None
    area_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    crop_type: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    area_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    crop_type: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    farmer_id: Optional[int] = None
    area_hectares: Optional[float] = None
    soil_type: Optional[str] = None
    crop_type: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    analysis_count: int = 0
    
    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    analyses: List["AnalysisReportResponse"] = []


# ============================================================================
# Analysis Report CRUD
# ============================================================================
class AnalysisReportCreate(BaseModel):
    project_id: Optional[int] = None
    title: str
    inputs: dict
    results: dict
    notes: Optional[str] = None


class AnalysisReportUpdate(BaseModel):
    title: Optional[str] = None
    notes: Optional[str] = None


class AnalysisReportResponse(BaseModel):
    id: int
    project_id: Optional[int] = None
    title: str
    inputs: Optional[dict] = None
    results: Optional[dict] = None
    overall_score: Optional[float] = None
    overall_health: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Dashboard Stats
# ============================================================================
class DashboardStats(BaseModel):
    total_projects: int
    active_projects: int
    total_analyses: int
    avg_score: float
    health_distribution: Dict[str, int]
    recent_analyses: List[AnalysisReportResponse]
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ... (کدهای قبلی فایل)

class SoilWaterAnalysisCreate(BaseModel):
    """Schema for creating a soil-water analysis"""
    region: str = Field(..., description="نام منطقه")
    soil_type: Optional[str] = Field(None, description="نوع خاک")
    area_ha: float = Field(..., gt=0, description="مساحت به هکتار")
    crop: str = Field(..., description="نوع محصول")
    irrigation_method: Optional[str] = Field(None, description="روش آبیاری")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="پارامترهای اضافی")

class SoilWaterAnalysisResponse(BaseModel):
    """Schema for soil-water analysis response"""
    id: str
    region: str
    soil_type: Optional[str]
    area_ha: float
    crop: str
    irrigation_method: Optional[str]
    results: Optional[Dict[str, Any]]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class SoilWaterAnalysisList(BaseModel):
    """Schema for list of analyses"""
    analyses: List[SoilWaterAnalysisResponse]
    total: int