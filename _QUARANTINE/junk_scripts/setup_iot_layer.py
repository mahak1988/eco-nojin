#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 راه‌اندازی لایه ۲ IoT - Real-time Ingestion
- مدل‌های دیتابیس سری زمانی
- سرویس MQTT Ingestion
- شبیه‌ساز سنسور برای تست
- WebSocket برای داشبورد Real-time
- REST API برای کوئری داده‌ها
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)}")


# ========== 1. مدل‌های دیتابیس IoT ==========
def create_iot_models():
    print("\n📊 ایجاد مدل‌های دیتابیس IoT...")
    
    content = '''# api/modules/iot/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Index, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Sensor(Base):
    """تعریف سنسورهای نصب‌شده در حوضه‌های آبریز"""
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_code = Column(String(50), unique=True, nullable=False, index=True)
    sensor_type = Column(String(50), nullable=False)  # tdr, flume, rain_gauge, piezometer, weather
    location_name = Column(String(100))
    structure_id = Column(Integer, nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation_m = Column(Float)
    install_date = Column(DateTime, server_default=func.now())
    status = Column(String(20), default="active")  # active, maintenance, offline
    battery_level = Column(Float, default=100.0)
    last_seen = Column(DateTime, server_default=func.now(), onupdate=func.now())
    metadata_json = Column(JSON, default=dict)


class SensorReading(Base):
    """داده‌های خوانده‌شده از سنسورها (Time-Series)"""
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_code = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, server_default=func.now())
    
    # مقادیر اصلی
    value = Column(Float)  # مقدار اصلی
    value_secondary = Column(Float)  # مقدار ثانویه (مثلاً دما برای TDR)
    unit = Column(String(20))  # mm, m3/s, %, °C, m
    
    # کیفیت داده
    quality_flag = Column(String(20), default="good")  # good, suspicious, bad, missing
    battery_level = Column(Float)
    signal_strength = Column(Integer)  # RSSI
    
    # داده خام
    raw_payload = Column(JSON, default=dict)


class SensorAlert(Base):
    """هشدارهای تولیدشده از داده‌های سنسور"""
    __tablename__ = "sensor_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_code = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, server_default=func.now())
    alert_type = Column(String(50))  # low_battery, threshold_exceeded, sensor_offline, anomaly
    severity = Column(String(20))  # info, warning, critical
    message = Column(String(500))
    value = Column(Float)
    threshold = Column(Float)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)


# ایندکس‌های بهینه برای کوئری‌های سری زمانی
Index("idx_sensor_time", SensorReading.sensor_code, SensorReading.timestamp.desc())
Index("idx_time_sensor", SensorReading.timestamp.desc(), SensorReading.sensor_code)
Index("idx_alert_time", SensorAlert.timestamp.desc())
'''
    
    write_file(API_DIR / "modules" / "iot" / "models.py", content)


