"""
Econojin Spider Security - Middleware Layer
لایه اول: middlewareهای امنیتی برای فیلتر کردن درخواست‌ها
"""
import time
import hashlib
import re
import os
import json
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict
from datetime import datetime, timedelta
import logging

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger("econojin.security")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    لایه ۱: افزودن هدرهای امنیتی به پاسخ‌ها
    - X-Frame-Options: جلوگیری از clickjacking
    - X-Content-Type-Options: جلوگیری از MIME sniffing
    - X-XSS-Protection: فعال‌سازی XSS filter مرورگر
    - Content-Security-Policy: محدود کردن منابع قابل اعتماد
    - Referrer-Policy: کنترل اطلاعات referrer
    - Strict-Transport-Security: اجبار HTTPS
    - Permissions-Policy: محدود کردن ویژگی‌های مرورگر
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.is_production = os.getenv("ENV_STATE", "development") == "production"
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # جلوگیری از Clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # جلوگیری از MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS (فقط در production)
        if self.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=(), usb=()"
        )
        
        # حذف هدرهای حساس
        headers_to_remove = ["Server", "X-Powered-By", "X-AspNet-Version"]
        for header in headers_to_remove:
            if header in response.headers:
                del response.headers[header]
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    لایه ۲: کنترل نرخ درخواست‌ها (Rate Limiting)
    - محدودیت درخواست بر اساس IP
    - الگوریتم sliding window
    - قابلیت تنظیم برای endpointهای مختلف
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # تنظیمات پیش‌فرض
        self.requests_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
        self.requests_per_hour = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
        self.window_size = 60  # ثانیه
        
        # ذخیره‌سازی موقت برای tracking درخواست‌ها
        self.request_history: Dict[str, List[float]] = defaultdict(list)
        self.hourly_history: Dict[str, List[float]] = defaultdict(list)
        
        # لیست endpointهای با محدودیت ویژه
        self.strict_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/users",
        ]
        self.strict_limit = 10  # درخواست در دقیقه برای endpointهای حساس
        
    def _get_client_ip(self, request: Request) -> str:
        """استخراج IP واقعی کلاینت حتی پشت proxy"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        return request.client.host if request.client else "unknown"
    
    def _clean_old_entries(self, history: Dict[str, List[float]], cutoff: float):
        """حذف ورودی‌های قدیمی از تاریخچه"""
        for ip in list(history.keys()):
            history[ip] = [t for t in history[ip] if t > cutoff]
            if not history[ip]:
                del history[ip]
    
    def _is_rate_limited(self, ip: str, current_time: float, is_strict: bool = False) -> tuple[bool, int]:
        """بررسی اینکه آیا IP محدود شده است"""
        limit = self.strict_limit if is_strict else self.requests_per_minute
        
        # Clean old entries
        cutoff = current_time - self.window_size
        self._clean_old_entries(self.request_history, cutoff)
        
        # Count requests in current window
        recent_requests = len(self.request_history[ip])
        
        if recent_requests >= limit:
            return True, limit
        
        # Add current request
        self.request_history[ip].append(current_time)
        
        return False, limit
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # نادیده گرفتن health check و docs
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # بررسی endpointهای حساس
        is_strict = any(
            request.url.path.startswith(ep) 
            for ep in self.strict_endpoints
        )
        
        # بررسی rate limit
        is_limited, limit = self._is_rate_limited(client_ip, current_time, is_strict)
        
        if is_limited:
            logger.warning(f"⚠️ Rate limit exceeded for IP: {client_ip} on {request.url.path}")
            
            # اضافه کردن هدرهای informative
            retry_after = self.window_size
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Too Many Requests",
                    "message": f"شما بیش از حد مجاز ({limit} درخواست در دقیقه) ارسال کرده‌اید.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        # ادامه پردازش درخواست
        response = await call_next(request)
        
        # اضافه کردن هدرهای rate limit به پاسخ
        remaining = limit - len(self.request_history[client_ip])
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_size))
        
        return response


class HoneypotMiddleware(BaseHTTPMiddleware):
    """
    لایه ۳: تله عنکبوتی (Honeypot)
    - ایجاد endpointهای جعلی برای شناسایی اسکنرها و مهاجمان
    - ثبت فعالیت‌های مشکوک
    - مسدود کردن خودکار IPهای مخرب
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.honeypot_paths = [
            "/admin",
            "/wp-admin",
            "/phpmyadmin",
            "/.env",
            "/.git/config",
            "/backup.sql",
            "/database.sql",
            "/config.php",
            "/wp-login.php",
            "/administrator",
            "/.htaccess",
            "/server-status",
            "/api/admin",
            "/api/debug",
            "/graphql",
            "/.aws/credentials",
        ]
        
        # IPهای مسدود شده
        self.blocked_ips: set = set()
        self.ip_violations: Dict[str, int] = defaultdict(int)
        
        # لاگ فعالیت‌های honeypot
        self.honeypot_log_file = os.getenv("HONEYPOT_LOG_FILE", "/tmp/honeypot.log")
        
    def _log_honeypot_hit(self, ip: str, path: str, user_agent: str):
        """ثبت فعالیت honeypot"""
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "ip": ip,
            "path": path,
            "user_agent": user_agent,
        }
        
        try:
            with open(self.honeypot_log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write honeypot log: {e}")
        
        logger.warning(f"🕸️ HONEYPOT TRIGGERED: {ip} tried to access {path}")
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
        user_agent = request.headers.get("User-Agent", "")
        
        # بررسی اینکه آیا IP مسدود است
        if client_ip in self.blocked_ips:
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden", "message": "دسترسی مسدود شده است"}
            )
        
        # بررسی honeypot paths
        if any(request.url.path.startswith(hp) for hp in self.honeypot_paths):
            self._log_honeypot_hit(client_ip, request.url.path, user_agent)
            
            # افزایش تعداد تخلفات
            self.ip_violations[client_ip] += 1
            
            # مسدود کردن بعد از ۳ تخلف
            if self.ip_violations[client_ip] >= 3:
                self.blocked_ips.add(client_ip)
                logger.critical(f"🚫 IP BLOCKED: {client_ip} after multiple honeypot violations")
            
            # بازگرداندن پاسخ 404 برای گیج کردن مهاجم
            return JSONResponse(
                status_code=404,
                content={"error": "Not Found", "message": "صفحه مورد نظر یافت نشد"}
            )
        
        # ادامه پردازش عادی
        response = await call_next(request)
        return response


