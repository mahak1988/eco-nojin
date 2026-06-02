"""Economugin ORM Models - Ready for PostgreSQL + PostGIS"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from geoalchemy2 import Geometry
from datetime import datetime
import os
from dotenv import load_dotenv
from scripts.core.logger import UnifiedLogger
logger = UnifiedLogger.get_logger(__name__)


load_dotenv()
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    national_id = Column(String(20), unique=True)
    phone = Column(String(20))
    role = Column(String(50), default="farmer")
    wallet_address = Column(String(42))
    created_at = Column(DateTime, default=datetime.utcnow)
    sensor_data = relationship("SensorData", back_populates="user")

class Subbasin(Base):
    __tablename__ = "subbasins"
    id = Column(Integer, primary_key=True)
    subbasin_code = Column(String(50), unique=True, nullable=False)
    area_ha = Column(DECIMAL(12,2))
    geometry = Column(Geometry("POLYGON", srid=4326))
    centroid = Column(Geometry("POINT", srid=4326))
    weather_data = relationship("WeatherData", back_populates="subbasin")

class WeatherData(Base):
    __tablename__ = "weather_data"
    id = Column(Integer, primary_key=True)
    subbasin_code = Column(String(50), ForeignKey("subbasins.subbasin_code"))
    date = Column(DateTime, nullable=False)
    precipitation_mm = Column(DECIMAL(8,2))
    temp_avg_c = Column(DECIMAL(5,2))
    et0_mm = Column(DECIMAL(8,2))
    source = Column(String(50), default="ERA5-Land")
    fetch_timestamp = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("subbasin_code", "date"),)
    subbasin = relationship("Subbasin", back_populates="weather_data")

class SoilProfile(Base):
    __tablename__ = "soil_profiles"
    id = Column(Integer, primary_key=True)
    profile_code = Column(String(50), unique=True)
    location = Column(Geometry("POINT", srid=4326))
    organic_carbon_pct = Column(DECIMAL(5,2))
    sampled_date = Column(DateTime)

class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(Integer, primary_key=True)
    sensor_code = Column(String(50), unique=True)
    location = Column(Geometry("POINT", srid=4326))
    sensor_type = Column(String(50))
    status = Column(String(20), default="active")
    readings = relationship("SensorData", back_populates="sensor")

class SensorData(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True)
    sensor_code = Column(String(50), ForeignKey("sensors.sensor_code"))
    timestamp = Column(DateTime, nullable=False)
    value = Column(DECIMAL(12,4))
    unit = Column(String(20))
    recorded_by = Column(Integer, ForeignKey("users.id"))
    __table_args__ = (UniqueConstraint("sensor_code", "timestamp"),)
    sensor = relationship("Sensor", back_populates="readings")
    user = relationship("User", back_populates="sensor_data")

def get_engine():
    db_url = f"postgresql://{os.getenv('DB_USER',
        'postgres')}:{os.getenv('DB_PASSWORD',
        '')}@{os.getenv('DB_HOST',
        'localhost')}:{os.getenv('DB_PORT',
        '5432')}/{os.getenv('DB_NAME',
        'economugin')}"
    return create_engine(db_url, echo=False)

def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine

def get_session():
    from sqlalchemy.orm import sessionmaker
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == "__main__":
    logger.info("✓ Models file ready. Run with real PostgreSQL when available.")