# ========== 2. سرویس MQTT Ingestion ==========
def create_mqtt_service():
    print("\n🔌 ایجاد سرویس MQTT Ingestion...")
    
    content = '''# api/services/mqtt_ingestion.py
import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import async_session
from api.modules.iot.models import SensorReading, Sensor, SensorAlert

logger = logging.getLogger(__name__)

# تنظیمات MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "econojin/sensors/#")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")


class MQTTIngestionService:
    """سرویس دریافت و پردازش داده‌های MQTT"""
    
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.error_count = 0
        self.last_message_time = None
        self._ws_clients: List[Any] = []  # WebSocket clients
    
    async def start(self):
        """شروع گوش‌دادن به MQTT Broker"""
        self.running = True
        logger.info(f"🚀 Starting MQTT Ingestion on {MQTT_BROKER}:{MQTT_PORT}")
        
        try:
            import aiomqtt
            
            while self.running:
                try:
                    async with aiomqtt.Client(
                        MQTT_BROKER,
                        port=MQTT_PORT,
                        username=MQTT_USERNAME or None,
                        password=MQTT_PASSWORD or None,
                    ) as client:
                        await client.subscribe(MQTT_TOPIC, qos=1)
                        logger.info(f"✅ Subscribed to {MQTT_TOPIC}")
                        
                        async for message in client.messages:
                            await self._process_message(message)
                            
                except Exception as e:
                    logger.error(f"❌ MQTT Error: {e}. Reconnecting in 5s...")
                    await asyncio.sleep(5)
                    
        except ImportError:
            logger.error("❌ aiomqtt not installed. Run: pip install aiomqtt")
            logger.info("🔄 Starting in SIMULATION mode...")
            await self._run_simulation()
    
    async def _process_message(self, message):
        """پردازش یک پیام MQTT"""
        try:
            topic = str(message.topic)
            payload = json.loads(message.payload.decode())
            
            # استخراج sensor_code از topic
            # Format: econojin/sensors/{sensor_code}/data
            parts = topic.split("/")
            if len(parts) >= 3:
                sensor_code = parts[2]
            else:
                sensor_code = payload.get("sensor_code", "unknown")
            
            # ذخیره در دیتابیس
            await self._save_reading(sensor_code, payload)
            
            # بررسی شرایط هشدار
            await self._check_alerts(sensor_code, payload)
            
            # ارسال به WebSocket clients
            await self._broadcast_ws({
                "type": "sensor_data",
                "sensor_code": sensor_code,
                "data": payload,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            self.message_count += 1
            self.last_message_time = datetime.now(timezone.utc)
            
            if self.message_count % 100 == 0:
                logger.info(f"📊 Processed {self.message_count} messages")
                
        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ Error processing message: {e}")
    
    async def _save_reading(self, sensor_code: str, payload: Dict[str, Any]):
        """ذخیره خوانش سنسور در دیتابیس"""
        async with async_session() as session:
            try:
                reading = SensorReading(
                    sensor_code=sensor_code,
                    timestamp=datetime.fromisoformat(payload.get("timestamp", datetime.now(timezone.utc).isoformat())),
                    value=payload.get("value"),
                    value_secondary=payload.get("value_secondary"),
                    unit=payload.get("unit", ""),
                    quality_flag=payload.get("quality", "good"),
                    battery_level=payload.get("battery"),
                    signal_strength=payload.get("rssi"),
                    raw_payload=payload
                )
                session.add(reading)
                await session.commit()
            except Exception as e:
                logger.error(f"❌ DB Error: {e}")
                await session.rollback()
    
    async def _check_alerts(self, sensor_code: str, payload: Dict[str, Any]):
        """بررسی شرایط تولید هشدار"""
        alerts = []
        
        # هشدار باتری کم
        battery = payload.get("battery")
        if battery is not None and battery < 20:
            alerts.append({
                "alert_type": "low_battery",
                "severity": "warning" if battery > 10 else "critical",
                "message": f"باتری سنسور {sensor_code} در سطح {battery}%",
                "value": battery,
                "threshold": 20
            })
        
        # هشدار آستانه (مثلاً رطوبت خیلی کم یا زیاد)
        value = payload.get("value")
        sensor_type = payload.get("sensor_type", "")
        
        if sensor_type == "tdr" and value is not None:
            if value < 10:  # رطوبت خیلی کم
                alerts.append({
                    "alert_type": "threshold_exceeded",
                    "severity": "warning",
                    "message": f"رطوبت خاک بسیار کم: {value}%",
                    "value": value,
                    "threshold": 10
                })
            elif value > 80:  # رطوبت خیلی زیاد (خطر سیلاب)
                alerts.append({
                    "alert_type": "threshold_exceeded",
                    "severity": "critical",
                    "message": f"رطوبت خاک بسیار بالا (خطر سیلاب): {value}%",
                    "value": value,
                    "threshold": 80
                })
        
        # ذخیره هشدارها
        for alert in alerts:
            await self._save_alert(sensor_code, alert)
    
    async def _save_alert(self, sensor_code: str, alert_data: Dict[str, Any]):
        """ذخیره هشدار در دیتابیس"""
        async with async_session() as session:
            try:
                alert = SensorAlert(
                    sensor_code=sensor_code,
                    alert_type=alert_data["alert_type"],
                    severity=alert_data["severity"],
                    message=alert_data["message"],
                    value=alert_data.get("value"),
                    threshold=alert_data.get("threshold")
                )
                session.add(alert)
                await session.commit()
                logger.warning(f"🚨 Alert: {alert_data['message']}")
            except Exception as e:
                logger.error(f"❌ Alert save error: {e}")
                await session.rollback()
    
    async def _broadcast_ws(self, data: Dict[str, Any]):
        """ارسال داده به تمام WebSocket clients"""
        # این متد در فایل websocket_manager.py پیاده‌سازی می‌شود
        pass
    
    async def _run_simulation(self):
        """حالت شبیه‌سازی برای تست بدون MQTT Broker"""
        import random
        
        logger.info("🎭 Running in SIMULATION mode")
        sensors = ["TDR-001", "TDR-002", "FLUME-001", "RAIN-001", "PIEZ-001"]
        
        while self.running:
            for sensor_code in sensors:
                sensor_type = sensor_code.split("-")[0].lower()
                
                # تولید داده تصادفی واقع‌گرایانه
                if sensor_type == "tdr":
                    value = random.uniform(15, 65)  # رطوبت خاک %
                    unit = "%"
                elif sensor_type == "flume":
                    value = random.uniform(0.1, 2.5)  # دبی m3/s
                    unit = "m3/s"
                elif sensor_type == "rain":
                    value = random.uniform(0, 15)  # بارش mm/hr
                    unit = "mm/hr"
                elif sensor_type == "piez":
                    value = random.uniform(1, 10)  # سطح آب زیرزمینی m
                    unit = "m"
                else:
                    value = random.uniform(0, 100)
                    unit = ""
                
                payload = {
                    "sensor_code": sensor_code,
                    "sensor_type": sensor_type,
                    "value": round(value, 2),
                    "unit": unit,
                    "battery": random.uniform(60, 100),
                    "rssi": random.randint(-100, -40),
                    "quality": "good",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                await self._save_reading(sensor_code, payload)
                await self._check_alerts(sensor_code, payload)
                
                self.message_count += 1
            
            await asyncio.sleep(5)  # هر 5 ثانیه یک بار
    
    def stop(self):
        """توقف سرویس"""
        self.running = False
        logger.info("🛑 MQTT Ingestion Service stopped")


# Singleton instance
mqtt_service = MQTTIngestionService()
'''
    
    write_file(API_DIR / "services" / "mqtt_ingestion.py", content)


