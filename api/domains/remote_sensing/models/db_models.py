"""SQLAlchemy Database Models for Remote_sensing Domain"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Date
from sqlalchemy.sql import func
from datetime import datetime

try:
    from api.core.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class SatelliteImages(Base):
    """مدل پایگاه داده برای satellite_images"""
    __tablename__ = "satellite_images"

    id = Column(Integer, primary_key=True)
    image_id = Column(String(100), unique=True, nullable=False)
    satellite = Column(String(50), nullable=False)
    pilot_site = Column(String(50), index=True, nullable=False)
    acquisition_date = Column(Date, nullable=False)
    cloud_cover = Column(Float, nullable=True)
    ndvi_mean = Column(Float, nullable=True)
    ndwi_mean = Column(Float, nullable=True)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SatelliteImages(id={self.id})>"
