#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Soil & Water Module Expansion
Expands the module with scientific models and standard indices
"""

from pathlib import Path
from datetime import datetime


def create_models():
    """Create comprehensive models.py"""
    content = '''"""
Soil & Water Models - Comprehensive Version
Includes scientific models for water balance, erosion, and soil analysis
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from api.core.database import Base


# ============================================================================
# Scenario Model
# ============================================================================
class Scenario(Base):
    """Scenario model for water analysis"""
    __tablename__ = "scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scenario_type = Column(String(100), nullable=True)
    parameters = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    water_balances = relationship("WaterBalance", back_populates="scenario")


# ============================================================================
# Water Balance Model
# ============================================================================
class WaterBalance(Base):
    """Water balance analysis model"""
    __tablename__ = "water_balance"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    date = Column(Date, nullable=False)
    precipitation = Column(Float, nullable=True)
    evaporation = Column(Float, nullable=True)
    runoff = Column(Float, nullable=True)
    infiltration = Column(Float, nullable=True)
    soil_moisture = Column(Float, nullable=True)
    groundwater_recharge = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    scenario = relationship("Scenario", back_populates="water_balances")


# ============================================================================
# Soil Water Analysis Model
# ============================================================================
class SoilWaterAnalysis(Base):
    """Soil water analysis model"""
    __tablename__ = "soil_water_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    location_id = Column(Integer, nullable=True)
    field_name = Column(String(255), nullable=True)
    soil_texture = Column(String(100), nullable=True)
    bulk_density = Column(Float, nullable=True)
    field_capacity = Column(Float, nullable=True)
    wilting_point = Column(Float, nullable=True)
    saturation_percentage = Column(Float, nullable=True)
    available_water_capacity = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============================================================================
# Irrigation Schedule Model
# ============================================================================
class IrrigationSchedule(Base):
    """Irrigation schedule based on soil water analysis"""
    __tablename__ = "irrigation_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    analysis_id = Column(Integer, ForeignKey("soil_water_analyses.id"), nullable=True)
    crop_type = Column(String(100), nullable=True)
    irrigation_method = Column(String(100), nullable=True)
    water_requirement_mm = Column(Float, nullable=True)
    irrigation_interval_days = Column(Integer, nullable=True)
    efficiency_percentage = Column(Float, nullable=True)
    recommended_date = Column(Date, nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============================================================================
# Drought Index Model
# ============================================================================
class DroughtIndex(Base):
    """Drought indices (SPI, SPEI, PDSI)"""
    __tablename__ = "drought_indices"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, nullable=True)
    date = Column(Date, nullable=False)
    spi_1month = Column(Float, nullable=True)
    spi_3month = Column(Float, nullable=True)
    spi_6month = Column(Float, nullable=True)
    spi_12month = Column(Float, nullable=True)
    spei_1month = Column(Float, nullable=True)
    spei_3month = Column(Float, nullable=True)
    spei_6month = Column(Float, nullable=True)
    spei_12month = Column(Float, nullable=True)
    pdsi = Column(Float, nullable=True)
    drought_category = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# Vegetation Index Model
# ============================================================================
class VegetationIndex(Base):
    """Vegetation indices (NDVI, NDWI, EVI)"""
    __tablename__ = "vegetation_indices"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, nullable=True)
    date = Column(Date, nullable=False)
    ndvi = Column(Float, nullable=True)
    ndwi = Column(Float, nullable=True)
    evi = Column(Float, nullable=True)
    savi = Column(Float, nullable=True)
    lai = Column(Float, nullable=True)
    fapar = Column(Float, nullable=True)
    vegetation_health = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# Soil Erosion Risk Model
