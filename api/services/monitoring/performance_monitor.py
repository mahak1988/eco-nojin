"""Performance Monitoring Service

این سرویس مانیتورینگ عملکرد و تولید گزارش‌های benchmark را فراهم می‌کند.
"""
import time
import psutil
import os
from typing import Dict, List
from datetime import datetime, timezone
from collections import defaultdict


class PerformanceMonitor:
    """مانیتورینگ عملکرد سیستم"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_time = datetime.now(timezone.utc)
    
    def measure_execution_time(self, func_name: str):
        """Decorator برای اندازه‌گیری زمان اجرا"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                result = func(*args, **kwargs)
                end = time.perf_counter()
                
                execution_time = end - start
                self.metrics[func_name].append({
                    "execution_time": execution_time,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                return result
            return wrapper
        return decorator
    
    def get_system_metrics(self) -> Dict:
        """دریافت معیارهای سیستم"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_percent": memory.percent,
            "disk_total_gb": round(disk.total / (1024**3), 2),
            "disk_used_gb": round(disk.used / (1024**3), 2),
            "disk_percent": disk.percent,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_function_metrics(self, func_name: str = None) -> Dict:
        """دریافت معیارهای توابع"""
        if func_name:
            metrics = self.metrics.get(func_name, [])
            if not metrics:
                return {"error": "No metrics found"}
            
            times = [m["execution_time"] for m in metrics]
            return {
                "function": func_name,
                "call_count": len(times),
                "avg_time_ms": round(sum(times) / len(times) * 1000, 2),
                "min_time_ms": round(min(times) * 1000, 2),
                "max_time_ms": round(max(times) * 1000, 2),
                "p95_time_ms": round(sorted(times)[int(len(times) * 0.95)] * 1000, 2),
                "last_call": metrics[-1]["timestamp"]
            }
        
        # All functions
        result = {}
        for func_name, metrics in self.metrics.items():
            times = [m["execution_time"] for m in metrics]
            result[func_name] = {
                "call_count": len(times),
                "avg_time_ms": round(sum(times) / len(times) * 1000, 2),
                "min_time_ms": round(min(times) * 1000, 2),
                "max_time_ms": round(max(times) * 1000, 2)
            }
        
        return result
    
    def get_uptime(self) -> Dict:
        """دریافت زمان فعالیت"""
        uptime = datetime.now(timezone.utc) - self.start_time
        return {
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_human": str(uptime).split('.')[0]
        }
    
    def generate_performance_report(self) -> Dict:
        """تولید گزارش عملکرد کامل"""
        return {
            "system": self.get_system_metrics(),
            "functions": self.get_function_metrics(),
            "uptime": self.get_uptime(),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }


# Singleton instance
performance_monitor = PerformanceMonitor()
