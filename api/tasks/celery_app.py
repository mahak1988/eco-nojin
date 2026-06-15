"""Celery Configuration for Async Tasks

این ماژول پیکربندی Celery را برای پردازش ناهمزمان وظایف سنگین
مانند محاسبات MRV، شبیه‌سازی‌های هیدرولوژیک و پردازش تصاویر ماهواره‌ای فراهم می‌کند.
"""
from celery import Celery
import os


# Create Celery app
celery_app = Celery(
    'econojin',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
)

# Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_routes={
        'api.tasks.mrv_tasks.*': {'queue': 'mrv'},
        'api.tasks.hydrology_tasks.*': {'queue': 'hydrology'},
        'api.tasks.remote_sensing_tasks.*': {'queue': 'remote_sensing'},
        'api.tasks.notification_tasks.*': {'queue': 'notifications'},
    }
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['api.tasks'])
