"""Celery application — Redis broker when available."""

from __future__ import annotations

import os

from celery import Celery

REDIS_URL = (
    os.getenv("CELERY_BROKER_URL")
    or os.getenv("REDIS_URL")
    or "redis://localhost:6379/0"
)

celery_app = Celery(
    "econojin",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["apps.simulation.tasks", "apps.satellite.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "weekly-vegetation-check": {
            "task": "satellite.weekly_vegetation_check",
            "schedule": 60 * 60 * 24 * 7,  # seconds; override with crontab in prod
        },
    },
)

# Register weekly task name if defined
try:
    from apps.satellite.tasks import weekly_vegetation_check_sync

    @celery_app.task(name="satellite.weekly_vegetation_check")
    def weekly_vegetation_check() -> dict:
        return weekly_vegetation_check_sync()

except Exception:
    pass
