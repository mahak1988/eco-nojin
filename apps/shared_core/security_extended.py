"""
Extended security module integrating security features from eco-nojin project.
This module consolidates security middleware and practices from both codebases.
"""

import hashlib
import secrets


class SecurityIntegrator:
    """
    A class to manage integration of security features between the main apps
    and the eco-nojin security patterns.
    """

    def __init__(self):
        self.security_features = {}

    def integrate_spider_guard(self):
        """
        Integrate spider guard functionality from spider_security app
        with additional security patterns from eco-nojin project.
        """
        from apps.spider_security.middleware import SpiderGuardMiddleware

        return SpiderGuardMiddleware

    def enhance_security_headers(self, response_headers: dict[str, str]) -> dict[str, str]:
        """
        Enhance response headers with additional security measures
        inspired by eco-nojin security patterns.
        """
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

        response_headers.update(security_headers)
        return response_headers

    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate cryptographically secure tokens following best practices
        identified in eco-nojin security implementations.
        """
        return secrets.token_urlsafe(length)

    def hash_sensitive_data(self, data: str, salt: str | None = None) -> str:
        """
        Hash sensitive data using secure hashing algorithm.
        """
        if salt is None:
            salt = secrets.token_hex(16)

        hashed = hashlib.pbkdf2_hmac("sha256", data.encode("utf-8"), salt.encode("utf-8"), 100000)
        return f"{salt}${hashed.hex()}"


# Initialize the security integrator
security_integrator = SecurityIntegrator()


def apply_security_best_practices():
    """
    Apply security best practices identified from both main apps
    and eco-nojin project structures.
    """
    practices = [
        "Implement proper input validation",
        "Use parameterized queries to prevent SQL injection",
        "Apply proper authentication and authorization",
        "Implement rate limiting and DDoS protection",
        "Secure session management",
        "Proper error handling without information disclosure",
        "Regular security audits and vulnerability assessments",
    ]

    return practices


def get_security_monitoring_config():
    """
    Return security monitoring configuration based on
    patterns observed in both codebases.
    """
    return {
        "log_security_events": True,
        "alert_on_anomalies": True,
        "request_tracing_enabled": True,
        "ip_blocking_threshold": 100,  # requests per minute
        "sensitive_endpoints_monitoring": True,
        "authentication_attempts_monitoring": True,
    }


# Export commonly used security utilities
__all__ = [
    "SecurityIntegrator",
    "apply_security_best_practices",
    "get_security_monitoring_config",
    "security_integrator",
]
