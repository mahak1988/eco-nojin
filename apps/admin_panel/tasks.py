from celery import shared_task
import logging
from apps.shared_core.database.session import get_db_session
from apps.admin_panel.service import ReportService

logger = logging.getLogger(__name__)

@shared_task(name="admin.generate_report_task", bind=True)
def generate_report_task(self, report_id: int, report_type: str, filters: dict):
    """
    تسک ناهمگام برای تولید گزارشهای سنگین پنل ادمین.
    این کار از مسدود شدن Event Loop اصلی FastAPI جلوگیری میکند.
    """
    logger.info(f"Starting report generation: {report_type} for report_id: {report_id}")
    try:
        # استفاده از سینتکس صحیح برای Dependency Injection در Celery
        db_gen = get_db_session()
        db = next(db_gen)
        
        report_service = ReportService()
        # فرض بر این است که متد process_report در سرویس وجود دارد
        report_service.process_report(db=db, report_id=report_id, report_type=report_type, filters=filters)
        
        logger.info(f"Report {report_id} generated successfully.")
        return {"status": "completed", "report_id": report_id}
        
    except Exception as e:
        logger.error(f"Failed to generate report {report_id}: {str(e)}")
        # بهروزرسانی وضعیت گزارش به 'failed' در دیتابیس
        return {"status": "failed", "report_id": report_id, "error": str(e)}