# ========== 3. شبیه‌ساز سنسور (برای تست) ==========
def create_sensor_simulator():
    print("\n🎭 ایجاد شبیه‌ساز سنسور...")
    
    content = '''# scripts/sensor_simulator.py
"""
شبیه‌ساز سنسورهای IoT برای تست سیستم
این اسکریپت داده‌های واقع‌گرایانه تولید و به MQTT Broker ارسال می‌کند
"""
import asyncio
import json
import random
import time
from datetime import datetime, timezone
import sys

# تنظیمات
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
INTERVAL = 5  # ثانیه

# تعریف سنسورها
SENSORS = [
    {"code": "TDR-001", "type": "tdr", "location": "حوضه کشف‌رود - ایستگاه ۱", "base_value": 35},
    {"code": "TDR-002", "type": "tdr", "location": "حوضه کشف‌رود - ایستگاه ۲", "base_value": 42},
    {"code": "TDR-003", "type": "tdr", "location": "دشت کویر - زون A", "base_value": 18},
    {"code": "FLUME-001", "type": "flume", "location": "کانال اصلی - ایستگاه ۱", "base_value": 1.2},
    {"code": "FLUME-002", "type": "flume", "location": "کانال فرعی - ایستگاه ۲", "base_value": 0.8},
    {"code": "RAIN-001", "type": "rain", "location": "ایستگاه هواشناسی مرکزی", "base_value": 0},
    {"code": "PIEZ-001", "type": "piez", "location": "چاه پیزومتر ۱", "base_value": 5.5},
    {"code": "PIEZ-002", "type": "piez", "location": "چاه پیزومتر ۲", "base_value": 7.2},
    {"code": "WEATHER-001", "type": "weather", "location": "ایستگاه هواشناسی", "base_value": 25},
]


def generate_reading(sensor: dict) -> dict:
    """تولید یک خوانش واقع‌گرایانه"""
    sensor_type = sensor["type"]
    base = sensor["base_value"]
    
    # افزودن نویز و روند زمانی
    noise = random.gauss(0, base * 0.05)  # نویز گوسی ۵٪
    daily_cycle = 0.1 * base * (0.5 + 0.5 * (datetime.now().hour / 24))  # سیکل روزانه
    
    if sensor_type == "tdr":
        value = base + noise + daily_cycle
        value = max(5, min(95, value))  # محدود به ۵-۹۵٪
        unit = "%"
        value_secondary = 15 + random.gauss(0, 3)  # دمای خاک
    elif sensor_type == "flume":
        value = base + noise + daily_cycle * 0.5
        value = max(0, value)
        unit = "m3/s"
        value_secondary = None
    elif sensor_type == "rain":
        # بارش به صورت رگباری شبیه‌سازی می‌شود
        if random.random() < 0.1:  # ۱۰٪ احتمال بارش
            value = random.expovariate(1/5)  # توزیع نمایی
        else:
            value = 0
        unit = "mm/hr"
        value_secondary = None
    elif sensor_type == "piez":
        value = base + noise * 0.5
        value = max(0, value)
        unit = "m"
        value_secondary = None
    elif sensor_type == "weather":
        value = base + noise + daily_cycle
        unit = "°C"
        value_secondary = random.uniform(30, 80)  # رطوبت نسبی
    else:
        value = base + noise
        unit = ""
        value_secondary = None
    
    # گاهی اوقات کیفیت داده بد باشد
    quality = "good"
    if random.random() < 0.02:
        quality = "suspicious"
    elif random.random() < 0.005:
        quality = "bad"
    
    return {
        "sensor_code": sensor["code"],
        "sensor_type": sensor_type,
        "location": sensor["location"],
        "value": round(value, 2),
        "value_secondary": round(value_secondary, 2) if value_secondary else None,
        "unit": unit,
        "battery": round(random.uniform(70, 100), 1),
        "rssi": random.randint(-95, -45),
        "quality": quality,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


async def run_simulator():
    """اجرای شبیه‌ساز"""
    print("🎭 Econojin Sensor Simulator")
    print("=" * 60)
    print(f"📡 Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"🔢 Sensors: {len(SENSORS)}")
    print(f"⏱️  Interval: {INTERVAL}s")
    print("=" * 60)
    
    try:
        import aiomqtt
        
        async with aiomqtt.Client(MQTT_BROKER, port=MQTT_PORT) as client:
            print("✅ Connected to MQTT Broker")
            
            while True:
                for sensor in SENSORS:
                    reading = generate_reading(sensor)
                    topic = f"econojin/sensors/{sensor['code']}/data"
                    
                    await client.publish(
                        topic,
                        json.dumps(reading),
                        qos=1
                    )
                    
                    # نمایش در کنسول
                    status = "🟢" if reading["quality"] == "good" else "🟡" if reading["quality"] == "suspicious" else "🔴"
                    print(f"{status} {reading['timestamp'][:19]} | {sensor['code']:12} | {reading['value']:6.2f} {reading['unit']:6} | Bat: {reading['battery']:.0f}%")
                
                await asyncio.sleep(INTERVAL)
                
    except ImportError:
        print("⚠️  aiomqtt not installed. Running in API mode...")
        print("📡 Sending data to FastAPI endpoint instead...")
        
        import httpx
        
        async with httpx.AsyncClient() as http_client:
            while True:
                for sensor in SENSORS:
                    reading = generate_reading(sensor)
                    
                    try:
                        response = await http_client.post(
                            "http://localhost:8000/api/v1/iot/ingest",
                            json=reading,
                            timeout=5.0
                        )
                        
                        status = "🟢" if reading["quality"] == "good" else "🟡"
                        print(f"{status} {reading['timestamp'][:19]} | {sensor['code']:12} | {reading['value']:6.2f} {reading['unit']:6}")
                        
                    except Exception as e:
                        print(f"❌ Error: {e}")
                
                await asyncio.sleep(INTERVAL)
    
    except KeyboardInterrupt:
        print("\\n🛑 Simulator stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure FastAPI is running on localhost:8000")


if __name__ == "__main__":
    try:
        asyncio.run(run_simulator())
    except KeyboardInterrupt:
        print("\\n🛑 Simulator stopped by user")
'''
    
    write_file(ROOT / "scripts" / "sensor_simulator.py", content)


