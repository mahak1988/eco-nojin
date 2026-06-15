"""SQLAlchemy models for drought domain."""
from sqlalchemy import Column, Integer, String, Float, DateTime
from api.core.database import Base
from datetime import datetime


class DroughtIndexDB(Base):
    __tablename__ = "drought_indices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    location_lat = Column(Float)
    location_lon = Column(Float)
    severity = Column(String)


class SPEIValueDB(Base):
    __tablename__ = "spei_values"
    
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String, index=True)
    date = Column(DateTime)
    value = Column(Float)
    scale_months = Column(Integer)
