"""Celery application — Redis broker when available, else solo/memory for local."""

from __future__ import annotations

import os

from celery import Celery

REDIS_URL = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"

celery_app = Celery(
    "econojin",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["apps.simulation.tasks"],
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
)
