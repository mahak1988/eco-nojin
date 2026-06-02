# -*- coding: utf-8 -*-
"""
IoT Sensor Simulator
Simulates soil, weather, and environmental sensors
"""

import random
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SensorReading:
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime
    latitude: float
    longitude: float
    quality: float  # 0-1


class IoTSimulator:
    """Simulates IoT sensor networks for environmental monitoring"""

    SENSOR_TYPES = {
        'soil_moisture': {'unit': '%', 'min': 10, 'max': 90, 'noise': 5},
        'soil_temperature': {'unit': '°C', 'min': 5, 'max': 35, 'noise': 2},
        'soil_ph': {'unit': 'pH', 'min': 5.5, 'max': 8.5, 'noise': 0.3},
        'air_temperature': {'unit': '°C', 'min': -5, 'max': 45, 'noise': 3},
        'air_humidity': {'unit': '%', 'min': 20, 'max': 95, 'noise': 8},
        'light_intensity': {'unit': 'lux', 'min': 0, 'max': 100000, 'noise': 5000},
        'co2_concentration': {'unit': 'ppm', 'min': 350, 'max': 1500, 'noise': 50},
        'rainfall': {'unit': 'mm', 'min': 0, 'max': 100, 'noise': 5},
        'wind_speed': {'unit': 'm/s', 'min': 0, 'max': 30, 'noise': 3},
        'ndvi': {'unit': 'index', 'min': -0.1, 'max': 0.9, 'noise': 0.05},
    }

    def __init__(self, num_sensors: int = 10):
        self.sensors: Dict[str, Dict] = {}
        self.readings: List[SensorReading] = []
        self._initialize_sensors(num_sensors)

    def _initialize_sensors(self, num_sensors: int):
        """Initialize sensor network"""
        sensor_types = list(self.SENSOR_TYPES.keys())

        for i in range(num_sensors):
            sensor_type = sensor_types[i % len(sensor_types)]
            sensor_id = f"sensor_{i:03d}_{sensor_type}"

            self.sensors[sensor_id] = {
                'id': sensor_id,
                'type': sensor_type,
                'latitude': 35.6892 + random.uniform(-0.1, 0.1),
                'longitude': 51.3890 + random.uniform(-0.1, 0.1),
                'installed': datetime.now(timezone.utc) - timedelta(days=random.randint(30, 365)),
                'battery': random.uniform(60, 100),
                'active': True,
            }

    def generate_reading(self, sensor_id: str) -> Optional[SensorReading]:
        """Generate a sensor reading"""
        if sensor_id not in self.sensors:
            return None

        sensor = self.sensors[sensor_id]
        sensor_type = sensor['type']
        config = self.SENSOR_TYPES[sensor_type]

        # Generate value with seasonal variation
        hour = datetime.now(timezone.utc).hour
        day_of_year = datetime.now(timezone.utc).timetuple().tm_yday

        # Base value with seasonal pattern
        if sensor_type == 'air_temperature':
            # Hotter in summer, cooler in winter
            seasonal = 15 + 15 * (1 + __import__('math').sin(2 * __import__('math').pi * (day_of_year - 80) / 365)) / 2
            # Daily variation
            daily = 5 * __import__('math').sin(2 * __import__('math').pi * (hour - 6) / 24)
            base_value = seasonal + daily
        elif sensor_type == 'light_intensity':
            # Light follows sun
            if 6 <= hour <= 18:
                base_value = 50000 * __import__('math').sin(__import__('math').pi * (hour - 6) / 12)
            else:
                base_value = 0
        elif sensor_type == 'soil_moisture':
            # Moisture decreases during day
            base_value = 50 - 10 * __import__('math').sin(2 * __import__('math').pi * (hour - 6) / 24)
        else:
            # Random base value
            base_value = (config['min'] + config['max']) / 2

        # Add noise
        value = base_value + random.uniform(-config['noise'], config['noise'])
        value = max(config['min'], min(config['max'], value))

        # Quality score
        quality = random.uniform(0.85, 1.0)

        reading = SensorReading(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            value=round(value, 2),
            unit=config['unit'],
            timestamp=datetime.now(timezone.utc),
            latitude=sensor['latitude'],
            longitude=sensor['longitude'],
            quality=quality
        )

        self.readings.append(reading)
        return reading

    def generate_all_readings(self) -> List[SensorReading]:
        """Generate readings from all active sensors"""
        readings = []
        for sensor_id, sensor in self.sensors.items():
            if sensor['active']:
                reading = self.generate_reading(sensor_id)
                if reading:
                    readings.append(reading)
        return readings

    def get_sensor_status(self, sensor_id: str) -> Optional[Dict]:
        """Get sensor status"""
        return self.sensors.get(sensor_id)

    def get_all_sensors(self) -> List[Dict]:
        """Get all sensors"""
        return list(self.sensors.values())

    def get_recent_readings(self, hours: int = 24) -> List[SensorReading]:
        """Get readings from last N hours"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        return [r for r in self.readings if r.timestamp > cutoff]

    def get_statistics(self) -> Dict:
        """Get network statistics"""
        active_sensors = sum(1 for s in self.sensors.values() if s['active'])
        avg_battery = sum(s['battery'] for s in self.sensors.values()) / len(self.sensors) if self.sensors else 0

        return {
            'total_sensors': len(self.sensors),
            'active_sensors': active_sensors,
            'total_readings': len(self.readings),
            'avg_battery': round(avg_battery, 1),
            'sensor_types': len(set(s['type'] for s in self.sensors.values())),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    def simulate_growth(self, days: int = 30) -> List[Dict]:
        """Simulate plant growth over time"""
        growth_data = []
        base_ndvi = 0.3

        for day in range(days):
            # NDVI increases with growth
            ndvi = base_ndvi + (day / days) * 0.4
            ndvi += random.uniform(-0.02, 0.02)  # Noise

            growth_data.append({
                'day': day,
                'ndvi': round(ndvi, 3),
                'biomass_kg': round(10 + day * 2 + random.uniform(-1, 1), 2),
                'height_cm': round(5 + day * 1.5 + random.uniform(-0.5, 0.5), 2),
                'timestamp': (datetime.now(timezone.utc) - timedelta(days=days-day)).isoformat()
            })

        return growth_data


# Global simulator
_simulator = IoTSimulator()

def get_simulator() -> IoTSimulator:
    return _simulator

def reset_simulator(num_sensors: int = 10):
    global _simulator
    _simulator = IoTSimulator(num_sensors)
