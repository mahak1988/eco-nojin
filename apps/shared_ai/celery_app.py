"""
Celery Tasks for Background Processing
====================================
Asynchronous task processing for simulations and long-running operations.

Features:
- Task monitoring with Prometheus metrics
- Flower integration ready
- Error tracking and logging
- Background simulation processing
"""

import logging
from celery import Celery
from celery.signals import task_success, task_failure, task_prerun, task_postrun
from typing import Any, Optional

from apps.simulation.base import SimulationRegistry
from apps.shared_core.config import settings

logger = logging.getLogger("econojin")


# ==========================================
# Task Monitoring
# ==========================================
class TaskMonitor:
    """Monitor Celery task execution and metrics."""

    _tasks_running: int = 0
    _tasks_completed: int = 0
    _tasks_failed: int = 0

    @classmethod
    def get_stats(cls) -> dict:
        """Get current task statistics."""
        return {
            "tasks_running": cls._tasks_running,
            "tasks_completed": cls._tasks_completed,
            "tasks_failed": cls._tasks_failed,
        }

    @classmethod
    def reset_stats(cls) -> None:
        """Reset task statistics."""
        cls._tasks_running = 0
        cls._tasks_completed = 0
        cls._tasks_failed = 0


# Celery app instance
celery_app = Celery(
    "econojin",
    broker=settings.REDIS_URL or "redis://localhost:6379/0",
    backend=settings.REDIS_URL or "redis://localhost:6379/0",
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Tehran",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
)


# ==========================================
# Task Signal Handlers
# ==========================================
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
    """Increment running count before task starts."""
    TaskMonitor._tasks_running += 1
    logger.info(f"Task started: {task.name} (id={task_id})")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, **kwargs):
    """Decrement running count after task completes."""
    TaskMonitor._tasks_running -= 1


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """Increment completed count on success."""
    TaskMonitor._tasks_completed += 1
    logger.info(f"Task completed successfully: {sender.name}")


@task_failure.connect
def task_failure_handler(sender=None, exception=None, **kwargs):
    """Increment failed count on failure."""
    TaskMonitor._tasks_failed += 1
    logger.error(f"Task failed: {sender.name}, error: {str(exception)}")


@celery_app.task
def run_simulation_task(simulator_id: str, parameters: dict[str, Any]) -> dict:
    """Run a simulation in the background."""
    import asyncio

    sim_class = SimulationRegistry.get(simulator_id)
    if not sim_class:
        return {"error": f"Simulator '{simulator_id}' not found"}

    sim = sim_class()

    # Run async simulation in event loop
    result = asyncio.run(sim.run(parameters))

    return result.to_dict()


@celery_app.task
def get_weather_forecast_task(latitude: float, longitude: float, days: int = 7) -> dict:
    """Get weather forecast in the background."""
    # This would integrate with the climate simulator
    return {
        "latitude": latitude,
        "longitude": longitude,
        "days": days,
        "forecast": "pending_implementation",
    }


@celery_app.task
def send_notification_task(user_id: int, message: str, notification_type: str) -> dict:
    """Send notification to user asynchronously."""
    return {
        "user_id": user_id,
        "message": message,
        "type": notification_type,
        "status": "queued",
    }