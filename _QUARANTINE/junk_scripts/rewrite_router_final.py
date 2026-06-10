#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 بازنویسی کامل router.py با import صحیح
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"


def main():
    print("🔧 بازنویسی کامل router.py")
    print("=" * 70)
    
    router_path = API_DIR / "modules" / "iot" / "router.py"
    
    content = '''# api/modules/iot/router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from api.core.database import get_db
from api.modules.iot.models import Sensor, SensorReading, SensorAlert

router = APIRouter(prefix="/iot", tags=["IoT"])


# ============ Response Models ============
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


class CitizenDataSubmission(BaseModel):
    """مدل ثبت داده شهروندی - همه فیلدهای اختیاری با Optional"""
    module_type: str = Field(..., description="نوع ماژول")
    measurement_type: str = Field(..., description="نوع اندازه‌گیری")
    value: float = Field(..., description="مقدار اندازه‌گیری شده")
    unit: str = Field(default="", description="واحد اندازه‌گیری")
    latitude: Optional[float] = Field(default=None, description="عرض جغرافیایی")
    longitude: Optional[float] = Field(default=None, description="طول جغرافیایی")
    location_name: Optional[str] = Field(default=None, description="نام مکان")
    notes: Optional[str] = Field(default=None, description="یادداشت‌ها")
    measurement_method: Optional[str] = Field(default=None, description="روش اندازه‌گیری")
    confidence_level: float = Field(default=0.7, ge=0.0, le=1.0, description="سطح اطمینان")


# ============ Endpoints ============
@router.get("/sensors", response_model=List[SensorResponse])
async def get_sensors(db: AsyncSession = Depends(get_db)):
    """دریافت لیست سنسورها"""
    result = await db.execute(select(Sensor).order_by(Sensor.sensor_code))
    return result.scalars().all()


@router.get("/sensors/{sensor_code}/latest")
async def get_latest(sensor_code: str, db: AsyncSession = Depends(get_db)):
    """دریافت آخرین خوانش"""
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
    """آمار IoT"""
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
    """ثبت خوانش سنسور"""
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


# ============ Citizen Science Endpoints ============
@router.post("/citizen/submit")
async def submit_citizen_data(
    data: CitizenDataSubmission,
    db: AsyncSession = Depends(get_db)
):
    """ثبت داده شهروندی"""
    try:
        sensor_code = f"CITIZEN-{data.module_type.upper()}"
        
        reading = SensorReading(
            sensor_code=sensor_code,
            timestamp=datetime.utcnow(),
            value=data.value,
            unit=data.unit or "",
            quality_flag="citizen",
            raw_payload={
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
        
        return {
            "status": "success",
            "message": "داده شما با موفقیت ثبت شد",
            "reading_id": reading.id,
            "confidence_level": data.confidence_level
        }
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"خطا در ثبت داده: {str(e)}")


@router.get("/citizen/recent")
async def get_recent_citizen_data(
    limit: int = Query(default=50, ge=1, le=500),
    module_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """دریافت داده‌های شهروندی اخیر"""
    query = (
        select(SensorReading)
        .where(SensorReading.quality_flag == "citizen")
        .order_by(desc(SensorReading.timestamp))
        .limit(limit)
    )
    
    result = await db.execute(query)
    readings = result.scalars().all()
    
    if module_type:
        readings = [
            r for r in readings 
            if r.raw_payload and r.raw_payload.get("module_type") == module_type
        ]
    
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
'''
    
    # نوشتن فایل
    router_path.parent.mkdir(parents=True, exist_ok=True)
    router_path.write_text(content, encoding="utf-8")
    
    print(f"✅ فایل بازنویسی شد: {router_path.relative_to(ROOT)}")
    print(f"   حجم: {router_path.stat().st_size} bytes")
    
    # بررسی import ها
    if "from typing import List, Optional" in content:
        print("   ✅ Optional import شده")
    else:
        print("   ❌ Optional import نشده!")
        return 1
    
    print("\n🚀 حالا سرور بک‌اند را اجرا کنید:")
    print("   uvicorn api.main:app --reload --port 8000")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())