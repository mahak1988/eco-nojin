#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 IoT Integration - Complete Fix
تشخیص و رفع خودکار تمام مشکلات
"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"
SCRIPTS_DIR = ROOT / "scripts"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)}")


def delete_db():
    """حذف دیتابیس قدیمی"""
    db_path = ROOT / "econojin.db"
    if db_path.exists():
        db_path.unlink()
        print("   🗑️ econojin.db deleted")


# ========== فایل 1: database.py ==========
def create_database():
    print("\n[1/6] Creating database.py...")
    content = '''# api/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./econojin.db")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# IMPORTANT: Single Base for all models
Base = declarative_base()


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables"""
    # Import all models to register them in Base.metadata
    from api.modules.iot import models  # noqa
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created")
'''
    write_file(API_DIR / "core" / "database.py", content)


# ========== فایل 2: iot/__init__.py ==========
def create_iot_init():
    print("\n[2/6] Creating iot/__init__.py...")
    content = '''# api/modules/iot/__init__.py
from . import models
from . import router
'''
    write_file(API_DIR / "modules" / "iot" / "__init__.py", content)


# ========== فایل 3: iot/models.py ==========
def create_models():
    print("\n[3/6] Creating iot/models.py...")
    content = '''# api/modules/iot/models.py
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


# Indexes
Index("idx_sensor_time", SensorReading.sensor_code, SensorReading.timestamp.desc())
'''
    write_file(API_DIR / "modules" / "iot" / "models.py", content)


# ========== فایل 4: iot/router.py ==========
def create_router():
    print("\n[4/6] Creating iot/router.py...")
    content = '''# api/modules/iot/router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

from api.core.database import get_db
from api.modules.iot.models import Sensor, SensorReading, SensorAlert

router = APIRouter(prefix="/iot", tags=["IoT"])


class SensorResponse(BaseModel):
    sensor_code: str
    sensor_type: str
    location_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    status: str
    battery_level: Optional[float]
    
    class Config:
        from_attributes = True


class ReadingResponse(BaseModel):
    sensor_code: str
    timestamp: datetime
    value: Optional[float]
    unit: Optional[str]
    quality_flag: str
    
    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total_sensors: int
    active_sensors: int
    total_readings_24h: int
    alerts_today: int
    avg_battery: float


@router.get("/sensors", response_model=List[SensorResponse])
async def get_sensors(db: AsyncSession = Depends(get_db)):
    """Get all sensors"""
    result = await db.execute(select(Sensor).order_by(Sensor.sensor_code))
    return result.scalars().all()


@router.get("/sensors/{sensor_code}/readings", response_model=List[ReadingResponse])
async def get_readings(
    sensor_code: str,
    hours: int = Query(default=24, ge=1, le=720),
    limit: int = Query(default=100, ge=1, le=10000),
    db: AsyncSession = Depends(get_db)
):
    """Get sensor readings"""
    since = datetime.utcnow() - timedelta(hours=hours)
    query = (
        select(SensorReading)
        .where(and_(
            SensorReading.sensor_code == sensor_code,
            SensorReading.timestamp >= since
        ))
        .order_by(desc(SensorReading.timestamp))
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/sensors/{sensor_code}/latest")
async def get_latest(sensor_code: str, db: AsyncSession = Depends(get_db)):
    """Get latest reading"""
    query = (
        select(SensorReading)
        .where(SensorReading.sensor_code == sensor_code)
        .order_by(desc(SensorReading.timestamp))
        .limit(1)
    )
    result = await db.execute(query)
    reading = result.scalar_one_or_none()
    
    if not reading:
        raise HTTPException(status_code=404, detail="No readings found")
    
    return {
        "sensor_code": reading.sensor_code,
        "timestamp": reading.timestamp,
        "value": reading.value,
        "unit": reading.unit,
        "quality": reading.quality_flag
    }


@router.get("/alerts")
async def get_alerts(
    hours: int = Query(default=24, ge=1, le=720),
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get alerts"""
    since = datetime.utcnow() - timedelta(hours=hours)
    query = (
        select(SensorAlert)
        .where(SensorAlert.timestamp >= since)
        .order_by(desc(SensorAlert.timestamp))
        .limit(limit)
    )
    result = await db.execute(query)
    alerts = result.scalars().all()
    return [
        {
            "id": a.id,
            "sensor_code": a.sensor_code,
            "timestamp": a.timestamp,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "message": a.message,
            "acknowledged": a.acknowledged
        }
        for a in alerts
    ]


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get IoT statistics"""
    total = (await db.execute(select(func.count(Sensor.id)))).scalar() or 0
    active = (await db.execute(
        select(func.count(Sensor.id)).where(Sensor.status == "active")
    )).scalar() or 0
    
    since_24h = datetime.utcnow() - timedelta(hours=24)
    readings = (await db.execute(
        select(func.count(SensorReading.id)).where(SensorReading.timestamp >= since_24h)
    )).scalar() or 0
    
    since_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    alerts = (await db.execute(
        select(func.count(SensorAlert.id)).where(SensorAlert.timestamp >= since_today)
    )).scalar() or 0
    
    avg_bat = (await db.execute(
        select(func.avg(Sensor.battery_level)).where(Sensor.status == "active")
    )).scalar() or 0
    
    return StatsResponse(
        total_sensors=total,
        active_sensors=active,
        total_readings_24h=readings,
        alerts_today=alerts,
        avg_battery=round(avg_bat, 1)
    )


@router.post("/ingest")
async def ingest(
    sensor_code: str,
    value: float,
    unit: str = "",
    battery: Optional[float] = None,
    quality: str = "good",
    db: AsyncSession = Depends(get_db)
):
    """Ingest sensor reading"""
    reading = SensorReading(
        sensor_code=sensor_code,
        timestamp=datetime.utcnow(),
        value=value,
        unit=unit,
        quality_flag=quality,
        battery_level=battery
    )
    db.add(reading)
    await db.commit()
    return {"status": "ok"}
'''
    write_file(API_DIR / "modules" / "iot" / "router.py", content)


