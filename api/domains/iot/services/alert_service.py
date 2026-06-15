"""Early Warning System Service

این سرویس سیستم هشدار زودهنگام برای پایش شرایط بحرانی را پیاده‌سازی می‌کند.
"""
from typing import List, Dict, Optional
from datetime import datetime
from .models.iot_models import SensorReading, AlertRule, Alert, SensorType
from .repositories.iot_repository import IoTRepository
import uuid


class AlertService:
    """سرویس مدیریت هشدارها و سیستم هشدار زودهنگام"""
    
    def __init__(self, repository: IoTRepository):
        self.repo = repository
    
    def evaluate_reading(self, reading: SensorReading) -> List[Alert]:
        """ارزیابی یک قرائت و تولید هشدار در صورت نیاز"""
        alerts = []
        
        # دریافت قوانین هشدار برای این نوع حسگر
        rules = self.repo.get_alert_rules(reading.unit)
        
        for rule in rules:
            if not rule.enabled:
                continue
            
            # بررسی آستانه‌ها
            if rule.threshold_min is not None and reading.value < rule.threshold_min:
                alert = self._create_alert(
                    rule=rule,
                    reading=reading,
                    threshold=rule.threshold_min,
                    message=f"مقدار {reading.value} {reading.unit} کمتر از آستانه minimum {rule.threshold_min}"
                )
                alerts.append(alert)
            
            if rule.threshold_max is not None and reading.value > rule.threshold_max:
                alert = self._create_alert(
                    rule=rule,
                    reading=reading,
                    threshold=rule.threshold_max,
                    message=f"مقدار {reading.value} {reading.unit} بیشتر از آستانه maximum {rule.threshold_max}"
                )
                alerts.append(alert)
        
        return alerts
    
    def _create_alert(
        self,
        rule: AlertRule,
        reading: SensorReading,
        threshold: float,
        message: str
    ) -> Alert:
        """ایجاد یک هشدار"""
        return Alert(
            alert_id=str(uuid.uuid4()),
            rule_id=rule.rule_id,
            device_id=reading.device_id,
            reading_id=reading.reading_id,
            timestamp=datetime.utcnow(),
            severity=rule.severity,
            message=message,
            value=reading.value,
            threshold=threshold
        )
    
    def check_drought_conditions(
        self,
        pilot_site: str,
        soil_moisture_threshold: float = 20.0,
        days_without_rain: int = 30
    ) -> Dict:
        """بررسی شرایط خشکسالی"""
        # دریافت قرائت‌های رطوبت خاک
        devices = self.repo.get_devices_by_pilot(pilot_site)
        moisture_devices = [d for d in devices if d.sensor_type == SensorType.SOIL_MOISTURE]
        
        if not moisture_devices:
            return {'status': 'NO_DATA', 'message': 'داده رطوبت خاک موجود نیست'}
        
        # محاسبه میانگین رطوبت
        total_moisture = 0.0
        count = 0
        
        for device in moisture_devices:
            latest = self.repo.get_latest_reading(device.device_id)
            if latest:
                total_moisture += latest.value
                count += 1
        
        if count == 0:
            return {'status': 'NO_DATA', 'message': 'قرائت جدید موجود نیست'}
        
        avg_moisture = total_moisture / count
        
        # ارزیابی شرایط
        if avg_moisture < soil_moisture_threshold * 0.5:
            severity = 'CRITICAL'
            status = 'EXTREME_DROUGHT'
        elif avg_moisture < soil_moisture_threshold:
            severity = 'WARNING'
            status = 'MODERATE_DROUGHT'
        else:
            severity = 'INFO'
            status = 'NORMAL'
        
        return {
            'pilot_site': pilot_site,
            'status': status,
            'severity': severity,
            'average_soil_moisture': round(avg_moisture, 2),
            'threshold': soil_moisture_threshold,
            'devices_count': count,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def check_flood_risk(
        self,
        pilot_site: str,
        water_level_threshold: float = 80.0
    ) -> Dict:
        """بررسی ریسک سیلاب"""
        devices = self.repo.get_devices_by_pilot(pilot_site)
        water_devices = [d for d in devices if d.sensor_type == SensorType.WATER_LEVEL]
        
        if not water_devices:
            return {'status': 'NO_DATA', 'message': 'داده سطح آب موجود نیست'}
        
        max_level = 0.0
        critical_device = None
        
        for device in water_devices:
            latest = self.repo.get_latest_reading(device.device_id)
            if latest and latest.value > max_level:
                max_level = latest.value
                critical_device = device.device_id
        
        if max_level > water_level_threshold:
            severity = 'CRITICAL'
            status = 'FLOOD_WARNING'
        elif max_level > water_level_threshold * 0.8:
            severity = 'WARNING'
            status = 'HIGH_WATER_LEVEL'
        else:
            severity = 'INFO'
            status = 'NORMAL'
        
        return {
            'pilot_site': pilot_site,
            'status': status,
            'severity': severity,
            'max_water_level': round(max_level, 2),
            'threshold': water_level_threshold,
            'critical_device': critical_device,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def generate_daily_report(self, pilot_site: str) -> Dict:
        """تولید گزارش روزانه برای یک پایلوت"""
        devices = self.repo.get_devices_by_pilot(pilot_site)
        
        online_count = sum(1 for d in devices if d.status.value == 'online')
        offline_count = len(devices) - online_count
        
        # بررسی شرایط خاص
        drought_check = self.check_drought_conditions(pilot_site)
        flood_check = self.check_flood_risk(pilot_site)
        
        return {
            'pilot_site': pilot_site,
            'date': datetime.utcnow().date().isoformat(),
            'devices': {
                'total': len(devices),
                'online': online_count,
                'offline': offline_count
            },
            'drought_status': drought_check,
            'flood_risk': flood_check,
            'active_alerts': len(self.repo.get_active_alerts(pilot_site)),
            'generated_at': datetime.utcnow().isoformat()
        }
