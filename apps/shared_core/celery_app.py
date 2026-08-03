"""Celery application — production-grade with Redis backend and structured logging."""

from __future__ import annotations

import logging
import os
from typing import Any, Callable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
REDIS_URL = (
    os.getenv("CELERY_BROKER_URL")
    or os.getenv("REDIS_URL")
    or "redis://localhost:6379/0"
)

RESULT_BACKEND = (
    os.getenv("CELERY_RESULT_BACKEND")
    or os.getenv("REDIS_URL")
    or "redis://localhost:6379/0"
)

CELERY_AVAILABLE = False
celery_app: Any = None


# ---------------------------------------------------------------------------
# Stub classes for Zero-Install (no Celery installed)
# ---------------------------------------------------------------------------
class _StubTask:
    """Minimal stand-in for celery Task / decorated function."""

    def __init__(self, fn: Callable[..., Any], name: str = "") -> None:
        self._fn = fn
        self.name = name

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._fn(*args, **kwargs)

    def delay(self, *args: Any, **kwargs: Any) -> Any:
        class _Result:
            def __init__(self, fn: Callable[..., Any], a: tuple, kw: dict) -> None:
                self._fn = fn
                self._a = a
                self._kw = kw

            def get(self, *a: Any, **k: Any) -> Any:
                return self._fn(*self._a, **self._kw)

            @property
            def id(self) -> str:
                return "sync-local"

            @property
            def state(self) -> str:
                return "SUCCESS"

            def ready(self) -> bool:
                return True

            def successful(self) -> bool:
                return True

            def failed(self) -> bool:
                return False

        return _Result(self._fn, args, kwargs)

    def apply_async(self, args: Any = None, kwargs: Any = None, **_: Any) -> Any:
        return self.delay(*(args or ()), **(kwargs or {}))

    def s(self, *args: Any, **kwargs: Any) -> "_StubTask":
        """Signature support for chaining."""
        return _StubTask(lambda *a, **kw: self._fn(*(args + a), **{**kwargs, **kw}), name=self.name)


class _StubCelery:
    """No-op Celery stub for local development without Redis."""

    def __init__(self) -> None:
        self.conf = type("c", (), {"update": lambda *a, **k: None})()

    def task(self, *dargs: Any, **dkwargs: Any) -> Callable[[Callable[..., Any]], _StubTask]:
        name = dkwargs.get("name", "")

        def decorator(fn: Callable[..., Any]) -> _StubTask:
            if dkwargs.get("bind"):

                def wrapper(*args: Any, **kwargs: Any) -> Any:
                    class _Req:
                        id = "sync-local"

                    class _Self:
                        request = _Req()

                    return fn(_Self(), *args, **kwargs)

                return _StubTask(wrapper, name=name)
            return _StubTask(fn, name=name)

        return decorator

    def send_task(self, name: str, args: Any = None, kwargs: Any = None, **_: Any) -> Any:
        logger.debug("Stub send_task: %s", name)
        return None

    @property
    def tasks(self) -> dict:
        return {}