# ============================================================================
class SoilErosionRisk(Base):
    """Soil erosion risk assessment (RUSLE model)"""
    __tablename__ = "soil_erosion_risks"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, nullable=True)
    date = Column(Date, nullable=False)
    r_factor = Column(Float, nullable=True)  # Rainfall erosivity
    k_factor = Column(Float, nullable=True)  # Soil erodibility
    ls_factor = Column(Float, nullable=True)  # Slope length & steepness
    c_factor = Column(Float, nullable=True)  # Cover management
    p_factor = Column(Float, nullable=True)  # Support practices
    soil_loss_tons_per_ha = Column(Float, nullable=True)
    erosion_risk_category = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# Carbon Sequestration Model
# ============================================================================
class CarbonSequestration(Base):
    """Carbon sequestration estimates"""
    __tablename__ = "carbon_sequestration"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, nullable=True)
    date = Column(Date, nullable=False)
    soil_organic_carbon_pct = Column(Float, nullable=True)
    carbon_stock_tons_per_ha = Column(Float, nullable=True)
    carbon_sequestration_rate = Column(Float, nullable=True)
    land_use_type = Column(String(100), nullable=True)
    management_practice = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
'''
    
    path = Path("api/modules/soil_water/models.py")
    path.write_text(content, encoding='utf-8')
    print(f"✅ Created: {path} ({len(content)} bytes)")


def create_schemas():
    """Create comprehensive schemas.py"""
    content = '''"""
Soil & Water Schemas - Comprehensive Version
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# Scenario Schemas
# ============================================================================
class ScenarioBase(BaseModel):
    name: str
    description: Optional[str] = None
    scenario_type: Optional[str] = None
    parameters: Optional[dict] = None


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioResponse(ScenarioBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Water Balance Schemas
# ============================================================================
class WaterBalanceBase(BaseModel):
    scenario_id: int
    date: date
    precipitation: Optional[float] = None
    evaporation: Optional[float] = None
    runoff: Optional[float] = None
    infiltration: Optional[float] = None
    soil_moisture: Optional[float] = None
    groundwater_recharge: Optional[float] = None


class WaterBalanceCreate(WaterBalanceBase):
    pass


class WaterBalanceResponse(WaterBalanceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Soil Water Analysis Schemas
# ============================================================================
class SoilWaterAnalysisBase(BaseModel):
    farmer_id: int
    location_id: Optional[int] = None
    field_name: Optional[str] = None
    soil_texture: Optional[str] = None
    bulk_density: Optional[float] = None
    field_capacity: Optional[float] = None
    wilting_point: Optional[float] = None
    saturation_percentage: Optional[float] = None
    available_water_capacity: Optional[float] = None


class SoilWaterAnalysisCreate(SoilWaterAnalysisBase):
    pass


class SoilWaterAnalysisResponse(SoilWaterAnalysisBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Irrigation Schedule Schemas
# ============================================================================
class IrrigationScheduleBase(BaseModel):
    farmer_id: int
    analysis_id: Optional[int] = None
    crop_type: Optional[str] = None
    irrigation_method: Optional[str] = None
    water_requirement_mm: Optional[float] = None
    irrigation_interval_days: Optional[int] = None
    efficiency_percentage: Optional[float] = None
    recommended_date: Optional[date] = None
    status: str = "pending"


class IrrigationScheduleCreate(IrrigationScheduleBase):
    pass


class IrrigationScheduleResponse(IrrigationScheduleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Drought Index Schemas
# ============================================================================
class DroughtIndexBase(BaseModel):
    location_id: Optional[int] = None
    date: date
    spi_1month: Optional[float] = None
    spi_3month: Optional[float] = None
    spi_6month: Optional[float] = None
    spi_12month: Optional[float] = None
    spei_1month: Optional[float] = None
    spei_3month: Optional[float] = None
    spei_6month: Optional[float] = None
    spei_12month: Optional[float] = None
    pdsi: Optional[float] = None
    drought_category: Optional[str] = None


class DroughtIndexCreate(DroughtIndexBase):
    pass


class DroughtIndexResponse(DroughtIndexBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Vegetation Index Schemas
# ============================================================================
class VegetationIndexBase(BaseModel):
    location_id: Optional[int] = None
    date: date
    ndvi: Optional[float] = None
    ndwi: Optional[float] = None
    evi: Optional[float] = None
    savi: Optional[float] = None
    lai: Optional[float] = None
    fapar: Optional[float] = None
    vegetation_health: Optional[str] = None


class VegetationIndexCreate(VegetationIndexBase):
    pass


class VegetationIndexResponse(VegetationIndexBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Soil Erosion Risk Schemas
# ============================================================================
class SoilErosionRiskBase(BaseModel):
    location_id: Optional[int] = None
    date: date
    r_factor: Optional[float] = None
    k_factor: Optional[float] = None
    ls_factor: Optional[float] = None
    c_factor: Optional[float] = None
    p_factor: Optional[float] = None
    soil_loss_tons_per_ha: Optional[float] = None
    erosion_risk_category: Optional[str] = None


class SoilErosionRiskCreate(SoilErosionRiskBase):
    pass


class SoilErosionRiskResponse(SoilErosionRiskBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Carbon Sequestration Schemas
# ============================================================================
class CarbonSequestrationBase(BaseModel):
    location_id: Optional[int] = None
    date: date
    soil_organic_carbon_pct: Optional[float] = None
    carbon_stock_tons_per_ha: Optional[float] = None
    carbon_sequestration_rate: Optional[float] = None
    land_use_type: Optional[str] = None
    management_practice: Optional[str] = None


class CarbonSequestrationCreate(CarbonSequestrationBase):
    pass


class CarbonSequestrationResponse(CarbonSequestrationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Scientific Calculation Schemas
# ============================================================================
class LDNCalculation(BaseModel):
    """Land Degradation Neutrality calculation"""
    soil_organic_carbon: float
    vegetation_cover: float
    erosion_risk: float


class WaterBalanceCalculation(BaseModel):
    """Water balance calculation inputs"""
    precipitation: float
    evapotranspiration: float
    runoff_coefficient: float = 0.3
    soil_moisture_initial: float = 50.0


class IrrigationRecommendation(BaseModel):
    """Irrigation recommendation output"""
    water_requirement_mm: float
    irrigation_interval_days: int
    efficiency_percentage: float
    recommended_date: date
    crop_type: str
    method: str
'''
    
    path = Path("api/modules/soil_water/schemas.py")
    path.write_text(content, encoding='utf-8')
    print(f"✅ Created: {path} ({len(content)} bytes)")


def create_service():
    """Create comprehensive service.py with scientific calculations"""
    content = '''"""
