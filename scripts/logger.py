"""
سیستم لاگینگ یکپارچه برای کل پروژه
جایگزین تمام print statements
"""

import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import structlog

    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


class ColorFormatter(logging.Formatter):
    """فرمت‌کننده رنگی برای ترمینال"""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m",  # Red background
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class UnifiedLogger:
    """
    لاگر یکپارچه با قابلیت‌های:
    - خروجی رنگی به کنسول
    - ذخیره در فایل (JSON و text)
    - چرخش خودکار لاگ‌ها
    - پشتیبانی از structlog
    """

    _loggers: dict = {}

    @classmethod
    def get_logger(
        cls, name: str, log_dir: Optional[Path] = None, level: int = logging.INFO
    ) -> logging.Logger:
        """دریافت لاگر با نام مشخص"""

        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False

        # پاک کردن handler های قبلی
        logger.handlers.clear()

        # Console handler (رنگی)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_format = ColorFormatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

        # File handler (اختیاری)
        if log_dir:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)

            # File handler - Text
            text_file = log_dir / f"{name}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                text_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
            )
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s"
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger


def get_structured_logger(name: str):
    """
    لاگر ساختاریافته با structlog (برای production)
    """
    if not STRUCTLOG_AVAILABLE:
        return UnifiedLogger.get_logger(name)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger(name)


# استفاده آسان
def setup_project_logging(log_dir: Optional[Path] = None):
    """راه‌اندازی لاگینگ برای کل پروژه"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # کاهش لاگ‌های پر سر و صدا
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


# Disable colors on Windows to avoid encoding issues
import os as _os

if _os.name == "nt":
    # Windows - disable ANSI colors
    # SECURITY WARNING: Consider shell=False for better security
    subprocess.run("", shell=True, check=False)  # Enable ANSI on Win10+
