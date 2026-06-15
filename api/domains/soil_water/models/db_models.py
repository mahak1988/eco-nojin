"""SQLAlchemy models for soil_water domain."""
from sqlalchemy import Column, Integer, String, Float, DateTime
from api.core.database import Base
from datetime import datetime


class SoilAnalysisDB(Base):
    __tablename__ = "soil_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    location_lat = Column(Float)
    location_lon = Column(Float)
    soil_type = Column(String)
    organic_matter_percent = Column(Float)
    moisture_content = Column(Float)
    ph_level = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


class ErosionRiskDB(Base):
    __tablename__ = "erosion_risks"
    
    id = Column(Integer, primary_key=True, index=True)
    location_lat = Column(Float)
    location_lon = Column(Float)
    risk_level = Column(String)
    rusle_value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
