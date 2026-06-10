#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 IoT Setup - Fully Automated
همه کارها را خودکار انجام می‌دهد - بدون نیاز به input
"""
import sys
import os
import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"
SCRIPTS_DIR = ROOT / "scripts"


def write_file(path: Path, content: str):
    """نوشتن فایل با بررسی"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    # بررسی اینکه واقعاً نوشته شده
    if path.exists() and path.stat().st_size > 0:
        print(f"   ✅ {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")
        return True
    else:
        print(f"   ❌ FAILED: {path.relative_to(ROOT)}")
        return False


# ============================================================================
# فایل 1: database.py
# ============================================================================
FILE_DATABASE = '''# api/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./econojin.db")
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    from api.modules.iot import models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized")
'''

# ============================================================================
# فایل 2: iot/__init__.py
# ============================================================================
FILE_IOT_INIT = '''# api/modules/iot/__init__.py
from . import models
from . import router
'''

# ============================================================================
# فایل 3: iot/models.py
# ============================================================================
FILE_IOT_MODELS = '''# api/modules/iot/models.py
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
'''

# ============================================================================
# فایل 4: iot/router.py
# ============================================================================
FILE_IOT_ROUTER = '''# api/modules/iot/router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel

from api.core.database import get_db
from api.modules.iot.models import Sensor, SensorReading, SensorAlert

router = APIRouter(prefix="/iot", tags=["IoT"])


class SensorResponse(BaseModel):
    sensor_code: str
    sensor_type: str
    location_name: str = None
    latitude: float = None
    longitude: float = None
    status: str
    battery_level: float = None
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
    result = await db.execute(select(Sensor).order_by(Sensor.sensor_code))
    return result.scalars().all()


@router.get("/sensors/{sensor_code}/latest")
async def get_latest(sensor_code: str, db: AsyncSession = Depends(get_db)):
    query = (
        select(SensorReading)
        .where(SensorReading.sensor_code == sensor_code)
        .order_by(desc(SensorReading.timestamp))
        .limit(1)
    )
    result = await db.execute(query)
    reading = result.scalar_one_or_none()
    if not reading:
        return {"sensor_code": sensor_code, "message": "No readings yet"}
    return {
        "sensor_code": reading.sensor_code,
        "timestamp": reading.timestamp,
        "value": reading.value,
        "unit": reading.unit,
        "quality": reading.quality_flag
    }


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
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
    battery: float = None,
    quality: str = "good",
    db: AsyncSession = Depends(get_db)
):
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
    return {"status": "ok", "sensor_code": sensor_code}
'''

# ============================================================================
# فایل 5: main.py
# ============================================================================
FILE_MAIN = '''# api/main.py
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


app = FastAPI(title="Econojin API", version="2.0.0", lifespan=lifespan)

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


# Register IoT router
app.include_router(iot_router, prefix="/api/v1")
print("✅ IoT router registered: /api/v1/iot")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
'''

# ============================================================================
# فایل 6: seed_sensors.py
# ============================================================================
FILE_SEED = '''# scripts/seed_sensors.py
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.core.database import engine, async_session, Base
from api.modules.iot.models import Sensor


SENSORS = [
    {"sensor_code": "TDR-001", "sensor_type": "tdr", "location_name": "حوضه کشف‌رود ۱", "latitude": 36.305, "longitude": 59.612, "elevation_m": 1050, "structure_id": 1, "status": "active", "battery_level": 95.0},
    {"sensor_code": "TDR-002", "sensor_type": "tdr", "location_name": "حوضه کشف‌رود ۲", "latitude": 36.308, "longitude": 59.615, "elevation_m": 1045, "structure_id": 1, "status": "active", "battery_level": 88.0},
    {"sensor_code": "TDR-003", "sensor_type": "tdr", "location_name": "دشت کویر", "latitude": 33.520, "longitude": 54.510, "elevation_m": 850, "structure_id": 2, "status": "active", "battery_level": 72.0},
    {"sensor_code": "FLUME-001", "sensor_type": "flume", "location_name": "کانال اصلی", "latitude": 36.310, "longitude": 59.620, "elevation_m": 1040, "structure_id": 3, "status": "active", "battery_level": 92.0},
    {"sensor_code": "FLUME-002", "sensor_type": "flume", "location_name": "کانال فرعی", "latitude": 36.312, "longitude": 59.625, "elevation_m": 1038, "structure_id": 3, "status": "active", "battery_level": 85.0},
    {"sensor_code": "RAIN-001", "sensor_type": "rain", "location_name": "ایستگاه هواشناسی", "latitude": 36.300, "longitude": 59.600, "elevation_m": 1060, "status": "active", "battery_level": 98.0},
    {"sensor_code": "PIEZ-001", "sensor_type": "piez", "location_name": "چاه پیزومتر ۱", "latitude": 36.315, "longitude": 59.630, "elevation_m": 1035, "structure_id": 4, "status": "active", "battery_level": 78.0},
    {"sensor_code": "PIEZ-002", "sensor_type": "piez", "location_name": "چاه پیزومتر ۲", "latitude": 36.318, "longitude": 59.635, "elevation_m": 1032, "structure_id": 4, "status": "active", "battery_level": 65.0},
    {"sensor_code": "WEATHER-001", "sensor_type": "weather", "location_name": "ایستگاه کامل", "latitude": 36.302, "longitude": 59.605, "elevation_m": 1058, "status": "active", "battery_level": 90.0},
]


async def seed():
    print("🌱 Seeding sensors...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")
    
    async with async_session() as session:
        for data in SENSORS:
            session.add(Sensor(**data))
        await session.commit()
        print(f"✅ Inserted {len(SENSORS)} sensors")
    
    await engine.dispose()
    print("✅ Done!")


if __name__ == "__main__":
    asyncio.run(seed())
'''