# ========== 4. REST API برای کوئری داده‌ها ==========
def create_iot_api():
    print("\n🔗 ایجاد REST API برای IoT...")
    
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


# ============ Models ============
class SensorResponse(BaseModel):
    sensor_code: str
    sensor_type: str
    location_name: str
    latitude: Optional[float]
    longitude: Optional[float]
    status: str
    battery_level: Optional[float]
    last_seen: Optional[datetime]
    
    class Config:
        from_attributes = True


class ReadingResponse(BaseModel):
    sensor_code: str
    timestamp: datetime
    value: Optional[float]
    value_secondary: Optional[float]
    unit: str
    quality_flag: str
    battery_level: Optional[float]
    
    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: int
    sensor_code: str
    timestamp: datetime
    alert_type: str
    severity: str
    message: str
    value: Optional[float]
    acknowledged: bool
    
    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total_sensors: int
    active_sensors: int
    total_readings_24h: int
    alerts_today: int
    avg_battery: float


# ============ Endpoints ============
@router.get("/sensors", response_model=List[SensorResponse])
async def get_sensors(
    status: Optional[str] = None,
    sensor_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """دریافت لیست تمام سنسورها"""
    query = select(Sensor)
    
    if status:
        query = query.where(Sensor.status == status)
    if sensor_type:
        query = query.where(Sensor.sensor_type == sensor_type)
    
    result = await db.execute(query.order_by(Sensor.sensor_code))
    return result.scalars().all()


@router.get("/sensors/{sensor_code}/readings", response_model=List[ReadingResponse])
async def get_sensor_readings(
    sensor_code: str,
    hours: int = Query(default=24, ge=1, le=720),
    limit: int = Query(default=1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db)
):
    """دریافت خوانش‌های یک سنسور در بازه زمانی مشخص"""
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
async def get_latest_reading(
    sensor_code: str,
    db: AsyncSession = Depends(get_db)
):
    """دریافت آخرین خوانش یک سنسور"""
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
        "quality": reading.quality_flag,
        "battery": reading.battery_level
    }


