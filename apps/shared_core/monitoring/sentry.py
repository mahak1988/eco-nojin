"""
Sentry Monitoring Integration
============================
Error tracking and performance monitoring for Econojin backend.
"""

import os
from typing import Optional

# Sentry SDK import with fallback
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.asyncio import AsyncioIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


def init_sentry(app) -> None:
    """Initialize Sentry for error tracking and performance monitoring."""
    dsn = os.getenv("SENTRY_DSN")
    if not dsn or not SENTRY_AVAILABLE:
        return

    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            AsyncioIntegration(),
        ],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_RATE", "0.1")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_RATE", "0.1")),
        environment=os.getenv("ENVIRONMENT", "production"),
        release=os.getenv("APP_VERSION", "1.0.0"),
    )
    
    # Add Sentry middleware to FastAPI app
    from sentry_sdk.integrations.starlette import SentryAsgiMiddleware
    app.add_middleware(SentryAsgiMiddleware)


def capture_exception(exc: Exception, context: Optional[dict] = None) -> None:
    """Capture an exception with optional context."""
    if SENTRY_AVAILABLE:
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_extra(key, value)
            sentry_sdk.capture_exception(exc)


def capture_message(message: str, level: str = "info") -> None:
    """Capture a message at the specified level."""
    if SENTRY_AVAILABLE:
        sentry_sdk.capture_message(message, level=level)