# ========== فایل 5: main.py ==========
def create_main():
    print("\n[5/6] Creating main.py...")
    content = '''# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.core.database import init_db
from api.modules.iot.router import router as iot_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Econojin v2.0.0...")
    await init_db()
    print("Ready on http://127.0.0.1:8000")
    yield


app = FastAPI(
    title="Econojin API",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"name": "Econojin API", "version": "2.0.0", "status": "running"}


@app.get("/api/v1/health")
async def health():
    return {"status": "healthy"}


# Register routers
app.include_router(iot_router, prefix="/api/v1")

print("✅ IoT router registered at /api/v1/iot")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
'''
    write_file(API_DIR / "main.py", content)


# ========== فایل 6: seed_sensors.py ==========
def create_seed():
    print("\n[6/6] Creating seed_sensors.py...")
    content = '''# scripts/seed_sensors.py
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.core.database import engine, async_session, Base
from api.modules.iot.models import Sensor, SensorReading, SensorAlert


SENSORS = [
    {"sensor_code": "TDR-001", "sensor_type": "tdr", "location_name": "حوضه کشف‌رود - ایستگاه ۱", "latitude": 36.305, "longitude": 59.612, "elevation_m": 1050, "structure_id": 1, "status": "active", "battery_level": 95.0},
    {"sensor_code": "TDR-002", "sensor_type": "tdr", "location_name": "حوضه کشف‌رود - ایستگاه ۲", "latitude": 36.308, "longitude": 59.615, "elevation_m": 1045, "structure_id": 1, "status": "active", "battery_level": 88.0},
    {"sensor_code": "TDR-003", "sensor_type": "tdr", "location_name": "دشت کویر - زون A", "latitude": 33.520, "longitude": 54.510, "elevation_m": 850, "structure_id": 2, "status": "active", "battery_level": 72.0},
    {"sensor_code": "FLUME-001", "sensor_type": "flume", "location_name": "کانال اصلی", "latitude": 36.310, "longitude": 59.620, "elevation_m": 1040, "structure_id": 3, "status": "active", "battery_level": 92.0},
    {"sensor_code": "FLUME-002", "sensor_type": "flume", "location_name": "کانال فرعی", "latitude": 36.312, "longitude": 59.625, "elevation_m": 1038, "structure_id": 3, "status": "active", "battery_level": 85.0},
    {"sensor_code": "RAIN-001", "sensor_type": "rain", "location_name": "ایستگاه هواشناسی", "latitude": 36.300, "longitude": 59.600, "elevation_m": 1060, "status": "active", "battery_level": 98.0},
    {"sensor_code": "PIEZ-001", "sensor_type": "piez", "location_name": "چاه پیزومتر ۱", "latitude": 36.315, "longitude": 59.630, "elevation_m": 1035, "structure_id": 4, "status": "active", "battery_level": 78.0},
    {"sensor_code": "PIEZ-002", "sensor_type": "piez", "location_name": "چاه پیزومتر ۲", "latitude": 36.318, "longitude": 59.635, "elevation_m": 1032, "structure_id": 4, "status": "active", "battery_level": 65.0},
    {"sensor_code": "WEATHER-001", "sensor_type": "weather", "location_name": "ایستگاه هواشناسی کامل", "latitude": 36.302, "longitude": 59.605, "elevation_m": 1058, "status": "active", "battery_level": 90.0},
]


async def seed():
    print("🌱 Seeding sensors...")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")
    
    # Insert sensors
    async with async_session() as session:
        for data in SENSORS:
            sensor = Sensor(**data)
            session.add(sensor)
        await session.commit()
        print(f"✅ Inserted {len(SENSORS)} sensors")
    
    await engine.dispose()
    print("✅ Done!")


if __name__ == "__main__":
    asyncio.run(seed())
'''
    write_file(SCRIPTS_DIR / "seed_sensors.py", content)


