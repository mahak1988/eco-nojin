"""
Econojin Spider Security - Fingerprinting Layer
لایه سوم: شناسایی و fingerprinting درخواست‌ها
"""
import hashlib
import json
import os
import re
import time
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime

logger = logging.getLogger("econojin.security")


class RequestFingerprinter:
    """
    ایجاد fingerprint منحصر به فرد برای هر کلاینت
    برای شناسایی رفتارهای مشکوک و ربات‌ها
    """
    
    def __init__(self):
        self.fingerprint_db: Dict[str, Dict] = {}
        self.suspicious_threshold = int(os.getenv("SUSPICIOUS_THRESHOLD", "10"))
    
    def generate_fingerprint(self, request_headers: Dict[str, str], client_ip: str) -> str:
        """
        تولید fingerprint منحصر به فرد بر اساس ویژگی‌های درخواست
        
        Args:
            request_headers: هدرهای درخواست
            client_ip: IP کلاینت
        
        Returns:
            fingerprint رشته‌ای
        """
        # جمع‌آوری ویژگی‌ها
        features = {
            "user_agent": request_headers.get("User-Agent", ""),
            "accept_language": request_headers.get("Accept-Language", ""),
            "accept_encoding": request_headers.get("Accept-Encoding", ""),
            "connection": request_headers.get("Connection", ""),
            "client_ip": client_ip,
            "timestamp": int(time.time() / 300),  # گروه‌بندی در بازه‌های ۵ دقیقه‌ای
        }
        
        # ایجاد hash
        fingerprint_data = json.dumps(features, sort_keys=True)
        fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:32]
        
        return fingerprint
    
    def analyze_fingerprint(self, fingerprint: str, endpoint: str) -> Dict[str, Any]:
        """
        تحلیل fingerprint برای شناسایی رفتار مشکوک
        
        Returns:
            دیکشنری شامل اطلاعات تحلیل
        """
        current_time = time.time()
        
        # مقداردهی اولیه اگر fingerprint جدید است
        if fingerprint not in self.fingerprint_db:
            self.fingerprint_db[fingerprint] = {
                "first_seen": current_time,
                "last_seen": current_time,
                "request_count": 0,
                "endpoints": [],
                "suspicious_score": 0,
                "is_bot": False,
            }
        
        fp_data = self.fingerprint_db[fingerprint]
        
        # بروزرسانی اطلاعات
        fp_data["last_seen"] = current_time
        fp_data["request_count"] += 1
        fp_data["endpoints"].append(endpoint)
        
        # محدود کردن تاریخچه endpointها
        if len(fp_data["endpoints"]) > 100:
            fp_data["endpoints"] = fp_data["endpoints"][-100:]
        
        # تحلیل رفتار
        analysis = self._analyze_behavior(fp_data)
        fp_data.update(analysis)
        
        return {
            "fingerprint": fingerprint,
            "request_count": fp_data["request_count"],
            "suspicious_score": fp_data["suspicious_score"],
            "is_bot": fp_data["is_bot"],
            "risk_level": self._get_risk_level(fp_data["suspicious_score"]),
        }
    
    def _analyze_behavior(self, fp_data: Dict) -> Dict[str, Any]:
        """
        تحلیل الگوی رفتاری fingerprint
        """
        suspicious_score = fp_data["suspicious_score"]
        is_bot = fp_data["is_bot"]
        
        # بررسی سرعت درخواست‌ها
        time_diff = fp_data["last_seen"] - fp_data["first_seen"]
        if time_diff > 0:
            requests_per_second = fp_data["request_count"] / time_diff
            
            # بیشتر از ۱۰ درخواست در ثانیه مشکوک است
            if requests_per_second > 10:
                suspicious_score += 2
                logger.warning(f"🤖 High request rate detected: {requests_per_second:.2f} req/s")
        
        # بررسی تنوع endpointها
        unique_endpoints = len(set(fp_data["endpoints"]))
        total_requests = fp_data["request_count"]
        
        # اگر تمام درخواست‌ها به یک endpoint باشند، مشکوک است
        if total_requests > 20 and unique_endpoints == 1:
            suspicious_score += 3
            logger.warning(f"🎯 Single endpoint targeting detected")
        
        # بررسی اسکن endpointهای حساس
        sensitive_patterns = [
            "/admin", "/api/admin", "/.env", "/.git",
            "/backup", "/config", "/debug", "/test",
        ]
        
        sensitive_hits = sum(
            1 for ep in fp_data["endpoints"]
            if any(pattern in ep.lower() for pattern in sensitive_patterns)
        )
        
        if sensitive_hits > 3:
            suspicious_score += 5
            is_bot = True
            logger.warning(f"🕵️ Endpoint scanning detected: {sensitive_hits} hits")
        
        # بررسی User-Agent
        user_agent = fp_data.get("user_agent", "")
        if self._is_suspicious_user_agent(user_agent):
            suspicious_score += 3
            is_bot = True
        
        return {
            "suspicious_score": min(suspicious_score, 100),  # حداکثر ۱۰۰
            "is_bot": is_bot,
        }
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """
        بررسی User-Agent برای شناسایی ربات‌ها و اسکریپت‌ها
        """
        if not user_agent:
            return True  # بدون User-Agent مشکوک است
        
        # الگوهای مشکوک
        suspicious_patterns = [
            r"curl/",
            r"wget/",
            r"python-requests/",
            r"scrapy",
            r"bot",
            r"spider",
            r"crawler",
            r"scraper",
            r"httpclient",
            r"java/",
            r"go-http-client",
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True
        
        return False
    
    def _get_risk_level(self, score: int) -> str:
        """
        تعیین سطح ریسک بر اساس امتیاز
        """
        if score >= 50:
            return "CRITICAL"
        elif score >= 30:
            return "HIGH"
        elif score >= 15:
            return "MEDIUM"
        elif score >= 5:
            return "LOW"
        else:
            return "MINIMAL"
    
    def get_fingerprint_history(self, fingerprint: str) -> Optional[Dict]:
        """
        دریافت تاریخچه کامل یک fingerprint
        """
        return self.fingerprint_db.get(fingerprint)
    
    def cleanup_old_fingerprints(self, max_age_hours: int = 24):
        """
        پاکسازی fingerprintهای قدیمی
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        to_remove = []
        for fp, data in self.fingerprint_db.items():
            if current_time - data["last_seen"] > max_age_seconds:
                to_remove.append(fp)
        
        for fp in to_remove:
            del self.fingerprint_db[fp]
        
        if to_remove:
            logger.info(f"🧹 Cleaned up {len(to_remove)} old fingerprints")
        
        return len(to_remove)