class SpiderSecurityMiddleware(BaseHTTPMiddleware):
    """
    لایه اصلی امنیت عنکبوتی - ترکیب تمام لایه‌ها
    این middleware تمام لایه‌های امنیتی را یکپارچه می‌کند
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_headers = SecurityHeadersMiddleware(app)
        self.rate_limiter = RateLimitMiddleware(app)
        self.honeypot = HoneypotMiddleware(app)
        
        # لیست سیاه IPها
        self.blacklist_file = os.getenv("SECURITY_BLACKLIST_FILE", "/tmp/security_blacklist.json")
        self.blacklisted_ips: set = self._load_blacklist()
        
        # لیست سفید IPها (برای تست)
        whitelist_env = os.getenv("SECURITY_WHITELIST_IPS", "")
        self.whitelisted_ips = set(ip.strip() for ip in whitelist_env.split(",") if ip.strip())
        
    def _load_blacklist(self) -> set:
        """بارگذاری لیست سیاه از فایل"""
        try:
            if os.path.exists(self.blacklist_file):
                with open(self.blacklist_file, "r") as f:
                    data = json.load(f)
                    return set(data.get("blacklisted_ips", []))
        except Exception as e:
            logger.error(f"Error loading blacklist: {e}")
        return set()
    
    def _save_blacklist(self):
        """ذخیره لیست سیاه در فایل"""
        try:
            with open(self.blacklist_file, "w") as f:
                json.dump({"blacklisted_ips": list(self.blacklisted_ips)}, f)
        except Exception as e:
            logger.error(f"Error saving blacklist: {e}")
    
    def _add_to_blacklist(self, ip: str, reason: str):
        """اضافه کردن IP به لیست سیاه"""
        if ip not in self.whitelisted_ips:
            self.blacklisted_ips.add(ip)
            self._save_blacklist()
            logger.critical(f"🚫 BLACKLISTED: {ip} - Reason: {reason}")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # استخراج IP کلاینت
        client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
        if isinstance(client_ip, str) and "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()
        
        # بررسی لیست سیاه
        if client_ip in self.blacklisted_ips:
            logger.warning(f"🚫 Blocked request from blacklisted IP: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden", "message": "دسترسی شما مسدود شده است"}
            )
        
        # نادیده گرفتن لیست سفید
        if client_ip in self.whitelisted_ips:
            return await call_next(request)
        
        # اجرای لایه honeypot
        honeypot_response = await self.honeypot.dispatch(request, call_next)
        if honeypot_response.status_code != 200 and client_ip not in self.whitelisted_ips:
            # اگر honeypot triggered شد، ممکن است نیاز به blacklist باشد
            if honeypot_response.status_code == 403:
                self._add_to_blacklist(client_ip, "Multiple honeypot violations")
            return honeypot_response
        
        # اجرای rate limiting
        rate_limit_response = await self.rate_limiter.dispatch(request, call_next)
        if rate_limit_response.status_code == 429:
            # بعد از چندین بار rate limit violation، blacklist کن
            self._add_to_blacklist(client_ip, "Repeated rate limit violations")
            return rate_limit_response
        
        # اجرای security headers
        response = await self.security_headers.dispatch(request, call_next)
        
        # اضافه کردن fingerprint به response
        response.headers["X-Econojin-Security"] = "Spider-Security-Active"
        
        return response