Soil & Water Service - Scientific Calculations
"""
from typing import Optional, Tuple, List
from datetime import datetime, date, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.soil_water.models import (
    SoilWaterAnalysis, WaterBalance, Scenario, IrrigationSchedule,
    DroughtIndex, VegetationIndex, SoilErosionRisk, CarbonSequestration
)
from api.modules.soil_water import schemas


# ============================================================================
# Soil Water Analysis Functions
# ============================================================================
async def list_analyses(
    db: AsyncSession,
    farmer_id: Optional[int] = None,
    limit: int = 10,
    offset: int = 0,
) -> Tuple[int, List[dict]]:
    """List soil water analyses"""
    query = select(SoilWaterAnalysis)
    
    if farmer_id:
        query = query.where(SoilWaterAnalysis.farmer_id == farmer_id)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    query = query.order_by(SoilWaterAnalysis.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    items_dict = []
    for item in items:
        items_dict.append({
            "id": item.id,
            "farmer_id": item.farmer_id,
            "location_id": item.location_id,
            "field_name": item.field_name,
            "soil_texture": item.soil_texture,
            "bulk_density": item.bulk_density,
            "field_capacity": item.field_capacity,
            "wilting_point": item.wilting_point,
            "saturation_percentage": item.saturation_percentage,
            "available_water_capacity": item.available_water_capacity,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        })
    
    return total, items_dict


async def create_analysis(
    db: AsyncSession,
    payload: schemas.SoilWaterAnalysisCreate,
) -> dict:
    """Create a new soil water analysis"""
    analysis = SoilWaterAnalysis(
        farmer_id=payload.farmer_id,
        location_id=payload.location_id,
        field_name=payload.field_name,
        soil_texture=payload.soil_texture,
        bulk_density=payload.bulk_density,
        field_capacity=payload.field_capacity,
        wilting_point=payload.wilting_point,
        saturation_percentage=payload.saturation_percentage,
        available_water_capacity=payload.available_water_capacity,
    )
    
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    
    return {
        "id": analysis.id,
        "farmer_id": analysis.farmer_id,
        "field_name": analysis.field_name,
        "soil_texture": analysis.soil_texture,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
    }


async def get_analysis(db: AsyncSession, analysis_id: int) -> Optional[dict]:
    """Get a specific analysis"""
    result = await db.execute(
        select(SoilWaterAnalysis).where(SoilWaterAnalysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        return None
    
    return {
        "id": analysis.id,
        "farmer_id": analysis.farmer_id,
        "field_name": analysis.field_name,
        "soil_texture": analysis.soil_texture,
        "bulk_density": analysis.bulk_density,
        "field_capacity": analysis.field_capacity,
        "wilting_point": analysis.wilting_point,
    }


# ============================================================================
# Scientific Calculations
# ============================================================================
def calculate_ldn(soil_organic_carbon: float, vegetation_cover: float, erosion_risk: float) -> dict:
    """
    Calculate Land Degradation Neutrality (LDN) index
    
    LDN = (SOC * 0.4) + (VC * 0.35) + ((100 - ER) * 0.25)
    
    Where:
    - SOC: Soil Organic Carbon (%)
    - VC: Vegetation Cover (%)
    - ER: Erosion Risk (%)
    """
    ldn_score = (
        (soil_organic_carbon * 0.4) +
        (vegetation_cover * 0.35) +
        ((100 - erosion_risk) * 0.25)
    )
    
    if ldn_score > 70:
        status = "healthy"
    elif ldn_score > 40:
        status = "degraded"
    else:
        status = "critical"
    
    return {
        "ldn_score": round(ldn_score, 2),
        "status": status,
        "soil_organic_carbon": soil_organic_carbon,
        "vegetation_cover": vegetation_cover,
        "erosion_risk": erosion_risk,
    }


def calculate_water_balance(
    precipitation: float,
    evapotranspiration: float,
    runoff_coefficient: float = 0.3,
    soil_moisture_initial: float = 50.0,
) -> dict:
    """
    Calculate water balance
    
    WB = P - ET - R - ΔS
    
    Where:
    - P: Precipitation (mm)
    - ET: Evapotranspiration (mm)
    - R: Runoff (mm)
    - ΔS: Change in soil moisture (mm)
    """
    runoff = precipitation * runoff_coefficient
    net_water = precipitation - evapotranspiration - runoff
    soil_moisture_final = max(0, soil_moisture_initial + net_water)
    soil_moisture_change = soil_moisture_final - soil_moisture_initial
    
    return {
        "precipitation": precipitation,
        "evapotranspiration": evapotranspiration,
        "runoff": round(runoff, 2),
        "net_water": round(net_water, 2),
        "soil_moisture_initial": soil_moisture_initial,
        "soil_moisture_final": round(soil_moisture_final, 2),
        "soil_moisture_change": round(soil_moisture_change, 2),
        "water_surplus": net_water > 0,
    }


def calculate_ndvi(nir: float, red: float) -> float:
    """
    Calculate Normalized Difference Vegetation Index (NDVI)
    
    NDVI = (NIR - Red) / (NIR + Red)
    
    Range: -1 to 1
    - Negative: Water, clouds, snow
    - 0 to 0.2: Bare soil
    - 0.2 to 0.4: Sparse vegetation
    - 0.4 to 0.6: Moderate vegetation
    - 0.6 to 1.0: Dense vegetation
    """
    if (nir + red) == 0:
        return 0.0
    
    ndvi = (nir - red) / (nir + red)
    return round(ndvi, 4)


def calculate_ndwi(green: float, nir: float) -> float:
    """
    Calculate Normalized Difference Water Index (NDWI)
    
    NDWI = (Green - NIR) / (Green + NIR)
    
    Range: -1 to 1
    - Positive: Water bodies
    - Negative: Vegetation, soil
    """
    if (green + nir) == 0:
        return 0.0
    
    ndwi = (green - nir) / (green + nir)
    return round(ndwi, 4)


def calculate_rusle(
    r_factor: float,
    k_factor: float,
    ls_factor: float,
    c_factor: float,
    p_factor: float,
) -> dict:
    """
    Calculate Revised Universal Soil Loss Equation (RUSLE)
    
    A = R * K * LS * C * P
    
    Where:
    - A: Soil loss (tons/ha/year)
    - R: Rainfall erosivity factor
    - K: Soil erodibility factor
    - LS: Slope length & steepness factor
    - C: Cover management factor
    - P: Support practices factor
    """
    soil_loss = r_factor * k_factor * ls_factor * c_factor * p_factor
    
    if soil_loss < 5:
        category = "low"
    elif soil_loss < 15:
        category = "moderate"
    elif soil_loss < 30:
        category = "high"
    else:
        category = "very_high"
    
    return {
        "soil_loss_tons_per_ha": round(soil_loss, 2),
        "erosion_risk_category": category,
        "r_factor": r_factor,
        "k_factor": k_factor,
        "ls_factor": ls_factor,
        "c_factor": c_factor,
        "p_factor": p_factor,
    }


def calculate_irrigation_requirement(
    crop_type: str,
    field_capacity: float,
    wilting_point: float,
    current_moisture: float,
    et_crop: float,
    efficiency: float = 0.7,
) -> dict:
    """
    Calculate irrigation water requirement
    
    IR = (FC - WP) * (1 - (θ/FC)) * Z / Ea
    
    Where:
    - FC: Field capacity (%)
    - WP: Wilting point (%)
    - θ: Current soil moisture (%)
    - Z: Root zone depth (mm)
    - Ea: Application efficiency
    """
    available_water = field_capacity - wilting_point
    depletion = field_capacity - current_moisture
    depletion_fraction = depletion / available_water if available_water > 0 else 0
    
    root_zone_depth = 500  # mm (default)
    water_requirement = (depletion * root_zone_depth) / efficiency
    
    irrigation_interval = water_requirement / et_crop if et_crop > 0 else 7
    
    return {
        "water_requirement_mm": round(water_requirement, 2),
        "irrigation_interval_days": max(1, int(irrigation_interval)),
        "efficiency_percentage": efficiency * 100,
        "depletion_fraction": round(depletion_fraction, 2),
        "crop_type": crop_type,
        "recommended_date": (date.today() + timedelta(days=1)).isoformat(),
    }


def classify_drought(spi: float) -> str:
    """
    Classify drought based on Standardized Precipitation Index (SPI)
    
    SPI Categories:
    - ≥ 2.0: Extremely wet
    - 1.5 to 1.99: Very wet
    - 1.0 to 1.49: Moderately wet
    - -0.99 to 0.99: Near normal
    - -1.0 to -1.49: Moderately dry
    - -1.5 to -1.99: Severely dry
    - ≤ -2.0: Extremely dry
    """
    if spi >= 2.0:
        return "extremely_wet"
    elif spi >= 1.5:
        return "very_wet"
    elif spi >= 1.0:
        return "moderately_wet"
    elif spi >= -0.99:
        return "near_normal"
    elif spi >= -1.49:
        return "moderately_dry"
    elif spi >= -1.99:
        return "severely_dry"
    else:
        return "extremely_dry"


def calculate_carbon_sequestration(
    soil_organic_carbon_pct: float,
    bulk_density: float,
    depth_cm: float = 30,
) -> dict:
    """
    Calculate carbon stock in soil
    
    Carbon Stock (tons/ha) = SOC% * BD * Depth * 10
    
    Where:
    - SOC: Soil organic carbon (%)
    - BD: Bulk density (g/cm³)
    - Depth: Soil depth (cm)
    """
    carbon_stock = soil_organic_carbon_pct * bulk_density * depth_cm * 10
    
    return {
        "carbon_stock_tons_per_ha": round(carbon_stock, 2),
        "soil_organic_carbon_pct": soil_organic_carbon_pct,
        "bulk_density": bulk_density,
        "depth_cm": depth_cm,
    }
'''
    
    path = Path("api/modules/soil_water/service.py")
    path.write_text(content, encoding='utf-8')
    print(f"✅ Created: {path} ({len(content)} bytes)")


def create_router():
    """Create comprehensive router.py"""
    content = '''"""
