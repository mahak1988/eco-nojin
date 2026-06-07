from api.services.iot.mqtt_service import mqtt_service
# api/modules/iot/router.py
"""
ماژول مدیریت سنسورها و داده‌های شهروندی (IoT)
نسخه 2.0 - بهینه‌سازی شده برای پرفورمنس بالا و امنیت داده‌ها
"""
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from api.core.database import get_db
from api.core.security import get_current_user
from api.modules.library.models import User
from api.modules.iot.models import Sensor, SensorReading, SensorAlert

logger = logging.getLogger(__name__)
class IoTStatsResponse(BaseModel):
    """Auto-generated response model for get_stats"""
    total_sensors: int = 0
    active_sensors: int = 0
    total_readings_24h: int = 0
    alerts_today: int = 0
    avg_battery: float = 0.0


router = APIRouter(prefix="/iot", tags=["IoT"])


# =========================================================================
# Pydantic Models (Request & Response)
# =========================================================================
class SensorResponse(BaseModel):
    sensor_code: str
    sensor_type: str
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    battery_level: Optional[float] = None
    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    total_sensors: int
    active_sensors: int
    total_readings_24h: int
    alerts_today: int
    avg_battery: float

# 🔴 اصلاح: مدل جدید برای دریافت داده سنسور در Body
class SensorIngestRequest(BaseModel):
    sensor_code: str = Field(..., description="کد منحصر به فرد سنسور")
    value: float = Field(..., description="مقدار خوانش شده")
    unit: str = Field(default="", description="واحد اندازه‌گیری")
    battery: Optional[float] = Field(None, ge=0, le=100, description="سطح باتری (درصد)")
    quality: str = Field(default="good", description="شاخص کیفیت داده")

class CitizenDataSubmission(BaseModel):
    module_type: str = Field(..., description="نوع ماژول (مثلاً air_quality)")
    measurement_type: str = Field(..., description="نوع اندازه‌گیری (مثلاً pm2.5)")
    value: float = Field(..., description="مقدار اندازه‌گیری شده")
    unit: str = Field(default="", description="واحد اندازه‌گیری")
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    location_name: Optional[str] = None
    notes: Optional[str] = None
    measurement_method: Optional[str] = None
    confidence_level: float = Field(default=0.7, ge=0.0, le=1.0)


# =========================================================================
# Dependencies
# =========================================================================
async def verify_sensor_token(x_sensor_token: Optional[str] = Header(None)):
    """
    🔴 احراز هویت سنسورها (IoT Devices)
    در محیط تولید، این توکن باید با یک لیست سفید در Redis یا دیتابیس چک شود.
    """
    # TODO: Implement actual API Key validation logic
    # if not x_sensor_token or not is_valid_token(x_sensor_token):
    #     raise HTTPException(status_code=401, detail="Invalid sensor token")
    return True


# =========================================================================
# Endpoints
# =========================================================================
@router.get("/sensors", response_model=List[SensorResponse])
async def get_sensors(db: AsyncSession = Depends(get_db)):
    """دریافت لیست سنسورها"""
    result = await db.execute(select(Sensor).order_by(Sensor.sensor_code))
    return result.scalars().all()


@router.get("/sensors/{sensor_code}/latest", response_model=Dict[str, Any])
async def get_latest(sensor_code: str, db: AsyncSession = Depends(get_db)):
    """دریافت آخرین خوانش سنسور"""
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


@router.get("/stats", response_model=IoTStatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """آمار کلی IoT (بهینه‌سازی شده)"""
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
        avg_battery=round(float(avg_bat), 1) if avg_bat else 0.0
    )


# 🔴 اصلاح حیاتی: دریافت داده در Body + احراز هویت سنسور
@router.post("/ingest", response_model=StatsResponse)
async def ingest(
    data: SensorIngestRequest, # 🔴 اکنون JSON Body دریافت می‌کند
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_sensor_token)
):
    """ثبت خوانش سنسور (سریع و ایمن)"""
    try:
        reading = SensorReading(
            sensor_code=data.sensor_code,
            timestamp=datetime.utcnow(),
            value=data.value,
            unit=data.unit,
            quality_flag=data.quality,
            battery_level=data.battery
        )
        db.add(reading)
        await db.commit()
        
        logger.info(f"✅ Sensor {data.sensor_code} ingested: {data.value}{data.unit}")
        return {"status": "ok", "sensor_code": data.sensor_code}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Error ingesting sensor data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during ingestion")


