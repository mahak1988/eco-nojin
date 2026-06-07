"""
IoT MQTT Service
اتصال به EMQX/Mosquitto برای داده‌های real-time سنسورها
Documentation: https://www.emqx.com/docs/
"""
import asyncio
import json
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from collections import defaultdict
import time


class SensorReading(BaseModel):
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: str
    quality: float = 1.0
    location: Optional[Dict[str, float]] = None


class SensorStats(BaseModel):
    sensor_id: str
    sensor_type: str
    count: int
    mean: float
    min: float
    max: float
    std: float
    last_value: float
    last_update: str
    status: str  # normal, warning, critical


class IoTAlert(BaseModel):
    id: str
    sensor_id: str
    alert_type: str
    severity: str  # info, warning, critical
    message: str
    value: float
    threshold: float
    timestamp: str
    acknowledged: bool = False


class MQTTService:
    """سرویس MQTT برای IoT - بدون نیاز به broker خارجی"""
    
    # Thresholds for different sensor types
    THRESHOLDS = {
        'soil_moisture': {'min': 20, 'max': 80, 'unit': '%', 'warning_low': 30, 'warning_high': 70},
        'temperature': {'min': -10, 'max': 50, 'unit': '°C', 'warning_low': 5, 'warning_high': 40},
        'humidity': {'min': 20, 'max': 95, 'unit': '%', 'warning_low': 30, 'warning_high': 85},
        'air_quality': {'min': 0, 'max': 500, 'unit': 'AQI', 'warning_low': 0, 'warning_high': 100},
        'co2': {'min': 300, 'max': 5000, 'unit': 'ppm', 'warning_low': 350, 'warning_high': 1000},
        'light': {'min': 0, 'max': 100000, 'unit': 'lux', 'warning_low': 100, 'warning_high': 50000},
        'wind_speed': {'min': 0, 'max': 150, 'unit': 'km/h', 'warning_low': 0, 'warning_high': 60},
        'rainfall': {'min': 0, 'max': 200, 'unit': 'mm/h', 'warning_low': 0, 'warning_high': 50},
        'water_level': {'min': 0, 'max': 10, 'unit': 'm', 'warning_low': 1, 'warning_high': 8},
        'ph': {'min': 0, 'max': 14, 'unit': 'pH', 'warning_low': 5.5, 'warning_high': 8.5},
        'ec': {'min': 0, 'max': 5, 'unit': 'dS/m', 'warning_low': 0.5, 'warning_high': 3.0},
        'ndvi': {'min': -1, 'max': 1, 'unit': 'index', 'warning_low': 0.1, 'warning_high': 0.8},
    }
    
    def __init__(self):
        # In-memory storage (replace with Redis/TimescaleDB in production)
        self._readings: Dict[str, List[SensorReading]] = defaultdict(list)
        self._latest: Dict[str, SensorReading] = {}
        self._alerts: List[IoTAlert] = []
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._max_history = 1000  # Max readings per sensor
    
    async def publish_reading(self, reading: SensorReading) -> bool:
        """انتشار خوانش سنسور"""
        try:
            # Validate reading
            if reading.sensor_type not in self.THRESHOLDS:
                return False
            
            # Store reading
            self._readings[reading.sensor_id].append(reading)
            self._latest[reading.sensor_id] = reading
            
            # Trim history
            if len(self._readings[reading.sensor_id]) > self._max_history:
                self._readings[reading.sensor_id] = self._readings[reading.sensor_id][-self._max_history:]
            
            # Check thresholds
            await self._check_thresholds(reading)
            
            # Notify subscribers
            for callback in self._subscribers.get(reading.sensor_type, []):
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(reading)
                    else:
                        callback(reading)
                except Exception as e:
                    print(f"Subscriber error: {e}")
            
            return True
        except Exception as e:
            print(f"Publish error: {e}")
            return False
    
    async def _check_thresholds(self, reading: SensorReading):
        """بررسی آستانه‌ها و ایجاد هشدار"""
        thresholds = self.THRESHOLDS.get(reading.sensor_type)
        if not thresholds:
            return
        
        severity = None
        message = ""
        
        if reading.value < thresholds['min'] or reading.value > thresholds['max']:
            severity = "critical"
            message = f"مقدار بحرانی: {reading.value} {thresholds['unit']}"
        elif reading.value < thresholds['warning_low']:
            severity = "warning"
            message = f"مقدار پایین: {reading.value} {thresholds['unit']}"
        elif reading.value > thresholds['warning_high']:
            severity = "warning"
            message = f"مقدار بالا: {reading.value} {thresholds['unit']}"
        
        if severity:
            alert = IoTAlert(
                id=f"alert_{int(time.time() * 1000)}",
                sensor_id=reading.sensor_id,
                alert_type=reading.sensor_type,
                severity=severity,
                message=message,
                value=reading.value,
                threshold=thresholds['warning_high'] if reading.value > thresholds['warning_high'] else thresholds['warning_low'],
                timestamp=datetime.now().isoformat()
            )
            self._alerts.append(alert)
            
            # Keep only last 100 alerts
            if len(self._alerts) > 100:
                self._alerts = self._alerts[-100:]
    
    def get_latest_reading(self, sensor_id: str) -> Optional[SensorReading]:
        """دریافت آخرین خوانش"""
        return self._latest.get(sensor_id)
    
    def get_all_latest(self) -> List[SensorReading]:
        """دریافت آخرین خوانش همه سنسورها"""
        return list(self._latest.values())
    
    def get_history(
        self,
        sensor_id: str,
        hours: int = 24,
        limit: int = 100
    ) -> List[SensorReading]:
        """دریافت تاریخچه خوانش‌ها"""
        readings = self._readings.get(sensor_id, [])
        
        # Filter by time
        cutoff = datetime.now() - timedelta(hours=hours)
        filtered = [
            r for r in readings
            if datetime.fromisoformat(r.timestamp) > cutoff
        ]
        
        return filtered[-limit:]
    
    def get_statistics(self, sensor_id: str, hours: int = 24) -> Optional[SensorStats]:
        """محاسبه آمار سنسور"""
        readings = self.get_history(sensor_id, hours)
        
        if not readings:
            return None
        
        values = [r.value for r in readings]
        latest = readings[-1]
        
        # Calculate statistics
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std = variance ** 0.5
        
        # Determine status
        thresholds = self.THRESHOLDS.get(latest.sensor_type, {})
        if latest.value < thresholds.get('min', 0) or latest.value > thresholds.get('max', 100):
            status = "critical"
        elif latest.value < thresholds.get('warning_low', 0) or latest.value > thresholds.get('warning_high', 100):
            status = "warning"
        else:
            status = "normal"
        
        return SensorStats(
            sensor_id=sensor_id,
            sensor_type=latest.sensor_type,
            count=len(values),
            mean=round(mean, 2),
            min=round(min(values), 2),
            max=round(max(values), 2),
            std=round(std, 2),
            last_value=latest.value,
            last_update=latest.timestamp,
            status=status
        )
    
    def get_all_statistics(self, hours: int = 24) -> List[SensorStats]:
        """دریافت آمار همه سنسورها"""
        stats = []
        for sensor_id in self._latest.keys():
            stat = self.get_statistics(sensor_id, hours)
            if stat:
                stats.append(stat)
        return stats
    
    def get_alerts(
        self,
        severity: Optional[str] = None,
        limit: int = 50
    ) -> List[IoTAlert]:
        """دریافت هشدارها"""
        alerts = self._alerts
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return alerts[-limit:]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """تأیید هشدار"""
        for alert in self._alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def subscribe(self, sensor_type: str, callback: Callable):
        """اشتراک در نوع سنسور"""
        self._subscribers[sensor_type].append(callback)
    
    def get_sensor_types(self) -> List[str]:
        """دریافت لیست انواع سنسورها"""
        return list(self.THRESHOLDS.keys())
    
    def generate_sample_data(self, count: int = 10) -> List[SensorReading]:
        """تولید داده‌های نمونه برای تست"""
        import random
        
        readings = []
        sensor_types = list(self.THRESHOLDS.keys())
        
        for i in range(count):
            sensor_type = random.choice(sensor_types)
            thresholds = self.THRESHOLDS[sensor_type]
            
            # Generate value within normal range
            value = random.uniform(
                thresholds['warning_low'],
                thresholds['warning_high']
            )
            
            reading = SensorReading(
                sensor_id=f"sensor_{i+1:03d}",
                sensor_type=sensor_type,
                value=round(value, 2),
                unit=thresholds['unit'],
                timestamp=datetime.now().isoformat(),
                quality=round(random.uniform(0.8, 1.0), 2),
                location={
                    "lat": 35.6892 + random.uniform(-0.1, 0.1),
                    "lng": 51.3890 + random.uniform(-0.1, 0.1)
                }
            )
            readings.append(reading)
        
        return readings


# Singleton
mqtt_service = MQTTService()
