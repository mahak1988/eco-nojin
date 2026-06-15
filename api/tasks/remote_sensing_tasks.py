"""Remote Sensing Async Tasks

وظایف ناهمزمان مربوط به پردازش تصاویر ماهواره‌ای.
"""
from celery import shared_task
from datetime import datetime, timezone
import time


@shared_task(bind=True, max_retries=3)
def process_sentinel2_image(self, image_id: str, pilot_site: str):
    """پردازش تصویر Sentinel-2 به‌صورت ناهمزمان"""
    try:
        # شبیه‌سازی پردازش تصویر (معمولاً چندین دقیقه)
        time.sleep(15)
        
        result = {
            "image_id": image_id,
            "pilot_site": pilot_site,
            "status": "completed",
            "ndvi_statistics": {
                "mean": 0.45,
                "min": 0.12,
                "max": 0.78,
                "std": 0.15
            },
            "ndwi_statistics": {
                "mean": 0.22,
                "min": -0.15,
                "max": 0.65,
                "std": 0.18
            },
            "vegetation_health": {
                "very_poor_percent": 5.2,
                "poor_percent": 12.8,
                "fair_percent": 25.5,
                "good_percent": 38.5,
                "very_good_percent": 18.0
            },
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        
        return result
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def calculate_ndvi_timeseries(pilot_site: str, start_date: str, end_date: str):
    """محاسبه سری زمانی NDVI"""
    time.sleep(20)
    
    return {
        "pilot_site": pilot_site,
        "start_date": start_date,
        "end_date": end_date,
        "timeseries": [
            {"date": "2024-01-01", "mean_ndvi": 0.32},
            {"date": "2024-02-01", "mean_ndvi": 0.35},
            {"date": "2024-03-01", "mean_ndvi": 0.38},
            {"date": "2024-04-01", "mean_ndvi": 0.42},
            {"date": "2024-05-01", "mean_ndvi": 0.45},
            {"date": "2024-06-01", "mean_ndvi": 0.48}
        ],
        "trend": "improving",
        "calculated_at": datetime.now(timezone.utc).isoformat()
    }
