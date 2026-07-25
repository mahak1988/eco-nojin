
"""Zero Trust Security — Never Trust, Always Verify (2026)."""
from __future__ import annotations

class ZeroTrustConfig:
    """تنظیمات Zero Trust."""

    # ۱. Identity Verification — هر درخواست باید احراز هویت شود
    REQUIRE_AUTH_ALL_ENDPOINTS = True
    PUBLIC_ENDPOINTS = {"/health", "/docs", "/openapi.json", "/redoc"}

    # ۲. Least Privilege — حداقل دسترسی
    DEFAULT_ROLE = "viewer"
    ROLE_HIERARCHY = {
        "admin": ["admin", "editor", "viewer"],
        "editor": ["editor", "viewer"],
        "viewer": ["viewer"],
    }

    # ۳. Microsegmentation — جداسازی سرویس‌ها
    SERVICE_TOKENS = {
        "api": "internal-api-token",
        "cms": "internal-cms-token",
        "ai": "internal-ai-token",
    }

    # ۴. Continuous Verification — بررسی مداوم
    TOKEN_MAX_AGE_MINUTES = 60
    REQUIRE_MFA_ADMIN = True
    SESSION_BINDING = True  #绑定 IP + User-Agent

    # ۵. Assume Breach — فرض نفوذ
    LOG_ALL_ACCESS = True
    ANOMALY_DETECTION = True
    AUTO_LOCKOUT_THRESHOLD = 5