# ========== Test Function ==========
def test_api():
    """تست API"""
    print("\n" + "=" * 70)
    print("🧪 Testing API...")
    print("=" * 70)
    
    import subprocess
    import time
    import requests
    
    # Start server in background
    print("\n🚀 Starting server...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test endpoints
        print("\n📡 Testing endpoints...")
        
        # 1. Root
        try:
            r = requests.get("http://127.0.0.1:8000/", timeout=5)
            print(f"   {'✅' if r.status_code == 200 else '❌'} GET / → {r.status_code}")
        except Exception as e:
            print(f"   ❌ GET / → {e}")
        
        # 2. Sensors
        try:
            r = requests.get("http://127.0.0.1:8000/api/v1/iot/sensors", timeout=5)
            print(f"   {'✅' if r.status_code == 200 else '❌'} GET /api/v1/iot/sensors → {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"      📊 Found {len(data)} sensors")
        except Exception as e:
            print(f"   ❌ GET /api/v1/iot/sensors → {e}")
        
        # 3. Stats
        try:
            r = requests.get("http://127.0.0.1:8000/api/v1/iot/stats", timeout=5)
            print(f"   {'✅' if r.status_code == 200 else '❌'} GET /api/v1/iot/stats → {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"      📊 Stats: {data}")
        except Exception as e:
            print(f"   ❌ GET /api/v1/iot/stats → {e}")
        
        # 4. Latest reading
        try:
            r = requests.get("http://127.0.0.1:8000/api/v1/iot/sensors/TDR-001/latest", timeout=5)
            print(f"   {'✅' if r.status_code in [200, 404] else '❌'} GET /api/v1/iot/sensors/TDR-001/latest → {r.status_code}")
        except Exception as e:
            print(f"   ❌ GET latest → {e}")
        
        print("\n" + "=" * 70)
        print("✅ API Test Complete!")
        print("=" * 70)
        
    finally:
        # Stop server
        print("\n🛑 Stopping test server...")
        proc.terminate()
        proc.wait()


# ========== Main ==========
def main():
    print("🔧 IoT Integration - Complete Fix")
    print("=" * 70)
    
    # Delete old database
    print("\n🗑️  Cleaning up...")
    delete_db()
    
    # Create all files
    create_database()
    create_iot_init()
    create_models()
    create_router()
    create_main()
    create_seed()
    
    print("\n" + "=" * 70)
    print("✅ All files created successfully!")
    print("\n🚀 Next steps:")
    print("   1. Run seed:")
    print("      python scripts/seed_sensors.py")
    print("")
    print("   2. Start server:")
    print("      uvicorn api.main:app --reload --port 8000")
    print("")
    print("   3. Test API (in another terminal):")
    print('      Invoke-RestMethod "http://localhost:8000/api/v1/iot/sensors"')
    print('      Invoke-RestMethod "http://localhost:8000/api/v1/iot/stats"')
    print("=" * 70)
    
    # Ask to run test
    response = input("\n🧪 Run automated test? (y/n): ").strip().lower()
    if response == 'y':
        test_api()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())