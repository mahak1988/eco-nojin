"""MRV Async Tasks

وظایف ناهمزمان مربوط به محاسبات MRV و اعتبارات کربن.
"""
from celery import shared_task
from datetime import datetime, timezone
import time


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def calculate_mrv_report(self, project_id: str, pilot_site: str):
    """محاسبه گزارش MRV به‌صورت ناهمزمان"""
    try:
        # شبیه‌سازی محاسبه سنگین
        time.sleep(5)
        
        result = {
            "project_id": project_id,
            "pilot_site": pilot_site,
            "status": "completed",
            "soc_change_tCO2": 150.5,
            "biomass_sequestration_tCO2": 75.2,
            "n2o_emissions_tCO2e": 12.3,
            "ch4_emissions_tCO2e": 8.7,
            "net_carbon_balance_tCO2e": 204.7,
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
        
        return result
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3)
def issue_carbon_credits(self, project_id: str, volume_tCO2e: float):
    """صدور اعتبارات کربن به‌صورت ناهمزمان"""
    try:
        # شبیه‌سازی ارتباط با بلاکچین
        time.sleep(3)
        
        result = {
            "project_id": project_id,
            "volume_tCO2e": volume_tCO2e,
            "credits_issued": int(volume_tCO2e),
            "blockchain_tx_hash": "0x" + "a" * 64,
            "status": "issued",
            "issued_at": datetime.now(timezone.utc).isoformat()
        }
        
        return result
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def generate_mrv_certificate(project_id: str, report_id: str):
    """تولید گواهی MRV"""
    time.sleep(2)
    
    return {
        "certificate_id": f"MRV-{project_id}-{report_id}",
        "project_id": project_id,
        "report_id": report_id,
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "valid_until": "2030-12-31T23:59:59Z"
    }