@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    hours: int = Query(default=24, ge=1, le=720),
    severity: Optional[str] = None,
    unacknowledged_only: bool = False,
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """دریافت هشدارها"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(SensorAlert).where(SensorAlert.timestamp >= since)
    
    if severity:
        query = query.where(SensorAlert.severity == severity)
    if unacknowledged_only:
        query = query.where(SensorAlert.acknowledged == False)
    
    query = query.order_by(desc(SensorAlert.timestamp)).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """تأیید یک هشدار"""
    result = await db.execute(
        select(SensorAlert).where(SensorAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    await db.commit()
    
    return {"status": "acknowledged", "alert_id": alert_id}


@router.get("/stats", response_model=StatsResponse)
async def get_iot_stats(db: AsyncSession = Depends(get_db)):
    """دریافت آمار کلی IoT"""
    # تعداد کل سنسورها
    total_sensors = (await db.execute(select(func.count(Sensor.id)))).scalar() or 0
    
    # سنسورهای فعال
    active_sensors = (await db.execute(
        select(func.count(Sensor.id)).where(Sensor.status == "active")
    )).scalar() or 0
    
    # خوانش‌های ۲۴ ساعت اخیر
    since_24h = datetime.utcnow() - timedelta(hours=24)
    readings_24h = (await db.execute(
        select(func.count(SensorReading.id)).where(SensorReading.timestamp >= since_24h)
    )).scalar() or 0
    
    # هشدارهای امروز
    since_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    alerts_today = (await db.execute(
        select(func.count(SensorAlert.id)).where(SensorAlert.timestamp >= since_today)
    )).scalar() or 0
    
    # میانگین باتری
    avg_battery = (await db.execute(
        select(func.avg(Sensor.battery_level)).where(Sensor.status == "active")
    )).scalar() or 0
    
    return StatsResponse(
        total_sensors=total_sensors,
        active_sensors=active_sensors,
        total_readings_24h=readings_24h,
        alerts_today=alerts_today,
        avg_battery=round(avg_battery, 1)
    )


@router.get("/readings/aggregated")
async def get_aggregated_readings(
    sensor_code: str,
    interval: str = Query(default="1h", regex="^(5m|15m|1h|6h|1d)$"),
    hours: int = Query(default=24, ge=1, le=720),
    db: AsyncSession = Depends(get_db)
):
    """دریافت داده‌های تجمیع‌شده (میانگین در بازه زمانی)"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # برای SQLite، تجمیع ساده انجام می‌دهیم
    # برای PostgreSQL/TimescaleDB می‌توان از time_bucket استفاده کرد
    query = (
        select(
            SensorReading.sensor_code,
            func.date_trunc("hour", SensorReading.timestamp).label("time_bucket"),
            func.avg(SensorReading.value).label("avg_value"),
            func.min(SensorReading.value).label("min_value"),
            func.max(SensorReading.value).label("max_value"),
            func.count(SensorReading.id).label("count")
        )
        .where(and_(
            SensorReading.sensor_code == sensor_code,
            SensorReading.timestamp >= since
        ))
        .group_by("time_bucket")
        .order_by("time_bucket")
    )
    
    try:
        result = await db.execute(query)
        rows = result.all()
        
        return [
            {
                "timestamp": row.time_bucket,
                "avg": round(row.avg_value, 2) if row.avg_value else None,
                "min": round(row.min_value, 2) if row.min_value else None,
                "max": round(row.max_value, 2) if row.max_value else None,
                "count": row.count
            }
            for row in rows
        ]
    except Exception as e:
        # Fallback برای SQLite که date_trunc ندارد
        return {"error": "Aggregation not supported in SQLite", "detail": str(e)}


