"""Unit tests for IoT domain"""
import pytest
from datetime import datetime
from api.domains.iot.models.iot_models import (
    IoTDevice,
    SensorReading,
    AlertRule,
    SensorType,
    DeviceStatus
)
from api.domains.iot.services.alert_service import AlertService
from api.domains.iot.repositories.iot_repository import IoTRepository


class TestIoTModels:
    """تست‌های مدل‌های IoT"""
    
    def test_create_device(self):
        """تست ایجاد دستگاه"""
        device = IoTDevice(
            device_id="sensor_001",
            name="Soil Moisture Sensor 1",
            sensor_type=SensorType.SOIL_MOISTURE,
            location_lat=30.5,
            location_lon=51.5,
            pilot_site="dishmok"
        )
        
        assert device.device_id == "sensor_001"
        assert device.sensor_type == SensorType.SOIL_MOISTURE
        assert device.status == DeviceStatus.OFFLINE
    
    def test_create_reading(self):
        """تست ایجاد قرائت"""
        reading = SensorReading(
            reading_id="reading_001",
            device_id="sensor_001",
            timestamp=datetime.utcnow(),
            value=25.5,
            unit="percent"
        )
        
        assert reading.value == 25.5
        assert reading.quality == "good"
    
    def test_create_alert_rule(self):
        """تست ایجاد قانون هشدار"""
        rule = AlertRule(
            rule_id="rule_001",
            name="Low Soil Moisture",
            sensor_type=SensorType.SOIL_MOISTURE,
            threshold_min=20.0,
            severity="warning"
        )
        
        assert rule.threshold_min == 20.0
        assert rule.severity == "warning"
        assert rule.enabled == True


class TestAlertService:
    """تست‌های سرویس هشدار"""
    
    def test_evaluate_reading_below_threshold(self):
        """تست ارزیابی قرائت زیر آستانه"""
        repo = IoTRepository()
        service = AlertService(repo)
        
        # ایجاد قرائت
        reading = SensorReading(
            reading_id="reading_001",
            device_id="sensor_001",
            timestamp=datetime.utcnow(),
            value=15.0,
            unit="percent"
        )
        
        # ارزیابی (بدون قوانین، نباید هشداری تولید شود)
        alerts = service.evaluate_reading(reading)
        assert isinstance(alerts, list)
    
    def test_check_drought_conditions_no_data(self):
        """تست بررسی خشکسالی بدون داده"""
        repo = IoTRepository()
        service = AlertService(repo)
        
        result = service.check_drought_conditions("dishmok")
        assert result['status'] == 'NO_DATA'
    
    def test_check_flood_risk_no_data(self):
        """تست بررسی ریسک سیلاب بدون داده"""
        repo = IoTRepository()
        service = AlertService(repo)
        
        result = service.check_flood_risk("dishmok")
        assert result['status'] == 'NO_DATA'
    
    def test_generate_daily_report(self):
        """تست تولید گزارش روزانه"""
        repo = IoTRepository()
        service = AlertService(repo)
        
        report = service.generate_daily_report("dishmok")
        
        assert 'pilot_site' in report
        assert 'devices' in report
        assert 'drought_status' in report
        assert 'flood_risk' in report
        assert report['pilot_site'] == 'dishmok'
