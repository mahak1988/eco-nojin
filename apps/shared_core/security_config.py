"""
Security Configuration Module
Integrates security configurations from both main apps and eco-nojin project
"""

import os
from enum import Enum
from typing import Any


class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


# Security configuration based on analysis of both codebases
SECURITY_CONFIG = {
    "level": SecurityLevel.HIGH,
    # Rate limiting configuration
    "rate_limiting": {
        "enabled": True,
        "default_requests_per_minute": 120,
        "login_requests_per_minute": 30,
        "burst_window_seconds": 60,
        "track_by_ip": True,
        "track_by_user_agent": True,
    },
    # Bot detection and prevention
    "bot_detection": {
        "enabled": True,
        "blocked_agents": [
            "sqlmap",
            "nikto",
            "nmap",
            "masscan",
            "dirbuster",
            "gobuster",
            "wfuzz",
            "hydra",
            "burp",
            "zap",
            "scrapy",
            "googlebot",
            "bingbot",
            "yandexbot",
            "baiduspider",
            "duckduckbot",
            "slurp",
            "facebot",
            "ia_archiver",
            "semrushbot",
            "ahrefsbot",
            "dotbot",
            "mj12bot",
            "petalbot",
        ],
        "allow_developer_tools": True,  # Allow curl, wget, httpie for API clients
    },
    # Input validation and sanitization
    "input_validation": {
        "max_request_size_bytes": 10 * 1024 * 1024,  # 10MB
        "suspicious_patterns": [
            r"(?i)(union\s+select|insert\s+into|drop\s+table|delete\s+from)",
            r"(?i)(<script|javascript:|vbscript:|on\w+\s*=)",
            r"(?i)(\.\./|\.\.\\|%2e%2e)",
            r"(?i)(cmd\.exe|/bin/sh|/bin/bash|powershell)",
            r"(?i)(eval\s*\(|exec\s*\(|system\s*\()",
        ],
        "allowed_content_types": [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain",
        ],
    },
    # Security headers
    "security_headers": {
        "X-Frame-Options": "SAMEORIGIN",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "X-Permitted-Cross-Domain-Policies": "none",
    },
    # Authentication and authorization
    "authentication": {
        "jwt_algorithm": "HS256",
        "access_token_expire_minutes": 30,
        "refresh_token_expire_days": 7,
        "require_https": True,
        "session_timeout_minutes": 30,
        "max_login_attempts": 5,
        "lockout_duration_minutes": 30,
    },
    # Logging and monitoring
    "monitoring": {
        "log_security_events": True,
        "alert_on_anomalies": True,
        "request_tracing_enabled": True,
        "failed_auth_logging": True,
        "suspicious_activity_alerts": True,
    },
    # Environment-specific settings
    "environments": {
        "production": {
            "debug_mode": False,
            "detailed_error_messages": False,
            "strict_security": True,
            "require_authentication": True,
        },
        "development": {
            "debug_mode": True,
            "detailed_error_messages": True,
            "strict_security": False,
            "rate_limit_multiplier": 2,
        },
        "testing": {
            "debug_mode": True,
            "detailed_error_messages": True,
            "strict_security": False,
            "rate_limit_multiplier": 10,
        },
    },
}


def get_current_environment() -> str:
    """Get the current environment from environment variables."""
    return os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "development")).lower()


def get_security_config() -> dict[str, Any]:
    """Get security configuration adjusted for current environment."""
    env = get_current_environment()
    config = SECURITY_CONFIG.copy()

    # Adjust settings based on environment
    if env in config["environments"]:
        env_settings = config["environments"][env]
        for key, value in env_settings.items():
            if key == "rate_limit_multiplier" and isinstance(value, (int, float)):
                config["rate_limiting"]["default_requests_per_minute"] = int(
                    config["rate_limiting"]["default_requests_per_minute"] * value
                )
            else:
                config[key] = value

    return config


def is_production() -> bool:
    """Check if running in production environment."""
    return get_current_environment() == "production"


def get_blocked_user_agents() -> list[str]:
    """Get list of blocked user agents."""
    config = get_security_config()
    return (
        config["bot_detection"]["blocked_agents"] + ["curl/", "wget/", "httpie/", "python-requests"]
        if not config["bot_detection"]["allow_developer_tools"]
        else config["bot_detection"]["blocked_agents"]
    )


# Export the configuration
__all__ = [
    "SECURITY_CONFIG",
    "SecurityLevel",
    "get_blocked_user_agents",
    "get_current_environment",
    "get_security_config",
    "is_production",
]
