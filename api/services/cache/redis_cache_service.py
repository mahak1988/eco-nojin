"""Redis Cache Service - Advanced Caching Layer

این سرویس لایه کش‌گذاری پیشرفته را با Redis پیاده‌سازی می‌کند
برای کاهش بار پایگاه داده و افزایش سرعت پاسخ‌دهی.
"""
import redis
import json
import hashlib
from typing import Any, Optional, Dict, List
from datetime import timedelta
import os


class RedisCacheService:
    """سرویس کش‌گذاری Redis"""
    
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.client = redis.from_url(self.redis_url, decode_responses=True)
        self.default_ttl = 3600  # 1 hour
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """تولید کلید کش"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"econojin:{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """دریافت مقدار از کش"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """ذخیره مقدار در کش"""
        try:
            ttl = ttl or self.default_ttl
            self.client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """حذف مقدار از کش"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def get_or_set(self, key: str, callback, ttl: int = None) -> Any:
        """دریافت از کش یا اجرای callback و ذخیره"""
        value = self.get(key)
        if value is not None:
            return value
        
        value = callback()
        self.set(key, value, ttl)
        return value
    
    def cached(self, prefix: str, ttl: int = None):
        """Decorator برای کش‌گذاری توابع"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                key = self._generate_key(prefix, *args, **kwargs)
                return self.get_or_set(key, lambda: func(*args, **kwargs), ttl)
            return wrapper
        return decorator
    
    def invalidate_pattern(self, pattern: str) -> int:
        """باطل کردن تمام کلیدهای منطبق با الگو"""
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache invalidation error: {e}")
            return 0
    
    def get_stats(self) -> Dict:
        """دریافت آمار Redis"""
        try:
            info = self.client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """محاسبه نرخ hit کش"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)


# Singleton instance
cache_service = RedisCacheService()


# Decorators for common caching patterns
def cache_pilot_data(ttl: int = 7200):
    """Decorator برای کش‌گذاری داده‌های پایلوت"""
    return cache_service.cached("pilot", ttl)


def cache_dashboard_data(ttl: int = 300):
    """Decorator برای کش‌گذاری داده‌های داشبورد (5 دقیقه)"""
    return cache_service.cached("dashboard", ttl)


def cache_mrv_calculation(ttl: int = 86400):
    """Decorator برای کش‌گذاری محاسبات MRV (24 ساعت)"""
    return cache_service.cached("mrv", ttl)
