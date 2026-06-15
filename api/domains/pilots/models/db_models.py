"""SQLAlchemy Database Models for Pilots Domain"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Date
from sqlalchemy.sql import func
from datetime import datetime

try:
    from api.core.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class PilotSites(Base):
    """مدل پایگاه داده برای pilot_sites"""
    __tablename__ = "pilot_sites"

    id = Column(Integer, primary_key=True)
    pilot_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    country = Column(String(100), nullable=False)
    continent = Column(String(50), nullable=False)
    climate_zone = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    area_hectares = Column(Float, nullable=True)
    status = Column(String(50), default="registered")
    activated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PilotSites(id={self.id})>"