@router.post("/ingest")
async def ingest_reading(
    sensor_code: str,
    sensor_type: str,
    value: float,
    unit: str = "",
    value_secondary: Optional[float] = None,
    battery: Optional[float] = None,
    rssi: Optional[int] = None,
    quality: str = "good",
    timestamp: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """دریافت مستقیم داده سنسور (برای شبیه‌ساز یا HTTP POST)"""
    try:
        ts = datetime.fromisoformat(timestamp) if timestamp else datetime.utcnow()
        
        reading = SensorReading(
            sensor_code=sensor_code,
            timestamp=ts,
            value=value,
            value_secondary=value_secondary,
            unit=unit,
            quality_flag=quality,
            battery_level=battery,
            signal_strength=rssi,
            raw_payload={"source": "http_api"}
        )
        db.add(reading)
        
        # به‌روزرسانی last_seen سنسور
        sensor_result = await db.execute(
            select(Sensor).where(Sensor.sensor_code == sensor_code)
        )
        sensor = sensor_result.scalar_one_or_none()
        if sensor:
            sensor.last_seen = ts
            if battery:
                sensor.battery_level = battery
        
        await db.commit()
        return {"status": "ok", "timestamp": ts.isoformat()}
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
'''
    
    write_file(API_DIR / "modules" / "iot" / "router.py", content)


# ========== 5. WebSocket برای Real-time Dashboard ==========
def create_websocket_manager():
    print("\n🔌 ایجاد WebSocket Manager...")
    
    content = '''# api/services/websocket_manager.py
import asyncio
import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """مدیریت اتصالات WebSocket برای داشبورد Real-time"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.sensor_subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """اتصال یک کلاینت جدید"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"🔌 WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """قطع اتصال یک کلاینت"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # حذف از تمام subscription ها
        for sensor_code in list(self.sensor_subscriptions.keys()):
            if websocket in self.sensor_subscriptions[sensor_code]:
                self.sensor_subscriptions[sensor_code].remove(websocket)
        
        logger.info(f"🔌 WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """ارسال پیام به تمام کلاینت‌ها"""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"❌ WebSocket send error: {e}")
                disconnected.append(connection)
        
        # حذف اتصالات قطع‌شده
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_to_sensor_subscribers(self, sensor_code: str, data: Dict[str, Any]):
        """ارسال داده فقط به مشترکین یک سنسور خاص"""
        subscribers = self.sensor_subscriptions.get(sensor_code, [])
        
        for websocket in subscribers:
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"❌ WebSocket send error: {e}")
                self.disconnect(websocket)
    
    def subscribe_to_sensor(self, websocket: WebSocket, sensor_code: str):
        """اشتراک در داده‌های یک سنسور خاص"""
        if sensor_code not in self.sensor_subscriptions:
            self.sensor_subscriptions[sensor_code] = []
        
        if websocket not in self.sensor_subscriptions[sensor_code]:
            self.sensor_subscriptions[sensor_code].append(websocket)
            logger.info(f"📡 Client subscribed to {sensor_code}")
    
    def unsubscribe_from_sensor(self, websocket: WebSocket, sensor_code: str):
        """لغو اشتراک از یک سنسور"""
        if sensor_code in self.sensor_subscriptions:
            if websocket in self.sensor_subscriptions[sensor_code]:
                self.sensor_subscriptions[sensor_code].remove(websocket)
                logger.info(f"📡 Client unsubscribed from {sensor_code}")


# Singleton
ws_manager = WebSocketManager()
'''
    
    write_file(API_DIR / "services" / "websocket_manager.py", content)


# ========== 6. WebSocket Router ==========
def create_ws_router():
    print("\n🔌 ایجاد WebSocket Router...")
    
    content = '''# api/modules/iot/ws_router.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging
from api.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/iot")
async def websocket_iot_endpoint(websocket: WebSocket):
    """WebSocket endpoint برای دریافت داده‌های Real-time IoT"""
    await ws_manager.connect(websocket)
    
    try:
        # ارسال پیام خوش‌آمدگویی
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Econojin IoT WebSocket",
            "timestamp": "now"
        })
        
        while True:
            # دریافت پیام از کلاینت (مثلاً subscription request)
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "subscribe":
                    sensor_code = message.get("sensor_code")
                    if sensor_code:
                        ws_manager.subscribe_to_sensor(websocket, sensor_code)
                        await websocket.send_json({
                            "type": "subscribed",
                            "sensor_code": sensor_code
                        })
                
                elif action == "unsubscribe":
                    sensor_code = message.get("sensor_code")
                    if sensor_code:
                        ws_manager.unsubscribe_from_sensor(websocket, sensor_code)
                        await websocket.send_json({
                            "type": "unsubscribed",
                            "sensor_code": sensor_code
                        })
                
                elif action == "ping":
                    await websocket.send_json({"type": "pong"})
                
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        ws_manager.disconnect(websocket)
'''
    
    write_file(API_DIR / "modules" / "iot" / "ws_router.py", content)


# ========== 7. Seed Data (داده‌های اولیه) ==========
def create_seed_data():
    print("\n🌱 ایجاد داده‌های اولیه سنسورها...")
    
    content = '''# scripts/seed_sensors.py
"""
ایجاد داده‌های اولیه سنسورها در دیتابیس
"""
import asyncio
import sys
from pathlib import Path

# افزودن ریشه پروژه به path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.core.database import async_session, init_db
from api.modules.iot.models import Sensor


SENSORS_DATA = [
    {
        "sensor_code": "TDR-001",
        "sensor_type": "tdr",
        "location_name": "حوضه کشف‌رود - ایستگاه ۱",
        "latitude": 36.305,
        "longitude": 59.612,
        "elevation_m": 1050,
        "structure_id": 1,
        "status": "active",
        "battery_level": 95.0
    },
    {
        "sensor_code": "TDR-002",
        "sensor_type": "tdr",
        "location_name": "حوضه کشف‌رود - ایستگاه ۲",
        "latitude": 36.308,
        "longitude": 59.615,
        "elevation_m": 1045,
        "structure_id": 1,
        "status": "active",
        "battery_level": 88.0
    },
    {
        "sensor_code": "TDR-003",
        "sensor_type": "tdr",
        "location_name": "دشت کویر - زون A",
        "latitude": 33.520,
        "longitude": 54.510,
        "elevation_m": 850,
        "structure_id": 2,
        "status": "active",
        "battery_level": 72.0
    },
    {
        "sensor_code": "FLUME-001",
        "sensor_type": "flume",
        "location_name": "کانال اصلی - ایستگاه ۱",
        "latitude": 36.310,
        "longitude": 59.620,
        "elevation_m": 1040,
        "structure_id": 3,
        "status": "active",
        "battery_level": 92.0
    },
    {
        "sensor_code": "FLUME-002",
        "sensor_type": "flume",
        "location_name": "کانال فرعی - ایستگاه ۲",
        "latitude": 36.312,
        "longitude": 59.625,
        "elevation_m": 1038,
        "structure_id": 3,
        "status": "active",
        "battery_level": 85.0
    },
    {
        "sensor_code": "RAIN-001",
        "sensor_type": "rain",
        "location_name": "ایستگاه هواشناسی مرکزی",
        "latitude": 36.300,
        "longitude": 59.600,
        "elevation_m": 1060,
        "structure_id": None,
        "status": "active",
        "battery_level": 98.0
    },
    {
        "sensor_code": "PIEZ-001",
        "sensor_type": "piez",
        "location_name": "چاه پیزومتر ۱",
        "latitude": 36.315,
        "longitude": 59.630,
        "elevation_m": 1035,
        "structure_id": 4,
        "status": "active",
        "battery_level": 78.0
    },
    {
        "sensor_code": "PIEZ-002",
        "sensor_type": "piez",
        "location_name": "چاه پیزومتر ۲",
        "latitude": 36.318,
        "longitude": 59.635,
        "elevation_m": 1032,
        "structure_id": 4,
        "status": "active",
        "battery_level": 65.0
    },
    {
        "sensor_code": "WEATHER-001",
        "sensor_type": "weather",
        "location_name": "ایستگاه هواشناسی کامل",
        "latitude": 36.302,
        "longitude": 59.605,
        "elevation_m": 1058,
        "structure_id": None,
        "status": "active",
        "battery_level": 90.0
    },
]


async def seed_sensors():
    """درج داده‌های اولیه سنسورها"""
    print("🌱 Seeding sensors...")
    
    await init_db()
    
    async with async_session() as session:
        for sensor_data in SENSORS_DATA:
            sensor = Sensor(**sensor_data)
            session.add(sensor)
        
        await session.commit()
        print(f"✅ Inserted {len(SENSORS_DATA)} sensors")


if __name__ == "__main__":
    asyncio.run(seed_sensors())
'''
    
    write_file(ROOT / "scripts" / "seed_sensors.py", content)


# ========== Main ==========
def main():
    print("📡 راه‌اندازی لایه ۲ IoT - Real-time Ingestion")
    print("=" * 70)
    
    if not API_DIR.exists():
        print(f"❌ دایرکتوری {API_DIR} یافت نشد!")
        return 1
    
    # ایجاد فایل __init__.py
    write_file(API_DIR / "modules" / "iot" / "__init__.py", "# IoT Module\n")
    
    create_iot_models()
    create_mqtt_service()
    create_sensor_simulator()
    create_iot_api()
    create_websocket_manager()
    create_ws_router()
    create_seed_data()
    
    print("\n" + "=" * 70)
    print("✅ لایه ۲ IoT با موفقیت ایجاد شد!")
    print("\n📁 فایل‌های ایجاد شده:")
    print("   📊 api/modules/iot/models.py - مدل‌های دیتابیس")
    print("   🔌 api/modules/iot/router.py - REST API")
    print("   🔌 api/modules/iot/ws_router.py - WebSocket")
    print("   📡 api/services/mqtt_ingestion.py - سرویس MQTT")
    print("   🔌 api/services/websocket_manager.py - مدیریت WebSocket")
    print("   🎭 scripts/sensor_simulator.py - شبیه‌ساز سنسور")
    print("   🌱 scripts/seed_sensors.py - داده‌های اولیه")
    
    print("\n🚀 گام‌های بعدی:")
    print("   1. نصب پکیج‌ها:")
    print("      python -m pip install aiomqtt httpx")
    print("")
    print("   2. ثبت router در main.py:")
    print("      from api.modules.iot.router import router as iot_router")
    print("      from api.modules.iot.ws_router import router as ws_router")
    print("      app.include_router(iot_router, prefix='/api/v1')")
    print("      app.include_router(ws_router)")
    print("")
    print("   3. اجرای seed data:")
    print("      python scripts/seed_sensors.py")
    print("")
    print("   4. اجرای شبیه‌ساز (در ترمینال دیگر):")
    print("      python scripts/sensor_simulator.py")
    print("")
    print("   5. تست API:")
    print("      curl http://localhost:8000/api/v1/iot/sensors")
    print("      curl http://localhost:8000/api/v1/iot/stats")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())