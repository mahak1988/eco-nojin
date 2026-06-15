"""IoT Domain Models - Sensors and Readings"""
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class SensorType(str, Enum):
    """انواع حسگرهای IoT"""
    SOIL_MOISTURE = "soil_moisture"
    SOIL_TEMPERATURE = "soil_temperature"
    AIR_TEMPERATURE = "air_temperature"
    AIR_HUMIDITY = "air_humidity"
    WATER_LEVEL = "water_level"
    WATER_QUALITY_PH = "water_quality_ph"
    WATER_QUALITY_EC = "water_quality_ec"
    RAINFALL = "rainfall"
    WIND_SPEED = "wind_speed"
    SOLAR_RADIATION = "solar_radiation"
    ATMOSPHERIC_PRESSURE = "atmospheric_pressure"


class DeviceStatus(str, Enum):
    """وضعیت دستگاه"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"


@dataclass
class IoTDevice:
    """نماینده یک دستگاه IoT"""
    device_id: str
    name: str
    sensor_type: SensorType
    location_lat: float
    location_lon: float
    elevation_m: Optional[float] = None
    project_id: Optional[str] = None
    pilot_site: Optional[str] = None  # dishmok, behbahan, roudbar, yasouj
    installation_date: datetime = field(default_factory=datetime.utcnow)
    last_seen: Optional[datetime] = None
    status: DeviceStatus = DeviceStatus.OFFLINE
    battery_level: Optional[float] = None  # percentage
    firmware_version: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class SensorReading:
    """نماینده یک قرائت حسگر"""
    reading_id: str
    device_id: str
    timestamp: datetime
    value: float
    unit: str
    quality: str = "good"  # good, suspicious, bad
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class AlertRule:
    """قانون هشدار"""
    rule_id: str
    name: str
    sensor_type: SensorType
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    severity: str = "warning"  # info, warning, critical
    enabled: bool = True
    project_id: Optional[str] = None


@dataclass
class Alert:
    """هشدار فعال"""
    alert_id: str
    rule_id: str
    device_id: str
    reading_id: str
    timestamp: datetime
    severity: str
    message: str
    value: float
    threshold: float
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
