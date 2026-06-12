"""
Soil & Water Models - Comprehensive Version
Includes scientific models for water balance, erosion, and soil analysis
"""
from datetime import datetime, date
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
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
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
    
    farmer = relationship("Farmer", back_populates="soil_water_analyses")


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


# ============================================================================
# Soil Water Project Model
# ============================================================================
class SoilWaterProject(Base):
    """Project for organizing soil & water analyses"""
    __tablename__ = "soil_water_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=True)
    area_hectares = Column(Float, nullable=True)
    soil_type = Column(String(100), nullable=True)
    crop_type = Column(String(100), nullable=True)
    status = Column(String(50), default="active")  # active, archived, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    analyses = relationship("SoilWaterAnalysisReport", back_populates="project", cascade="all, delete-orphan")


# ============================================================================
# Soil Water Analysis Report Model
# ============================================================================
class SoilWaterAnalysisReport(Base):
    """Comprehensive analysis report"""
    __tablename__ = "soil_water_analysis_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("soil_water_projects.id"), nullable=True)
    title = Column(String(255), nullable=False)
    
    # Inputs (JSON)
    inputs = Column(JSON, nullable=True)
    
    # Results (JSON)
    results = Column(JSON, nullable=True)
    
    # Overall metrics
    overall_score = Column(Float, nullable=True)
    overall_health = Column(String(50), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("SoilWaterProject", back_populates="analyses")
