"""
Econojin Spider Security - Anomaly Detection Layer
لایه چهارم: تشخیص ناهنجاری و رفتارهای غیرعادی
"""
import os
import time
import logging
import statistics
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger("econojin.security")


class AnomalyDetector:
    """
    تشخیص ناهنجاری در الگوهای ترافیک و رفتار کاربران
    با استفاده از روش‌های آماری و heuristic
    """
    
    def __init__(self):
        # تاریخچه درخواست‌ها برای هر IP
        self.ip_history: Dict[str, List[Dict]] = defaultdict(list)
        
        # آمار کلی
        self.global_stats = {
            "total_requests": 0,
            "requests_by_minute": [],
            "avg_response_time": 0.0,
            "error_rate": 0.0,
        }
        
        # آستانه‌ها
        self.thresholds = {
            "requests_per_minute": int(os.getenv("ANOMALY_RPM_THRESHOLD", "500")),
            "error_rate": float(os.getenv("ANOMALY_ERROR_RATE", "0.3")),  # 30%
            "response_time_multiplier": float(os.getenv("ANOMALY_RESPONSE_TIME_MULT", "3.0")),
            "ip_request_spike": int(os.getenv("ANOMALY_IP_SPIKE", "100")),
        }
        
        # لیست سفید برای تست
        whitelist_env = os.getenv("SECURITY_WHITELIST_IPS", "")
        self.whitelisted_ips = set(ip.strip() for ip in whitelist_env.split(",") if ip.strip())
    
    def record_request(
        self, 
        ip: str, 
        endpoint: str, 
        method: str,
        status_code: int,
        response_time: float,
        timestamp: Optional[float] = None
    ):
        """
        ثبت یک درخواست برای تحلیل
        """
        if timestamp is None:
            timestamp = time.time()
        
        request_data = {
            "timestamp": timestamp,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time": response_time,
        }
        
        self.ip_history[ip].append(request_data)
        self.global_stats["total_requests"] += 1
        
        # پاکسازی داده‌های قدیمی (بیشتر از ۱ ساعت)
        self._cleanup_old_data(ip, max_age_seconds=3600)
    
    def detect_anomalies(self, ip: str) -> Dict[str, Any]:
        """
        تشخیص ناهنجاری‌ها برای یک IP خاص
        
        Returns:
            دیکشنری شامل ناهنجاری‌های شناسایی شده
        """
        if ip in self.whitelisted_ips:
            return {"is_anomalous": False, "reasons": []}
        
        anomalies = []
        is_anomalous = False
        
        history = self.ip_history.get(ip, [])
        
        if not history:
            return {"is_anomalous": False, "reasons": []}
        
        # ۱. بررسی حجم درخواست‌ها
        volume_anomaly = self._detect_volume_anomaly(ip, history)
        if volume_anomaly:
            anomalies.append(volume_anomaly)
            is_anomalous = True
        
        # ۲. بررسی نرخ خطا
        error_anomaly = self._detect_error_rate_anomaly(history)
        if error_anomaly:
            anomalies.append(error_anomaly)
            is_anomalous = True
        
        # ۳. بررسی زمان پاسخ
        response_anomaly = self._detect_response_time_anomaly(history)
        if response_anomaly:
            anomalies.append(response_anomaly)
            is_anomalous = True
        
        # ۴. بررسی الگوی endpointها
        endpoint_anomaly = self._detect_endpoint_pattern_anomaly(history)
        if endpoint_anomaly:
            anomalies.append(endpoint_anomaly)
            is_anomalous = True
        
        # ۵. بررسی burst traffic
        burst_anomaly = self._detect_burst_traffic(history)
        if burst_anomaly:
            anomalies.append(burst_anomaly)
            is_anomalous = True
        
        return {
            "is_anomalous": is_anomalous,
            "anomalies": anomalies,
            "risk_score": self._calculate_risk_score(anomalies),
            "recommendation": self._get_recommendation(anomalies),
        }
    
    def _detect_volume_anomaly(self, ip: str, history: List[Dict]) -> Optional[Dict]:
        """
        تشخیص افزایش ناگهانی حجم درخواست‌ها
        """
        current_time = time.time()
        minute_ago = current_time - 60
        
        # تعداد درخواست‌ها در دقیقه اخیر
        recent_requests = [r for r in history if r["timestamp"] > minute_ago]
        requests_per_minute = len(recent_requests)
        
        if requests_per_minute > self.thresholds["requests_per_minute"]:
            logger.warning(f"📊 Volume anomaly detected for {ip}: {requests_per_minute} req/min")
            return {
                "type": "VOLUME_SPIKE",
                "severity": "HIGH",
                "details": f"{requests_per_minute} requests per minute",
                "threshold": self.thresholds["requests_per_minute"],
            }
        
        # بررسی spike نسبت به میانگین
        if len(history) > 10:
            older_requests = [r for r in history if r["timestamp"] <= minute_ago and r["timestamp"] > minute_ago - 60]
            if older_requests:
                avg_previous = len(older_requests)
                if avg_previous > 0 and requests_per_minute > avg_previous * 5:
                    logger.warning(f"📈 Sudden traffic spike for {ip}: {requests_per_minute} vs avg {avg_previous}")
                    return {
                        "type": "TRAFFIC_SPIKE",
                        "severity": "MEDIUM",
                        "details": f"5x increase in traffic ({requests_per_minute} vs {avg_previous})",
                    }
        
        return None
    
    def _detect_error_rate_anomaly(self, history: List[Dict]) -> Optional[Dict]:
        """
        تشخیص نرخ خطای غیرعادی
        """
        if len(history) < 10:
            return None
        
        total = len(history)
        errors = sum(1 for r in history if r["status_code"] >= 400)
        error_rate = errors / total
        
        if error_rate > self.thresholds["error_rate"]:
            logger.warning(f"❌ High error rate detected: {error_rate:.2%}")
            return {
                "type": "HIGH_ERROR_RATE",
                "severity": "MEDIUM",
                "details": f"{error_rate:.2%} error rate ({errors}/{total})",
                "threshold": self.thresholds["error_rate"],
            }
        
        return None
    
    def _detect_response_time_anomaly(self, history: List[Dict]) -> Optional[Dict]:
        """
        تشخیص زمان پاسخ غیرعادی
        """
        response_times = [r["response_time"] for r in history if r.get("response_time")]
        
        if len(response_times) < 5:
            return None
        
        avg_time = statistics.mean(response_times)
        
        # اگر میانگین زمان پاسخ خیلی بیشتر از حد معمول باشد
        if avg_time > 5.0:  # بیشتر از ۵ ثانیه
            logger.warning(f"⏱️ Slow response times detected: avg {avg_time:.2f}s")
            return {
                "type": "SLOW_RESPONSE",
                "severity": "LOW",
                "details": f"Average response time: {avg_time:.2f}s",
            }
        
        return None
    
    def _detect_endpoint_pattern_anomaly(self, history: List[Dict]) -> Optional[Dict]:
        """
        تشخیص الگوی مشکوک در endpointها
        """
        if len(history) < 20:
            return None
        
        endpoints = [r["endpoint"] for r in history]
        unique_endpoints = len(set(endpoints))
        
        # Sequential scanning detection
        sequential_patterns = [
            "/api/v1/users/1",
            "/api/v1/users/2",
            "/api/v1/users/3",
        ]
        
        # بررسی sequential access
        numeric_endpoints = []
        for ep in endpoints[-50:]:  # آخرین ۵۰ درخواست
            import re
            numbers = re.findall(r'\d+', ep)
            if numbers:
                numeric_endpoints.extend([int(n) for n in numbers])
        
        if len(numeric_endpoints) > 10:
            # بررسی sequential بودن
            diffs = [numeric_endpoints[i+1] - numeric_endpoints[i] for i in range(len(numeric_endpoints)-1)]
            if all(d == 1 for d in diffs[-10:]):  # ۱۰ تای آخر sequential باشند
                logger.warning(f"🔢 Sequential ID scanning detected")
                return {
                    "type": "SEQUENTIAL_SCANNING",
                    "severity": "HIGH",
                    "details": "Sequential numeric ID access pattern",
                }
        
        # بررسی تنوع کم endpointها
        if unique_endpoints < 3 and len(history) > 50:
            logger.warning(f"🎯 Low endpoint diversity: {unique_endpoints} unique out of {len(history)}")
            return {
                "type": "LOW_ENDPOINT_DIVERSITY",
                "severity": "MEDIUM",
                "details": f"Only {unique_endpoints} unique endpoints accessed",
            }
        
        return None
    
    def _detect_burst_traffic(self, history: List[Dict]) -> Optional[Dict]:
        """
        تشخیص ترافیک انفجاری (burst)
        """
        if len(history) < 10:
            return None
        
        # گروه‌بندی درخواست‌ها در بازه‌های ۱ ثانیه‌ای
        time_buckets: Dict[int, int] = defaultdict(int)
        for r in history[-100:]:  # آخرین ۱۰۰ درخواست
            bucket = int(r["timestamp"])
            time_buckets[bucket] += 1
        
        # بررسی burst (بیش از ۲۰ درخواست در یک ثانیه)
        for second, count in time_buckets.items():
            if count > 20:
                logger.warning(f"💥 Burst traffic detected: {count} requests in 1 second")
                return {
                    "type": "BURST_TRAFFIC",
                    "severity": "HIGH",
                    "details": f"{count} requests in a single second",
                }
        
        return None
    
    def _calculate_risk_score(self, anomalies: List[Dict]) -> int:
        """
        محاسبه امتیاز ریسک بر اساس ناهنجاری‌ها
        """
        severity_scores = {
            "LOW": 10,
            "MEDIUM": 25,
            "HIGH": 50,
            "CRITICAL": 100,
        }
        
        total_score = sum(
            severity_scores.get(a.get("severity", "LOW"), 10)
            for a in anomalies
        )
        
        return min(total_score, 100)
    
    def _get_recommendation(self, anomalies: List[Dict]) -> str:
        """
        ارائه توصیه بر اساس ناهنجاری‌ها
        """
        if not anomalies:
            return "No action needed"
        
        risk_score = self._calculate_risk_score(anomalies)
        
        if risk_score >= 75:
            return "BLOCK: Immediate IP blocking recommended"
        elif risk_score >= 50:
            return "RATE_LIMIT: Apply strict rate limiting"
        elif risk_score >= 25:
            return "MONITOR: Increase monitoring frequency"
        else:
            return "WATCH: Continue normal monitoring"
    
    def _cleanup_old_data(self, ip: str, max_age_seconds: int = 3600):
        """
        پاکسازی داده‌های قدیمی
        """
        current_time = time.time()
        cutoff = current_time - max_age_seconds
        
        self.ip_history[ip] = [
            r for r in self.ip_history[ip]
            if r["timestamp"] > cutoff
        ]
        
        # حذف کامل اگر خالی شد
        if not self.ip_history[ip]:
            del self.ip_history[ip]
    
    def get_ip_statistics(self, ip: str) -> Dict[str, Any]:
        """
        دریافت آمار کامل برای یک IP
        """
        history = self.ip_history.get(ip, [])
        
        if not history:
            return {"error": "No data available"}
        
        total = len(history)
        errors = sum(1 for r in history if r["status_code"] >= 400)
        response_times = [r["response_time"] for r in history if r.get("response_time")]
        
        return {
            "total_requests": total,
            "error_count": errors,
            "error_rate": errors / total if total > 0 else 0,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "unique_endpoints": len(set(r["endpoint"] for r in history)),
            "methods": dict(defaultdict(int, {r["method"]: sum(1 for x in history if x["method"] == r["method"]) for r in history})),
            "time_range": {
                "first": datetime.fromtimestamp(min(r["timestamp"] for r in history)).isoformat(),
                "last": datetime.fromtimestamp(max(r["timestamp"] for r in history)).isoformat(),
            },
        }