Soil & Water Router - Comprehensive Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from api.core.database import get_db
from api.modules.soil_water import service as soil_service
from api.modules.soil_water import schemas

router = APIRouter(prefix="/soil-water", tags=["Soil & Water"])


# ============================================================================
# Soil Water Analysis Endpoints
# ============================================================================
@router.get("/recent-analyses")
async def recent_soil_water_analyses(
    limit: int = Query(10, ge=1, le=100),
    farmer_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get recent soil water analyses"""
    try:
        total, items = await soil_service.list_analyses(
            db=db,
            farmer_id=farmer_id,
            limit=limit,
        )
        return {"total": total, "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyses", response_model=schemas.SoilWaterAnalysisResponse)
async def create_soil_water_analysis(
    payload: schemas.SoilWaterAnalysisCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new soil water analysis"""
    try:
        result = await soil_service.create_analysis(db, payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyses/{analysis_id}")
async def get_soil_water_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific analysis"""
    try:
        result = await soil_service.get_analysis(db, analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Scientific Calculation Endpoints
# ============================================================================
@router.get("/ldn")
async def calculate_ldn(
    soil_organic_carbon: float = Query(..., description="Soil Organic Carbon (%)"),
    vegetation_cover: float = Query(..., description="Vegetation Cover (%)"),
    erosion_risk: float = Query(..., description="Erosion Risk (%)"),
):
    """Calculate Land Degradation Neutrality (LDN) index"""
    try:
        result = soil_service.calculate_ldn(
            soil_organic_carbon=soil_organic_carbon,
            vegetation_cover=vegetation_cover,
            erosion_risk=erosion_risk,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/water-balance")
async def calculate_water_balance(
    payload: schemas.WaterBalanceCalculation,
):
    """Calculate water balance"""
    try:
        result = soil_service.calculate_water_balance(
            precipitation=payload.precipitation,
            evapotranspiration=payload.evapotranspiration,
            runoff_coefficient=payload.runoff_coefficient,
            soil_moisture_initial=payload.soil_moisture_initial,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ndvi")
async def calculate_ndvi_endpoint(
    nir: float = Query(..., description="Near Infrared reflectance"),
    red: float = Query(..., description="Red reflectance"),
):
    """Calculate NDVI (Normalized Difference Vegetation Index)"""
    try:
        ndvi = soil_service.calculate_ndvi(nir=nir, red=red)
        
        if ndvi < 0:
            health = "non_vegetation"
        elif ndvi < 0.2:
            health = "bare_soil"
        elif ndvi < 0.4:
            health = "sparse_vegetation"
        elif ndvi < 0.6:
            health = "moderate_vegetation"
        else:
            health = "dense_vegetation"
        
        return {
            "ndvi": ndvi,
            "vegetation_health": health,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ndwi")
async def calculate_ndwi_endpoint(
    green: float = Query(..., description="Green reflectance"),
    nir: float = Query(..., description="Near Infrared reflectance"),
):
    """Calculate NDWI (Normalized Difference Water Index)"""
    try:
        ndwi = soil_service.calculate_ndwi(green=green, nir=nir)
        
        if ndwi > 0:
            water_presence = True
        else:
            water_presence = False
        
        return {
            "ndwi": ndwi,
            "water_presence": water_presence,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rusle")
async def calculate_rusle(
    r_factor: float = Query(..., description="Rainfall erosivity factor"),
    k_factor: float = Query(..., description="Soil erodibility factor"),
    ls_factor: float = Query(..., description="Slope length & steepness factor"),
    c_factor: float = Query(..., description="Cover management factor"),
    p_factor: float = Query(..., description="Support practices factor"),
):
    """Calculate RUSLE (Revised Universal Soil Loss Equation)"""
    try:
        result = soil_service.calculate_rusle(
            r_factor=r_factor,
            k_factor=k_factor,
            ls_factor=ls_factor,
            c_factor=c_factor,
            p_factor=p_factor,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/irrigation")
async def calculate_irrigation(
    crop_type: str = Query(..., description="Crop type"),
    field_capacity: float = Query(..., description="Field capacity (%)"),
    wilting_point: float = Query(..., description="Wilting point (%)"),
    current_moisture: float = Query(..., description="Current soil moisture (%)"),
    et_crop: float = Query(..., description="Crop evapotranspiration (mm/day)"),
    efficiency: float = Query(0.7, description="Irrigation efficiency"),
):
    """Calculate irrigation water requirement"""
    try:
        result = soil_service.calculate_irrigation_requirement(
            crop_type=crop_type,
            field_capacity=field_capacity,
            wilting_point=wilting_point,
            current_moisture=current_moisture,
            et_crop=et_crop,
            efficiency=efficiency,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drought-classification")
async def classify_drought_endpoint(
    spi: float = Query(..., description="Standardized Precipitation Index"),
):
    """Classify drought based on SPI"""
    try:
        category = soil_service.classify_drought(spi=spi)
        return {
            "spi": spi,
            "drought_category": category,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/carbon-sequestration")
async def calculate_carbon_sequestration(
    soil_organic_carbon_pct: float = Query(..., description="Soil organic carbon (%)"),
    bulk_density: float = Query(..., description="Bulk density (g/cm³)"),
    depth_cm: float = Query(30, description="Soil depth (cm)"),
):
    """Calculate carbon sequestration"""
    try:
        result = soil_service.calculate_carbon_sequestration(
            soil_organic_carbon_pct=soil_organic_carbon_pct,
            bulk_density=bulk_density,
            depth_cm=depth_cm,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
    
    path = Path("api/modules/soil_water/router.py")
    path.write_text(content, encoding='utf-8')
    print(f"✅ Created: {path} ({len(content)} bytes)")


def delete_database():
    """Delete database"""
    for db in [Path("econojin.db"), Path("api/econojin.db")]:
        if db.exists():
            try:
                db.unlink()
                print(f"🗑️ Deleted: {db}")
            except Exception as e:
                print(f"⚠️ Cannot delete {db}: {e}")


def main():
    print("=" * 70)
    print("🌊 Comprehensive Soil & Water Module Expansion")
    print("=" * 70)
    print()
    
    try:
        create_models()
        create_schemas()
        create_service()
        create_router()
        delete_database()
        
        print("\n" + "=" * 70)
        print("✅ All files created successfully!")
        print("=" * 70)
        print("\n📊 Scientific Models Implemented:")
        print("  ✅ LDN (Land Degradation Neutrality)")
        print("  ✅ Water Balance Calculation")
        print("  ✅ NDVI (Normalized Difference Vegetation Index)")
        print("  ✅ NDWI (Normalized Difference Water Index)")
        print("  ✅ RUSLE (Revised Universal Soil Loss Equation)")
        print("  ✅ Irrigation Water Requirement")
        print("  ✅ Drought Classification (SPI)")
        print("  ✅ Carbon Sequestration")
        print("\n📋 Next steps:")
        print("  1. Stop backend server (Ctrl+C)")
        print("  2. Remove-Item 'econojin.db' -Force")
        print("  3. uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print("  4. Visit: http://localhost:8000/docs")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()