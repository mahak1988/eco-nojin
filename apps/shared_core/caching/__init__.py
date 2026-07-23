"""
Caching Module with Redis
ماژول کشینگ برای بهینه‌سازی عملکرد با استفاده از Redis
"""
import json
import hashlib
import logging
from functools import wraps
from typing import Any, Optional, Callable
import asyncio

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        import aioredis
        REDIS_AVAILABLE = True
    except ImportError:
        REDIS_AVAILABLE = False
        logger.warning("Redis not available. Caching will be disabled.")


class RedisCache:
    """
    Redis Cache Manager برای مدیریت عملیات کشینگ
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        default_ttl: int = 300,  # 5 دقیقه
        prefix: str = "econojin:"
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.default_ttl = default_ttl
        self.prefix = prefix
        self._redis: Optional[aioredis.Redis] = None
    
    async def connect(self) -> bool:
        """اتصال به Redis"""
        if not REDIS_AVAILABLE:
            return False
        
        try:
            self._redis = await aioredis.from_url(
                f"redis://{self.host}:{self.port}/{self.db}",
                password=self.password,
                encoding="utf-8",
                decode_responses=True
            )
            await self._redis.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return False
    
    async def disconnect(self):
        """قطع اتصال از Redis"""
        if self._redis:
            await self._redis.close()
            logger.info("Disconnected from Redis")
    
    def _generate_key(self, key: str) -> str:
        """تولید کلید یکتا با پیشوند"""
        return f"{self.prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """دریافت مقدار از کش"""
        if not self._redis:
            return None
        
        try:
            full_key = self._generate_key(key)
            value = await self._redis.get(full_key)
            if value:
                logger.debug(f"Cache HIT: {full_key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {full_key}")
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """ذخیره مقدار در کش"""
        if not self._redis:
            return False
        
        try:
            full_key = self._generate_key(key)
            serialized = json.dumps(value, default=str)
            ttl = ttl or self.default_ttl
            await self._redis.setex(full_key, ttl, serialized)
            logger.debug(f"Cached: {full_key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """حذف مقدار از کش"""
        if not self._redis:
            return False
        
        try:
            full_key = self._generate_key(key)
            await self._redis.delete(full_key)
            logger.debug(f"Deleted cache: {full_key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """باطل کردن تمام کلیدهای مطابق با الگو"""
        if not self._redis:
            return 0
        
        try:
            full_pattern = self._generate_key(pattern)
            keys = []
            async for key in self._redis.scan_iter(match=full_pattern):
                keys.append(key)
            
            if keys:
                deleted = await self._redis.delete(*keys)
                logger.info(f"Invalidated {deleted} keys matching pattern: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error invalidating pattern {pattern}: {e}")
            return 0
    
    async def health_check(self) -> dict:
        """بررسی سلامت Redis"""
        if not self._redis:
            return {"status": "disconnected", "available": False}
        
        try:
            info = await self._redis.info("stats")
            return {
                "status": "connected",
                "available": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "N/A"),
                "hit_rate": await self._get_hit_rate()
            }
        except Exception as e:
            return {"status": "error", "available": False, "error": str(e)}
    
    async def _get_hit_rate(self) -> Optional[float]:
        """محاسبه نرخ Hit کش"""
        try:
            info = await self._redis.info("stats")
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            total = hits + misses
            if total == 0:
                return None
            return round((hits / total) * 100, 2)
        except Exception:
            return None


# Global cache instance
cache_manager = RedisCache(
    host="localhost",
    port=6379,
    db=0,
    password=None,
    default_ttl=300,
    prefix="econojin:"
)


def cached(
    key_prefix: str = "",
    ttl: int = 300,
    key_generator: Optional[Callable] = None
):
    """
    Decorator برای کش کردن نتایج توابع
    
    Args:
        key_prefix: پیشوند برای کلید کش
        ttl: زمان اعتبار کش به ثانیه
        key_generator: تابع سفارشی برای تولید کلید (اختیاری)
    
    مثال:
        @cached(key_prefix="user_profile", ttl=600)
        async def get_user_profile(user_id: int):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # تولید کلید کش
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                # تولید کلید خودکار بر اساس نام تابع و آرگومان‌ها
                func_name = func.__name__
                args_str = str(args) if args else ""
                kwargs_str = str(sorted(kwargs.items())) if kwargs else ""
                key_hash = hashlib.md5(f"{args_str}{kwargs_str}".encode()).hexdigest()[:8]
                cache_key = f"{key_prefix}:{func_name}:{key_hash}" if key_prefix else f"{func_name}:{key_hash}"
            
            # تلاش برای دریافت از کش
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # اجرا تابع و ذخیره در کش
            result = await func(*args, **kwargs)
            if result is not None:
                await cache_manager.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator


async def init_cache() -> bool:
    """راه‌اندازی ماژول کشینگ"""
    return await cache_manager.connect()


async def close_cache():
    """بستن اتصال کش"""
    await cache_manager.disconnect()
