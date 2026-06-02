# -*- coding: utf-8 -*-
"""
مدل‌های داده برای شبکه IoT
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class SensorType(str, Enum):
    """انواع سنسور"""
    SOIL_MOISTURE = "soil_moisture"
    SOIL_TEMPERATURE = "soil_temperature"
    AIR_TEMPERATURE = "air_temperature"
    AIR_HUMIDITY = "air_humidity"
    LIGHT_INTENSITY = "light_intensity"
    CO2_CONCENTRATION = "co2_concentration"
    RAINFALL = "rainfall"
    WIND_SPEED = "wind_speed"


@dataclass
class SensorReading:
    """یک خوانش سنسور"""
    sensor_id: str
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    battery_percent: Optional[float] = None
    quality_score: float = 1.0  # 0-1
    
    def is_valid(self) -> bool:
        """اعتبارسنجی داده"""
        # محدوده‌های معقول
        ranges = {
            SensorType.SOIL_MOISTURE: (0.0, 1.0),
            SensorType.SOIL_TEMPERATURE: (-20, 60),
            SensorType.AIR_TEMPERATURE: (-40, 60),
            SensorType.AIR_HUMIDITY: (0, 100),
            SensorType.CO2_CONCENTRATION: (300, 5000),
            SensorType.RAINFALL: (0, 500),
        }
        
        if self.sensor_type in ranges:
            min_val, max_val = ranges[self.sensor_type]
            return min_val <= self.value <= max_val
        
        return True


@dataclass
class SensorNetwork:
    """شبکه سنسورها"""
    network_id: str
    name: str
    location_region: str
    sensors: List[SensorReading] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_latest(self, sensor_type: SensorType) -> Optional[SensorReading]:
        """دریافت آخرین خوانش یک نوع سنسور"""
        readings = [
            s for s in self.sensors
            if s.sensor_type == sensor_type
        ]
        if not readings:
            return None
        return max(readings, key=lambda s: s.timestamp)
    
    def get_statistics(self, sensor_type: SensorType) -> Dict:
        """آمار یک نوع سنسور"""
        readings = [
            s for s in self.sensors
            if s.sensor_type == sensor_type
        ]
        
        if not readings:
            return {"count": 0}
        
        values = [s.value for s in readings]
        return {
            "count": len(readings),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": max(readings, key=lambda s: s.timestamp).value,
        }