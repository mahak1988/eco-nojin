# api/modules/iot/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Index, JSON, Boolean
from sqlalchemy.sql import func
from api.core.database import Base


class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(Integer, primary_key=True, index=True)
    sensor_code = Column(String(50), unique=True, nullable=False, index=True)
    sensor_type = Column(String(50), nullable=False)
    location_name = Column(String(100))
    structure_id = Column(Integer, nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation_m = Column(Float)
    install_date = Column(DateTime, server_default=func.now())
    status = Column(String(20), default="active")
    battery_level = Column(Float, default=100.0)
    last_seen = Column(DateTime, server_default=func.now())
    metadata_json = Column(JSON, default=dict)


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True, index=True)
    sensor_code = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, server_default=func.now())
    value = Column(Float)
    value_secondary = Column(Float)
    unit = Column(String(20))
    quality_flag = Column(String(20), default="good")
    battery_level = Column(Float)
    signal_strength = Column(Integer)
    raw_payload = Column(JSON, default=dict)


class SensorAlert(Base):
    __tablename__ = "sensor_alerts"
    id = Column(Integer, primary_key=True, index=True)
    sensor_code = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, server_default=func.now())
    alert_type = Column(String(50))
    severity = Column(String(20))
    message = Column(String(500))
    value = Column(Float)
    threshold = Column(Float)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)


Index("idx_sensor_time", SensorReading.sensor_code, SensorReading.timestamp.desc())
