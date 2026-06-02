"""
اتصال به PostgreSQL + PostGIS
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from datetime import datetime


# URL اتصال (از متغیر محیطی یا پیش‌فرض)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://econojin:econojin_secret_2026@localhost:5432/econojin"
)

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=10, max_overflow=20)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class FieldAnalysis(Base):
    """نتایج تحلیل هر منطقه/مزرعه"""
    __tablename__ = "field_analyses"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(16), index=True, nullable=False)
    region = Column(String(64), index=True, nullable=False)
    query = Column(Text, nullable=False)
    
    # نتایج کلیدی
    ndvi_avg = Column(Float, nullable=True)
    ndvi_health = Column(String(32), nullable=True)
    erosion_rate = Column(Float, nullable=True)  # تن/هکتار/سال
    erosion_severity = Column(String(32), nullable=True)
    predicted_yield = Column(Float, nullable=True)  # تن/هکتار
    irrigation_need = Column(Float, nullable=True)  # میلی‌متر
    rainfall_30d = Column(Float, nullable=True)
    
    # مکان
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    geom = Column(Geometry("POINT", srid=4326), nullable=True)
    
    # متادیتا
    quality_score = Column(Float, default=0.0)
    tools_used = Column(JSON, default=list)
    full_response = Column(Text, nullable=True)
    execution_time_ms = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MRVReport(Base):
    """گزارش‌های MRV برای ثبت روی بلاکچین"""
    __tablename__ = "mrv_reports"
    
    id = Column(Integer, primary_key=True)
    report_hash = Column(String(66), unique=True, index=True, nullable=False)  # 0x + 64
    analysis_id = Column(Integer, nullable=True)
    region = Column(String(64), index=True)
    indicators = Column(JSON)  # {ndvi, erosion, yield, ...}
    
    # بلاکچین
    chain = Column(String(32), default="polygon")  # polygon, ethereum, base
    tx_hash = Column(String(66), nullable=True)
    block_number = Column(Integer, nullable=True)
    is_registered = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FieldObservation(Base):
    """مشاهدات میدانی از KoboToolbox"""
    __tablename__ = "field_observations"
    
    id = Column(Integer, primary_key=True)
    kobo_submission_id = Column(String(64), unique=True, index=True)
    farmer_id = Column(String(64), index=True)
    region = Column(String(64), index=True)
    
    # موقعیت
    latitude = Column(Float)
    longitude = Column(Float)
    geom = Column(Geometry("POINT", srid=4326))
    
    # مشاهدات
    crop_type = Column(String(64))
    soil_condition = Column(String(64))
    pest_observed = Column(Integer, default=0)
    irrigation_method = Column(String(64))
    notes = Column(Text)
    photos = Column(JSON, default=list)  # لیست URL تصاویر
    
    submitted_at = Column(DateTime(timezone=True))
    synced_at = Column(DateTime(timezone=True), server_default=func.now())


async def init_db():
    """ساخت جداول"""
    async with engine.begin() as conn:
        # فعال‌سازی PostGIS
        await conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS postgis")
        await conn.run_sync(Base.metadata.create_all)
    print("✅ جداول با موفقیت ساخته شدند")


async def get_db() -> AsyncSession:
    """Dependency برای FastAPI"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())