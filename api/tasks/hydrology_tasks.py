"""Hydrology Async Tasks

وظایف ناهمزمان مربوط به شبیه‌سازی‌های هیدرولوژیک.
"""
from celery import shared_task
from datetime import datetime, timezone
import time


@shared_task(bind=True, max_retries=2, time_limit=7200)
def run_swat_simulation(self, watershed_id: str, scenario_name: str):
    """اجرای شبیه‌سازی SWAT به‌صورت ناهمزمان"""
    try:
        # شبیه‌سازی اجرای SWAT (معمولاً چندین دقیقه تا ساعت)
        time.sleep(10)
        
        result = {
            "watershed_id": watershed_id,
            "scenario_name": scenario_name,
            "status": "completed",
            "runoff_monthly": [45.2, 38.5, 52.1, 65.3, 78.9, 92.4, 85.6, 72.3, 58.7, 45.2, 38.9, 42.1],
            "baseflow_monthly": [12.5, 11.8, 13.2, 15.6, 18.9, 22.4, 20.6, 17.3, 14.7, 12.2, 11.9, 12.1],
            "evapotranspiration_monthly": [25.3, 28.5, 35.2, 42.3, 48.9, 55.4, 58.6, 52.3, 42.7, 32.2, 28.9, 25.1],
            "water_balance": {
                "precipitation_mm": 650.5,
                "runoff_mm": 715.2,
                "evapotranspiration_mm": 475.4,
                "recharge_mm": 125.8
            },
            "simulation_date": datetime.now(timezone.utc).isoformat()
        }
        
        return result
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2)
def run_weap_allocation(self, watershed_id: str, scenario_name: str):
    """اجرای تخصیص آب WEAP به‌صورت ناهمزمان"""
    try:
        time.sleep(8)
        
        result = {
            "watershed_id": watershed_id,
            "scenario_name": scenario_name,
            "status": "completed",
            "allocations": {
                "agriculture": [85.2, 82.5, 88.1, 92.3, 95.9, 98.4],
                "domestic": [45.5, 46.8, 47.2, 48.3, 49.9, 51.4],
                "industrial": [25.2, 26.5, 27.1, 28.3, 29.9, 31.4],
                "environmental": [15.5, 16.8, 17.2, 18.3, 19.9, 21.4]
            },
            "performance_indicators": {
                "reliability": 0.87,
                "vulnerability": 0.12,
                "resilience": 0.78
            },
            "simulation_date": datetime.now(timezone.utc).isoformat()
        }
        
        return result
    except Exception as exc:
        raise self.retry(exc=exc)
