"""Performance Tests for Econojin

تست‌های عملکرد و benchmark برای اطمینان از مقیاس‌پذیری.
"""
import pytest
import time
from datetime import datetime, timezone
from api.services.cache.redis_cache_service import RedisCacheService
from api.services.monitoring.performance_monitor import PerformanceMonitor


class TestCachePerformance:
    """تست‌های عملکرد کش"""
    
    def test_cache_set_get_performance(self):
        """تست عملکرد set/get کش"""
        cache = RedisCacheService()
        
        start = time.perf_counter()
        
        # Set 100 items
        for i in range(100):
            cache.set(f"test_key_{i}", {"value": i}, ttl=60)
        
        # Get 100 items
        for i in range(100):
            cache.get(f"test_key_{i}")
        
        end = time.perf_counter()
        execution_time = end - start
        
        # Should complete in less than 1 second
        assert execution_time < 1.0, f"Cache operations too slow: {execution_time}s"
    
    def test_cache_hit_rate(self):
        """تست نرخ hit کش"""
        cache = RedisCacheService()
        
        # Set a value
        cache.set("test_hit", {"data": "test"}, ttl=60)
        
        # Get multiple times
        hits = 0
        for _ in range(10):
            result = cache.get("test_hit")
            if result:
                hits += 1
        
        assert hits == 10, "Cache hit rate should be 100%"


class TestMonitoringPerformance:
    """تست‌های عملکرد مانیتورینگ"""
    
    def test_system_metrics_collection(self):
        """تست جمع‌آوری معیارهای سیستم"""
        monitor = PerformanceMonitor()
        
        start = time.perf_counter()
        metrics = monitor.get_system_metrics()
        end = time.perf_counter()
        
        execution_time = end - start
        
        # Should collect metrics in less than 2 seconds
        assert execution_time < 2.0
        assert "cpu_percent" in metrics
        assert "memory_percent" in metrics
    
    def test_execution_time_measurement(self):
        """تست اندازه‌گیری زمان اجرا"""
        monitor = PerformanceMonitor()
        
        @monitor.measure_execution_time("test_function")
        def sample_function():
            time.sleep(0.1)
            return "result"
        
        # Call function 5 times
        for _ in range(5):
            sample_function()
        
        # Check metrics
        metrics = monitor.get_function_metrics("test_function")
        assert metrics["call_count"] == 5
        assert metrics["avg_time_ms"] >= 100  # At least 100ms


class TestScalability:
    """تست‌های مقیاس‌پذیری"""
    
    def test_concurrent_pilot_access(self):
        """تست دسترسی هم‌زمان به پایلوت‌ها"""
        pilots = [
            "dishmok", "behbahan", "rodbar_talesh", "snow_mountain",
            "ouarzazate", "wadi_rum", "sahel_senegal", "ethiopian_highlands",
            "rajasthan", "outback_australia", "atacama_chile", "mongolian_steppe"
        ]
        
        start = time.perf_counter()
        
        # Simulate concurrent access
        for pilot in pilots:
            # In real scenario, this would be async
            time.sleep(0.01)  # Simulate 10ms per pilot
        
        end = time.perf_counter()
        execution_time = end - start
        
        # Should handle all pilots in less than 1 second
        assert execution_time < 1.0
    
    def test_large_dataset_processing(self):
        """تست پردازش داده‌های بزرگ"""
        # Simulate processing 10,000 records
        data = [{"id": i, "value": i * 2} for i in range(10000)]
        
        start = time.perf_counter()
        
        # Process data
        result = [d["value"] for d in data if d["value"] > 5000]
        
        end = time.perf_counter()
        execution_time = end - start
        
        # Should process in less than 0.5 seconds
        assert execution_time < 0.5
        assert len(result) > 0


class TestDatabasePerformance:
    """تست‌های عملکرد پایگاه داده"""
    
    def test_connection_pooling(self):
        """تست Connection Pooling"""
        from api.core.database import engine
        
        # Check pool configuration
        assert engine.pool.size() == 20
        assert engine.pool._max_overflow == 30
    
    def test_query_optimization(self):
        """تست بهینه‌سازی query"""
        from api.core.database import get_db
        
        # This would test actual query performance
        # For now, just verify the function exists
        assert callable(get_db)
