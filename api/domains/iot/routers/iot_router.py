"""IoT API Router"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from .schemas.iot_schemas import (
    IoTDeviceCreate,
    IoTDeviceResponse,
    SensorReadingCreate,
    SensorReadingResponse,
    AlertRuleCreate,
    AlertResponse,
    DeviceTelemetryBatch
)
from .repositories.iot_repository import IoTRepository
from .services.alert_service import AlertService
from .models.iot_models import IoTDevice, SensorReading, AlertRule, SensorType


router = APIRouter(prefix="/iot", tags=["IoT"])


def get_iot_repository() -> IoTRepository:
    """Dependency Injection"""
    return IoTRepository()


def get_alert_service(repo: IoTRepository = Depends(get_iot_repository)) -> AlertService:
    """Dependency Injection"""
    return AlertService(repo)


# Device Endpoints
@router.post("/devices", response_model=IoTDeviceResponse)
async def create_device(
    device: IoTDeviceCreate,
    repo: IoTRepository = Depends(get_iot_repository)
):
    """ایجاد دستگاه IoT جدید"""
    db_device = IoTDevice(
        device_id=device.device_id,
        name=device.name,
        sensor_type=device.sensor_type,
        location_lat=device.location_lat,
        location_lon=device.location_lon,
        elevation_m=device.elevation_m,
        project_id=device.project_id,
        pilot_site=device.pilot_site,
        firmware_version=device.firmware_version
    )
    
    success = repo.create_device(db_device)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create device")
    
    return db_device


@router.get("/devices/{device_id}", response_model=IoTDeviceResponse)
async def get_device(
    device_id: str,
    repo: IoTRepository = Depends(get_iot_repository)
):
    """دریافت اطلاعات یک دستگاه"""
    device = repo.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.get("/devices/project/{project_id}", response_model=List[IoTDeviceResponse])
async def get_devices_by_project(
    project_id: str,
    repo: IoTRepository = Depends(get_iot_repository)
):
    """دریافت تمام دستگاه‌های یک پروژه"""
    return repo.get_devices_by_project(project_id)


@router.get("/devices/pilot/{pilot_site}", response_model=List[IoTDeviceResponse])
async def get_devices_by_pilot(
    pilot_site: str,
    repo: IoTRepository = Depends(get_iot_repository)
):
    """دریافت تمام دستگاه‌های یک پایلوت"""
    return repo.get_devices_by_pilot(pilot_site)


# Reading Endpoints
@router.post("/readings", response_model=SensorReadingResponse)
async def create_reading(
    reading: SensorReadingCreate,
    repo: IoTRepository = Depends(get_iot_repository),
    alert_service: AlertService = Depends(get_alert_service)
):
    """ثبت قرائت حسگر"""
    import uuid
    
    db_reading = SensorReading(
        reading_id=str(uuid.uuid4()),
        device_id=reading.device_id,
        timestamp=reading.timestamp,
        value=reading.value,
        unit=reading.unit,
        quality=reading.quality,
        location_lat=reading.location_lat,
        location_lon=reading.location_lon
    )
    
    success = repo.create_reading(db_reading)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create reading")
    
    # بررسی هشدارها
    alerts = alert_service.evaluate_reading(db_reading)
    for alert in alerts:
        repo.create_alert(alert)
    
    return db_reading


@router.post("/readings/batch")
async def create_readings_batch(
    batch: DeviceTelemetryBatch,
    repo: IoTRepository = Depends(get_iot_repository)
):
    """ثبت بچ قرائت‌ها"""
    import uuid
    
    readings = []
    for r in batch.readings:
        readings.append(SensorReading(
            reading_id=str(uuid.uuid4()),
            device_id=r.device_id,
            timestamp=r.timestamp,
            value=r.value,
            unit=r.unit,
            quality=r.quality
        ))
    
    count = repo.create_readings_batch(readings)
    return {"created": count}


@router.get("/readings/device/{device_id}", response_model=List[SensorReadingResponse])
async def get_device_readings(
    device_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(default=100, le=1000),
    repo: IoTRepository = Depends(get_iot_repository)
):
    """دریافت قرائت‌های یک دستگاه"""
    return repo.get_readings_by_device(device_id, start_time, end_time, limit)


# Alert Endpoints
@router.post("/alert-rules", response_model=AlertResponse)
async def create_alert_rule(
    rule: AlertRuleCreate,
    repo: IoTRepository = Depends(get_iot_repository)
):
    """ایجاد قانون هشدار"""
    import uuid
    
    db_rule = AlertRule(
        rule_id=str(uuid.uuid4()),
        name=rule.name,
        sensor_type=rule.sensor_type,
        threshold_min=rule.threshold_min,
        threshold_max=rule.threshold_max,
        severity=rule.severity,
        project_id=rule.project_id
    )
    
    success = repo.create_alert_rule(db_rule)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create alert rule")
    
    return db_rule


@router.get("/alerts/active", response_model=List[AlertResponse])
async def get_active_alerts(
    project_id: Optional[str] = None,
    repo: IoTRepository = Depends(get_iot_repository)
):
    """دریافت هشدارهای فعال"""
    return repo.get_active_alerts(project_id)


# Analytics Endpoints
@router.get("/analytics/drought/{pilot_site}")
async def check_drought_conditions(
    pilot_site: str,
    soil_moisture_threshold: float = Query(default=20.0),
    alert_service: AlertService = Depends(get_alert_service)
):
    """بررسی شرایط خشکسالی"""
    return alert_service.check_drought_conditions(pilot_site, soil_moisture_threshold)


@router.get("/analytics/flood-risk/{pilot_site}")
async def check_flood_risk(
    pilot_site: str,
    water_level_threshold: float = Query(default=80.0),
    alert_service: AlertService = Depends(get_alert_service)
):
    """بررسی ریسک سیلاب"""
    return alert_service.check_flood_risk(pilot_site, water_level_threshold)


@router.get("/analytics/daily-report/{pilot_site}")
async def get_daily_report(
    pilot_site: str,
    alert_service: AlertService = Depends(get_alert_service)
):
    """دریافت گزارش روزانه"""
    return alert_service.generate_daily_report(pilot_site)