def main():
    print("🚀 IoT Setup - Fully Automated")
    print("=" * 70)
    
    # مرحله 0: بررسی ساختار
    print("\n📂 Checking structure...")
    if not API_DIR.exists():
        print(f"❌ API directory not found: {API_DIR}")
        return 1
    print(f"   ✅ API dir: {API_DIR}")
    
    # مرحله 1: حذف فایل‌های قدیمی
    print("\n🗑️  Cleaning old files...")
    old_files = [
        ROOT / "econojin.db",
        API_DIR / "services" / "mqtt_ingestion.py",
        API_DIR / "services" / "websocket_manager.py",
        API_DIR / "modules" / "iot" / "ws_router.py",
    ]
    for f in old_files:
        if f.exists():
            try:
                f.unlink()
                print(f"   🗑️  {f.relative_to(ROOT)}")
            except Exception as e:
                print(f"   ⚠️  Could not delete {f.name}: {e}")
    
    # مرحله 2: نوشتن همه فایل‌ها
    print("\n📝 Writing files...")
    files_to_write = [
        (API_DIR / "core" / "database.py", FILE_DATABASE),
        (API_DIR / "modules" / "iot" / "__init__.py", FILE_IOT_INIT),
        (API_DIR / "modules" / "iot" / "models.py", FILE_IOT_MODELS),
        (API_DIR / "modules" / "iot" / "router.py", FILE_IOT_ROUTER),
        (API_DIR / "main.py", FILE_MAIN),
        (SCRIPTS_DIR / "seed_sensors.py", FILE_SEED),
    ]
    
    success = True
    for path, content in files_to_write:
        if not write_file(path, content):
            success = False
    
    if not success:
        print("\n❌ Some files failed to write!")
        return 1
    
    # مرحله 3: تست import ها
    print("\n🧪 Testing imports...")
    try:
        sys.path.insert(0, str(ROOT))
        
        # پاک کردن cache
        for mod in list(sys.modules.keys()):
            if 'api.' in mod:
                del sys.modules[mod]
        
        from api.core.database import Base, engine
        from api.modules.iot.models import Sensor, SensorReading, SensorAlert
        from api.modules.iot.router import router
        from api.main import app
        
        # بررسی router ثبت شده
        routes = [r.path for r in app.routes]
        print(f"   ✅ Base: {Base}")
        print(f"   ✅ Models: Sensor, SensorReading, SensorAlert")
        print(f"   ✅ Router: {router.prefix}")
        print(f"   ✅ App routes: {len(routes)}")
        
        iot_routes = [r for r in routes if '/iot' in r]
        print(f"   ✅ IoT routes: {iot_routes}")
        
        if not iot_routes:
            print("   ❌ No IoT routes found!")
            return 1
            
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # مرحله 4: اجرای seed
    print("\n🌱 Running seed...")
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "seed_sensors.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"   ❌ Seed failed: {result.stderr}")
            return 1
    except Exception as e:
        print(f"   ❌ Seed error: {e}")
        return 1
    
    # مرحله 5: تست API
    print("\n🧪 Testing API...")
    print("   Starting server in background...")
    
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(4)
    
    try:
        import urllib.request
        import json
        
        endpoints = [
            ("http://127.0.0.1:8000/", "Root"),
            ("http://127.0.0.1:8000/api/v1/health", "Health"),
            ("http://127.0.0.1:8000/api/v1/iot/sensors", "Sensors"),
            ("http://127.0.0.1:8000/api/v1/iot/stats", "Stats"),
        ]
        
        all_ok = True
        for url, name in endpoints:
            try:
                with urllib.request.urlopen(url, timeout=5) as resp:
                    data = json.loads(resp.read().decode())
                    print(f"   ✅ {name}: {resp.status}")
                    if name == "Sensors":
                        print(f"      📊 Found {len(data)} sensors")
                    elif name == "Stats":
                        print(f"      📊 {data}")
            except Exception as e:
                print(f"   ❌ {name}: {e}")
                all_ok = False
        
        if all_ok:
            print("\n" + "=" * 70)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 70)
            print("\n🚀 Server is running on http://localhost:8000")
            print("\n📡 API Endpoints:")
            print("   • GET  /api/v1/iot/sensors")
            print("   • GET  /api/v1/iot/stats")
            print("   • GET  /api/v1/iot/sensors/{code}/latest")
            print("   • POST /api/v1/iot/ingest?sensor_code=X&value=Y")
            print("\n📚 Docs: http://localhost:8000/docs")
            print("=" * 70)
            print("\n💡 Press Ctrl+C to stop server")
            
            # نگه داشتن سرور در حال اجرا
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
        
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())