# ---------------------------------------------------------------------------
# Real Celery setup
# ---------------------------------------------------------------------------
try:
    from celery import Celery
    from celery.signals import after_setup_logger, after_setup_task_logger

    celery_app = Celery(
        "econojin",
        broker=REDIS_URL,
        backend=RESULT_BACKEND,
        include=[
            "apps.simulation.tasks",
            "apps.simulation.tasks_phase3",
            "apps.satellite.tasks",
        ],
    )

    # -------------------------------------------------------------------
    # Celery Configuration
    # -------------------------------------------------------------------
    celery_app.conf.update(
        # Serialization
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        # Time
        timezone="UTC",
        enable_utc=True,
        # Task execution
        task_track_started=True,
        task_time_limit=int(os.getenv("CELERY_TASK_TIME_LIMIT", "1800")),  # 30 min default
        task_soft_time_limit=int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT", "1500")),  # 25 min
        task_acks_late=True,  # Re-deliver on worker crash
        task_reject_on_worker_lost=True,  # Reject tasks when worker dies
        # Worker
        worker_prefetch_multiplier=1,  # Fair distribution
        worker_max_tasks_per_child=int(os.getenv("CELERY_MAX_TASKS_PER_CHILD", "100")),
        worker_max_memory_per_child=int(os.getenv("CELERY_MAX_MEMORY_PER_CHILD", "256000")),  # 256 MB
        worker_concurrency=int(os.getenv("CELERY_CONCURRENCY", "4")),
        # Result backend
        result_expires=int(os.getenv("CELERY_RESULT_EXPIRES", "86400")),  # 24 hours
        result_extended=True,  # Store extended task metadata
        # Broker
        broker_connection_retry_on_startup=True,
        broker_connection_retry=True,
        broker_connection_max_retries=10,
        broker_pool_limit=10,
        # Redis transport
        redis_socket_connect_timeout=5,
        redis_socket_timeout=10,
        redis_max_connections=int(os.getenv("CELERY_REDIS_MAX_CONNS", "50")),
        # Rate limiting
        worker_disable_rate_limits=False,
        task_default_rate_limit=os.getenv("CELERY_DEFAULT_RATE_LIMIT", "100/m"),
        # Events
        worker_send_task_events=True,
        task_send_sent_event=True,
        # Optimization
        task_compression="gzip",
        result_compression="gzip",
        task_store_errors_even_if_ignored=True,
    )

    # -------------------------------------------------------------------
    # Beat schedule (periodic tasks)
    # -------------------------------------------------------------------
    celery_app.conf.beat_schedule = {
        "weekly-vegetation-check": {
            "task": "satellite.weekly_vegetation_check",
            "schedule": 60 * 60 * 24 * 7,  # Every 7 days
            "options": {
                "expires": 60 * 60 * 24,  # Expire after 24h if not consumed
            },
        },
        "cleanup-expired-tokens": {
            "task": "shared_core.cleanup_expired_tokens",
            "schedule": 60 * 60 * 6,  # Every 6 hours
            "options": {
                "expires": 3600,
            },
        },
        "health-check-db": {
            "task": "shared_core.health_check_database",
            "schedule": 60 * 60,  # Every hour
            "options": {
                "expires": 600,
            },
        },
    }

    # -------------------------------------------------------------------
    # Signal handlers — structured logging integration
    # -------------------------------------------------------------------
    @after_setup_logger.connect
    def setup_celery_logger(logger_instance, **kwargs):  # noqa: ARG001
        """Inject structured logging into Celery logger."""
        try:
            from apps.shared_core.logging_config import configure_celery_logging

            configure_celery_logging(logger_instance)
        except ImportError:
            pass

    @after_setup_task_logger.connect
    def setup_celery_task_logger(logger_instance, **kwargs):  # noqa: ARG001
        """Inject structured logging into Celery task logger."""
        try:
            from apps.shared_core.logging_config import configure_celery_task_logging

            configure_celery_task_logging(logger_instance)
        except ImportError:
            pass

    # -------------------------------------------------------------------
    # Register built-in tasks
    # -------------------------------------------------------------------
    @celery_app.task(
        name="shared_core.cleanup_expired_tokens",
        bind=True,
        autoretry_for=(Exception,),
        retry_backoff=True,
        max_retries=3,
    )
    def cleanup_expired_tokens(self) -> dict:
        """Remove expired refresh tokens from the database."""
        from apps.shared_core.database.session import get_engine

        import asyncio

        async def _cleanup():
            from sqlalchemy import text

            eng = get_engine()
            async with eng.begin() as conn:
                result = await conn.execute(
                    text("DELETE FROM refresh_tokens WHERE expires_at < NOW()")
                )
                logger.info("Cleaned up %d expired tokens", result.rowcount)
                return {"cleaned": result.rowcount}

        return asyncio.get_event_loop().run_until_complete(_cleanup())

    @celery_app.task(
        name="shared_core.health_check_database",
        bind=True,
        autoretry_for=(Exception,),
        retry_backoff=True,
        max_retries=2,
    )
    def health_check_database(self) -> dict:
        """Periodic database health check."""
        from apps.shared_core.database.session import get_engine

        import asyncio

        async def _check():
            from sqlalchemy import text

            eng = get_engine()
            async with eng.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                return {"ok": result.scalar() == 1, "timestamp": str(result.scalar())}

        return asyncio.get_event_loop().run_until_complete(_check())

    # Register satellite task
    try:
        from apps.satellite.tasks import weekly_vegetation_check_sync

        @celery_app.task(name="satellite.weekly_vegetation_check")
        def weekly_vegetation_check() -> dict:
            return weekly_vegetation_check_sync()

    except Exception:
        pass

    CELERY_AVAILABLE = True
    logger.info(
        "Celery ready: broker=%s concurrency=%s",
        REDIS_URL.split("@")[-1] if "@" in REDIS_URL else REDIS_URL,
        celery_app.conf.worker_concurrency,
    )

except ImportError:
    logger.warning("celery not installed — using sync stub (Zero-Install mode)")
    celery_app = _StubCelery()
    CELERY_AVAILABLE = False
