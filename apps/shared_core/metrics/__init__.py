"""
Metrics and Monitoring Module
ماژول مانیتورینگ و معیارهای عملکرد
"""
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """معیارهای عملکرد سیستم"""
    
    # Database Metrics
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_active_connections: int = 0
    
    # Cache Metrics
    cache_enabled: bool = False
    cache_hit_rate: Optional[float] = None
    cache_hits: int = 0
    cache_misses: int = 0
    
    # API Metrics
    avg_response_time: float = 0.0
    slow_queries_count: int = 0
    total_requests: int = 0
    
    # Error Metrics
    error_count: int = 0
    last_error: Optional[str] = None
    
    # Timestamps
    last_updated: float = field(default_factory=time.time)
    
    def update_cache_stats(self, hits: int, misses: int):
        """بروزرسانی آمار کش"""
        self.cache_hits = hits
        self.cache_misses = misses
        total = hits + misses
        if total > 0:
            self.cache_hit_rate = round((hits / total) * 100, 2)
        self.last_updated = time.time()
    
    def record_request(self, response_time: float, is_slow: bool = False):
        """ثبت درخواست جدید"""
        self.total_requests += 1
        # Moving average برای response time
        self.avg_response_time = (
            (self.avg_response_time * (self.total_requests - 1) + response_time) 
            / self.total_requests
        )
        if is_slow:
            self.slow_queries_count += 1
        self.last_updated = time.time()
    
    def record_error(self, error_msg: str):
        """ثبت خطا"""
        self.error_count += 1
        self.last_error = error_msg
        self.last_updated = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        return {
            "database": {
                "pool_size": self.db_pool_size,
                "max_overflow": self.db_max_overflow,
                "active_connections": self.db_active_connections,
            },
            "cache": {
                "enabled": self.cache_enabled,
                "hit_rate": self.cache_hit_rate,
                "hits": self.cache_hits,
                "misses": self.cache_misses,
            },
            "api": {
                "avg_response_time_ms": round(self.avg_response_time * 1000, 2),
                "slow_queries_count": self.slow_queries_count,
                "total_requests": self.total_requests,
            },
            "errors": {
                "count": self.error_count,
                "last_error": self.last_error,
            },
            "last_updated": self.last_updated,
        }


# Global metrics instance
metrics = PerformanceMetrics()


async def get_system_health() -> Dict[str, Any]:
    """
    دریافت وضعیت سلامت سیستم
    شامل معیارهای دیتابیس، کش و API
    """
    from apps.shared_core.database.session import engine
    from apps.shared_core.caching import cache_manager
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {}
    }
    
    # Check Database
    try:
        # بررسی اتصال دیتابیس
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        health_status["components"]["database"] = {
            "status": "healthy",
            "pool_size": metrics.db_pool_size,
            "max_overflow": metrics.db_max_overflow,
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check Cache
    cache_health = await cache_manager.health_check()
    health_status["components"]["cache"] = cache_health
    if not cache_health.get("available", False):
        health_status["status"] = "degraded"
    
    # Add Metrics
    health_status["metrics"] = metrics.to_dict()
    
    return health_status


def configure_logging_for_performance():
    """
    پیکربندی لاگینگ برای شناسایی Slow Queries
    """
    # تنظیم سطح لاگ برای SQLAlchemy
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    
    # ایجاد Handler مخصوص برای Slow Queries
    slow_query_handler = logging.FileHandler("slow_queries.log")
    slow_query_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    slow_query_handler.setFormatter(formatter)
    
    logger = logging.getLogger("sqlalchemy.engine")
    logger.addHandler(slow_query_handler)
    
    logger.info("Performance logging configured")


async def init_metrics():
    """راه‌اندازی ماژول معیارها"""
    configure_logging_for_performance()
    logger.info("Metrics module initialized")
    return metrics
