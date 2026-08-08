"""Celery application — optional.

If `celery` is not installed (common on Zero-Install local), provide a no-op
stub so simulation routers still load and run_*_local sync paths work.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"

CELERY_AVAILABLE = False
celery_app: Any = None


class _StubTask:
    """Minimal stand-in for celery Task / decorated function."""

    def __init__(self, fn: Callable[..., Any], name: str = "") -> None:
        self._fn = fn
        self.name = name

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._fn(*args, **kwargs)

    def delay(self, *args: Any, **kwargs: Any) -> Any:
        class _Result:
            id = "sync-local"

            def get(self, *a: Any, **k: Any) -> Any:
                return self._fn(*args, **kwargs)

            def __init__(self, fn: Callable[..., Any], a: tuple, kw: dict) -> None:
                self._fn = fn
                self._a = a
                self._kw = kw

            def get(self, *a: Any, **k: Any) -> Any:  # noqa: F811
                return self._fn(*self._a, **self._kw)

        return _Result(self._fn, args, kwargs)

    def apply_async(self, args: Any = None, kwargs: Any = None, **_: Any) -> Any:
        return self.delay(*(args or ()), **(kwargs or {}))


class _StubCelery:
    def __init__(self) -> None:
        self.conf = type("c", (), {"update": lambda *a, **k: None})()

    def task(self, *dargs: Any, **dkwargs: Any) -> Callable[[Callable[..., Any]], _StubTask]:
        name = dkwargs.get("name", "")

        def decorator(fn: Callable[..., Any]) -> _StubTask:
            # Support bind=True tasks: first arg is self
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


try:
    from celery import Celery

    celery_app = Celery(
        "econojin",
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=[
            "apps.simulation.tasks",
            "apps.simulation.tasks_phase3",
            "apps.satellite.tasks",
        ],
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
                "schedule": 60 * 60 * 24 * 7,
            },
        },
    )
    CELERY_AVAILABLE = True

    try:
        from apps.satellite.tasks import weekly_vegetation_check_sync

        @celery_app.task(name="satellite.weekly_vegetation_check")
        def weekly_vegetation_check() -> dict:
            return weekly_vegetation_check_sync()

    except Exception:
        pass

except ImportError:
    logger.warning("celery not installed — using sync stub (Zero-Install mode)")
    celery_app = _StubCelery()
    CELERY_AVAILABLE = False
