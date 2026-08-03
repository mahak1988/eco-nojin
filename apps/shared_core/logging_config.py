"""Structured logging configuration — JSON format for production, rotation support."""

from __future__ import annotations

import logging
import logging.config
import logging.handlers
import os
import sys
from datetime import datetime, timezone
from typing import Any, Optional

# ---------------------------------------------------------------------------
# JSON Log Formatter
# ---------------------------------------------------------------------------


class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter for machine-readable logs."""

    def __init__(
        self,
        service_name: str = "econojin",
        environment: str = "production",
    ) -> None:
        self.service_name = service_name
        self.environment = environment
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        import json

        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "service": self.service_name,
            "environment": self.environment,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        # Context from extra fields (structlog-style)
        extra_fields = getattr(record, "_structured_fields", {})
        if isinstance(extra_fields, dict):
            log_entry.update(extra_fields)

        # Exception info
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = {
                "type": type(record.exc_info[1]).__name__,
                "message": str(record.exc_info[1]),
            }

        # Request context (FastAPI)
        request_id = getattr(record, "request_id", None)
        if request_id:
            log_entry["request_id"] = request_id

        client_ip = getattr(record, "client_ip", None)
        if client_ip:
            log_entry["client_ip"] = client_ip

        # Duration
        duration_ms = getattr(record, "duration_ms", None)
        if duration_ms is not None:
            log_entry["duration_ms"] = duration_ms

        return json.dumps(log_entry, ensure_ascii=False, default=str)


# ---------------------------------------------------------------------------
# Rotation file handler factory
# ---------------------------------------------------------------------------


def _rotating_file_handler(
    log_file: str,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 10,
    formatter: Optional[logging.Formatter] = None,
) -> logging.Handler:
    """Create a rotating file handler."""
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    if formatter:
        handler.setFormatter(formatter)
    return handler


def _timed_rotating_file_handler(
    log_file: str,
    when: str = "midnight",
    interval: int = 1,
    backup_count: int = 30,
    formatter: Optional[logging.Formatter] = None,
) -> logging.Handler:
    """Create a time-rotating file handler (daily rotation, 30-day retention)."""
    handler = logging.handlers.TimedRotatingFileHandler(
        log_file,
        when=when,
        interval=interval,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.suffix = "%Y-%m-%d"
    if formatter:
        handler.setFormatter(formatter)
    return handler


# ---------------------------------------------------------------------------
# Main configuration
# ---------------------------------------------------------------------------


def get_log_config(
    *,
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None,
    service_name: str = "econojin",
    environment: str = "production",
) -> dict[str, Any]:
    """Build a complete logging configuration dict.

    Args:
        log_level: Root log level (DEBUG, INFO, WARNING, ERROR)
        log_format: "json" for structured or "text" for human-readable
        log_file: Optional path for file-based logging with rotation
        service_name: Service identifier in logs
        environment: Deployment environment
    """
    is_json = log_format == "json"

    # Formatter
    if is_json:
        formatter = JsonFormatter(
            service_name=service_name,
            environment=environment,
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

    handlers: dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "json" if is_json else "text",
            "level": log_level,
        },
    }

    if log_file:
        # Ensure directory exists
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)

        handlers["file"] = {
            "()": _timed_rotating_file_handler,
            "log_file": log_file,
            "when": "midnight",
            "interval": 1,
            "backup_count": 30,
            "formatter": formatter,
        }

        handlers["error_file"] = {
            "()": _timed_rotating_file_handler,
            "log_file": log_file.replace(".log", ".error.log"),
            "when": "midnight",
            "interval": 1,
            "backup_count": 30,
            "formatter": formatter,
        }

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JsonFormatter,
                "service_name": service_name,
                "environment": environment,
            },
            "text": {
                "format": "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
        },
        "handlers": handlers,
        "loggers": {
            # Root logger
            "": {
                "handlers": list(handlers.keys()),
                "level": log_level,
                "propagate": False,
            },
            # Application loggers
            "apps": {
                "handlers": list(handlers.keys()),
                "level": log_level,
                "propagate": False,
            },
            "econojin": {
                "handlers": list(handlers.keys()),
                "level": log_level,
                "propagate": False,
            },
            # Third-party noise reduction
            "uvicorn": {
                "handlers": list(handlers.keys()),
                "level": os.getenv("UVICORN_LOG_LEVEL", "INFO"),
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": list(handlers.keys()),
                "level": os.getenv("UVICORN_ACCESS_LOG_LEVEL", "WARNING"),
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": list(handlers.keys()),
                "level": "WARNING",
                "propagate": False,
            },
            "sqlalchemy.pool": {
                "handlers": list(handlers.keys()),
                "level": "INFO",
                "propagate": False,
            },
            "celery": {
                "handlers": list(handlers.keys()),
                "level": log_level,
                "propagate": False,
            },
            "celery.beat": {
                "handlers": list(handlers.keys()),
                "level": log_level,
                "propagate": False,
            },
            # Library noise reduction
            "aiosqlite": {"handlers": [], "level": "WARNING", "propagate": False},
            "asyncio": {"handlers": [], "level": "WARNING", "propagate": False},
            "httpx": {"handlers": [], "level": "WARNING", "propagate": False},
            "httpcore": {"handlers": [], "level": "WARNING", "propagate": False},
            "urllib3": {"handlers": [], "level": "WARNING", "propagate": False},
            "botocore": {"handlers": [], "level": "WARNING", "propagate": False},
        },
    }

    # Error-only file handler
    if log_file:
        error_handlers = ["console"]
        if "file" in handlers:
            error_handlers.append("error_file")
        config["loggers"]["apps"]["handlers"] = error_handlers
        config["loggers"]["econojin"]["handlers"] = error_handlers

    return config


# ---------------------------------------------------------------------------
# Application bootstrap
# ---------------------------------------------------------------------------


def configure_logging(
    *,
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
    service_name: str = "econojin",
    environment: Optional[str] = None,
) -> None:
    """Configure application-wide structured logging.

    Called once during application startup (main.py lifespan).
    Reads from settings if arguments are not provided.

    Args:
        log_level: Override log level
        log_format: "json" or "text"
        log_file: Path to log file (triggers rotation)
        service_name: Service identity
        environment: Deployment environment
    """
    try:
        from apps.shared_core.config import settings

        log_level = log_level or settings.LOG_LEVEL
        log_format = log_format or settings.LOG_FORMAT
        log_file = log_file or settings.LOG_FILE
        environment = environment or settings.ENVIRONMENT
    except Exception:
        log_level = log_level or os.getenv("LOG_LEVEL", "INFO")
        log_format = log_format or os.getenv("LOG_FORMAT", "json")
        log_file = log_file or os.getenv("LOG_FILE", "logs/app.log")
        environment = environment or os.getenv("ENVIRONMENT", "production")

    config = get_log_config(
        log_level=log_level,
        log_format=log_format,
        log_file=log_file,
        service_name=service_name,
        environment=environment,
    )

    logging.config.dictConfig(config)

    logger = logging.getLogger("econojin")
    logger.info(
        "Logging configured: format=%s level=%s file=%s env=%s",
        log_format,
        log_level,
        log_file or "stdout-only",
        environment,
    )


def configure_celery_logging(logger_instance: logging.Logger) -> None:
    """Configure Celery workers for structured logging."""
    log_format = os.getenv("LOG_FORMAT", "json")

    # Remove existing handlers
    for handler in list(logger_instance.handlers):
        logger_instance.removeHandler(handler)

    if log_format == "json":
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            JsonFormatter(
                service_name="econojin-celery",
                environment=os.getenv("ENVIRONMENT", "production"),
            )
        )
        logger_instance.addHandler(handler)
        logger_instance.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] celery - %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        logger_instance.addHandler(handler)


def configure_celery_task_logging(logger_instance: logging.Logger) -> None:
    """Configure Celery task-level logging."""
    configure_celery_logging(logger_instance)


# ---------------------------------------------------------------------------
# Structured logging helper
# ---------------------------------------------------------------------------


def get_structured_logger(name: str, **extra: Any) -> logging.Logger:
    """Get a logger that supports structured extra fields.

    Usage:
        logger = get_structured_logger(__name__, request_id="abc123")
        logger.info("Processing request", extra={"duration_ms": 45.2})
    """
    logger = logging.getLogger(name)
    return StructuredLoggerAdapter(logger, extra)


class StructuredLoggerAdapter(logging.LoggerAdapter):
    """Adapter that injects structured fields into log records."""

    def __init__(self, logger: logging.Logger, extra: dict[str, Any]) -> None:
        super().__init__(logger, extra or {})

    def process(self, msg: Any, kwargs: Any) -> tuple[Any, Any]:
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = {"_structured_fields": extra}
        return msg, kwargs
