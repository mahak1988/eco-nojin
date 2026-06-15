"""SQLAlchemy Database Models for Iot Domain"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Date
from sqlalchemy.sql import func
from datetime import datetime

try:
    from api.core.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class IotReadings(Base):
    """مدل پایگاه داده برای iot_readings"""
    __tablename__ = "iot_readings"

    id = Column(Integer, primary_key=True)
    sensor_id = Column(String(100), index=True, nullable=False)
    pilot_site = Column(String(50), index=True, nullable=False)
    sensor_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    quality = Column(String(20), default="good")
    reading_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<IotReadings(id={self.id})>"
