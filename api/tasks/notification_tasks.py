"""Notification Async Tasks

وظایف ناهمزمان مربوط به ارسال اعلان‌ها.
"""
from celery import shared_task
from datetime import datetime, timezone
import time


@shared_task
def send_alert_notification(user_id: str, alert_type: str, message: str):
    """ارسال اعلان هشدار"""
    time.sleep(1)
    
    return {
        "user_id": user_id,
        "alert_type": alert_type,
        "message": message,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "status": "sent"
    }


@shared_task
def send_daily_report(pilot_site: str, recipients: list):
    """ارسال گزارش روزانه"""
    time.sleep(2)
    
    return {
        "pilot_site": pilot_site,
        "recipients_count": len(recipients),
        "report_date": datetime.now(timezone.utc).date().isoformat(),
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "status": "sent"
    }
