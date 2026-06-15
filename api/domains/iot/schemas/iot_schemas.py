"""IoT Domain Schemas - Pydantic Models"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from .models.iot_models import SensorType, DeviceStatus


class IoTDeviceCreate(BaseModel):
    """اسکیما برای ایجاد دستگاه"""
    device_id: str
    name: str
    sensor_type: SensorType
    location_lat: float = Field(..., ge=-90, le=90)
    location_lon: float = Field(..., ge=-180, le=180)
    elevation_m: Optional[float] = None
    project_id: Optional[str] = None
    pilot_site: Optional[str] = None
    firmware_version: Optional[str] = None


class IoTDeviceResponse(BaseModel):
    """اسکیما پاسخ دستگاه"""
    device_id: str
    name: str
    sensor_type: SensorType
    location_lat: float
    location_lon: float
    elevation_m: Optional[float]
    project_id: Optional[str]
    pilot_site: Optional[str]
    status: DeviceStatus
    last_seen: Optional[datetime]
    battery_level: Optional[float]
    
    class Config:
        from_attributes = True


class SensorReadingCreate(BaseModel):
    """اسکیما برای ایجاد قرائت"""
    device_id: str
    timestamp: datetime
    value: float
    unit: str
    quality: str = "good"
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None


class SensorReadingResponse(BaseModel):
    """اسکیما پاسخ قرائت"""
    reading_id: str
    device_id: str
    timestamp: datetime
    value: float
    unit: str
    quality: str
    
    class Config:
        from_attributes = True


class AlertRuleCreate(BaseModel):
    """اسکیما برای ایجاد قانون هشدار"""
    name: str
    sensor_type: SensorType
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    severity: str = "warning"
    project_id: Optional[str] = None


class AlertResponse(BaseModel):
    """اسکیما پاسخ هشدار"""
    alert_id: str
    rule_id: str
    device_id: str
    timestamp: datetime
    severity: str
    message: str
    value: float
    acknowledged: bool
    
    class Config:
        from_attributes = True


class DeviceTelemetryBatch(BaseModel):
    """بچ قرائت‌های تلمتری"""
    device_id: str
    readings: List[SensorReadingCreate]