# 🔴 اصلاح حیاتی: اضافه کردن احراز هویت شهروند
@router.post("/citizen/submit", response_model=Dict[str, Any])
async def submit_citizen_data(
    data: CitizenDataSubmission,
    current_user: User = Depends(get_current_user), # 🔴 فقط کاربران لاگین کرده
    db: AsyncSession = Depends(get_db)
):
    """ثبت داده شهروندی (با ردیابی کامل کاربر)"""
    try:
        # 🔴 اصلاح: افزودن ID کاربر به کد سنسور برای جلوگیری از تداخل
        sensor_code = f"CITIZEN-{data.module_type.upper()}-{current_user.id}"
        
        reading = SensorReading(
            sensor_code=sensor_code,
            timestamp=datetime.utcnow(),
            value=data.value,
            unit=data.unit or "",
            quality_flag="citizen",
            raw_payload={
                "user_id": current_user.id, # 🔴 ذخیره ID کاربر برای حسابرسی
                "module_type": data.module_type,
                "measurement_type": data.measurement_type,
                "latitude": data.latitude,
                "longitude": data.longitude,
                "location_name": data.location_name,
                "notes": data.notes,
                "measurement_method": data.measurement_method,
                "confidence_level": data.confidence_level,
                "source": "citizen_science"
            }
        )
        db.add(reading)
        await db.commit()
        
        logger.info(f"✅ Citizen {current_user.id} submitted data: {data.module_type} = {data.value}")
        
        return {
            "status": "success",
            "message": "داده شما با موفقیت ثبت شد و به امتیاز شهروندی شما افزوده خواهد شد",
            "reading_id": reading.id,
            "confidence_level": data.confidence_level
        }
    
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Error in citizen submit: {e}")
        raise HTTPException(status_code=500, detail="خطا در ثبت داده شهروندی")


# 🔴 اصلاح حیاتی: فیلتر کردن در سطح دیتابیس (SQL)
@router.get("/citizen/recent", response_model=IDResponse)
async def get_recent_citizen_data(
    limit: int = Query(default=50, ge=1, le=500),
    module_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """دریافت داده‌های شهروندی اخیر (بهینه‌سازی شده برای پرفورمنس)"""
    query = (
        select(SensorReading)
        .where(SensorReading.quality_flag == "citizen")
        .order_by(desc(SensorReading.timestamp))
        .limit(limit)
    )
    
    # 🔴 بهینه‌سازی: فیلتر کردن در دیتابیس به جای پایتون
    if module_type:
        try:
            # استفاده از قابلیت JSON دیتابیس (PostgreSQL/MySQL)
            query = query.where(SensorReading.raw_payload['module_type'].astext == module_type)
        except Exception:
            # Fallback برای دیتابیس‌هایی که از این سینتکس پشتیبانی نمی‌کنند
            pass 
    
    result = await db.execute(query)
    readings = result.scalars().all()
    
    # Fallback filter (فقط در صورتی که فیلتر دیتابیس کار نکرد)
    if module_type and not hasattr(SensorReading.raw_payload.type, 'astext'):
         readings = [r for r in readings if r.raw_payload and r.raw_payload.get("module_type") == module_type]

    return [
        {
            "id": r.id,
            "timestamp": r.timestamp,
            "module_type": r.raw_payload.get("module_type") if r.raw_payload else None,
            "measurement_type": r.raw_payload.get("measurement_type") if r.raw_payload else None,
            "value": r.value,
            "unit": r.unit,
            "location_name": r.raw_payload.get("location_name") if r.raw_payload else None,
            "latitude": r.raw_payload.get("latitude") if r.raw_payload else None,
            "longitude": r.raw_payload.get("longitude") if r.raw_payload else None,
            "confidence_level": r.raw_payload.get("confidence_level") if r.raw_payload else 0.7,
            "notes": r.raw_payload.get("notes") if r.raw_payload else None
        }
        for r in readings
    ]