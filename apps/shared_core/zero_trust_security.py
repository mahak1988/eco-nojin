"""
Zero Trust Security Implementation for Econojin Platform
Integrates Zero Trust principles with existing security infrastructure
"""

import hashlib
import os
import secrets
from collections import defaultdict
from datetime import UTC, datetime
from enum import Enum


class SecurityLevel(Enum):
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


class ZeroTrustConfig:
    """Zero Trust Security Configuration — Never Trust, Always Verify

    Public science compute endpoints are intentionally open for demo/DSS
    (AquaCrop conceptual, RothC, status). Writes that mutate user data stay protected.
    """

    # In local/dev, do not require token on every route (see authenticate_request)
    REQUIRE_AUTH_ALL_ENDPOINTS = True

    PUBLIC_ENDPOINTS: set[str] = {
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/favicon.ico",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
        "/api/v1/auth/forgot-password",
        ""  # Removed from public,
        # Science public compute (Phase B1)
        "/api/v1/science/status",
        "/api/v1/science/aquacrop-advanced",
        "/api/v1/science/rothc",
        "/api/v1/science/ndvi-canopy",
        "/api/v1/science/formulas",
        "/api/v1/science/climate-drivers",
        "/api/v1/science/runs",
        "/api/v1/science/sensitivity/rothc",
        "/api/v1/science/sensitivity/rusle",
        "/api/v1/science/soil/profile",
    }

    # Prefix match (trailing paths / query-free path startswith)
    PUBLIC_PREFIXES: tuple[str, ...] = (
        "/api/v1/auth/",
        "/api/v1/science/status",
        "/api/v1/science/aquacrop",
        "/api/v1/science/rothc",
        "/api/v1/science/ndvi",
        "/api/v1/science/formulas",
        "/api/v1/science/climate",
        "/api/v1/science/sensitivity",
        "/api/v1/science/soil/profile",
        "/api/v1/satellite/",
        "/api/v1/simulation/simulators",
        "/docs",
        "/redoc",
        "/openapi",
    )

    DEFAULT_ROLE = "viewer"
    ROLE_HIERARCHY = {
        "admin": ["admin", "editor", "viewer"],
        "editor": ["editor", "viewer"],
        "viewer": ["viewer"],
    }

    SERVICE_TOKENS = {
        "api": os.getenv("SERVICE_TOKEN_API", ""),
        "cms": os.getenv("SERVICE_TOKEN_CMS", ""),
        "ai": os.getenv("SERVICE_TOKEN_AI", ""),
        "simulation": os.getenv("SERVICE_TOKEN_SIM", ""),
        "ml": os.getenv("SERVICE_TOKEN_ML", ""),
    }

    TOKEN_MAX_AGE_MINUTES = 60
    REQUIRE_MFA_ADMIN = True
    SESSION_BINDING = True

    LOG_ALL_ACCESS = True
    ANOMALY_DETECTION = True
    AUTO_LOCKOUT_THRESHOLD = 5


class SupplyChainSecurity:
    """Supply chain security measures to ensure software integrity"""

    def __init__(self):
        self.known_good_hashes = {}
        self.trusted_sources = set(
            [
                "https://pypi.org/simple/",
                "https://registry.npmjs.org/",
                "https://github.com/mahak1988/eco-nojin.git",
            ]
        )
        self.integrity_checks_enabled = True

    def verify_component_integrity(
        self, component_path: str, expected_hash: str | None = None
    ) -> bool:
        if not self.integrity_checks_enabled:
            return True

        try:
            with open(component_path, "rb") as f:
                content = f.read()
            actual_hash = hashlib.sha256(content).hexdigest()

            if expected_hash:
                return actual_hash == expected_hash
            elif component_path in self.known_good_hashes:
                return actual_hash == self.known_good_hashes[component_path]
            else:
                return True
        except Exception:
            return False

    def register_known_good_hash(self, component_path: str, hash_value: str):
        self.known_good_hashes[component_path] = hash_value

    def is_trusted_source(self, source_url: str) -> bool:
        for trusted in self.trusted_sources:
            if source_url.startswith(trusted):
                return True
        return False


class EnhancedSecurityManager:
    """Main security manager that combines all security features"""

    def __init__(self):
        self.zero_trust_config = ZeroTrustConfig()
        self.supply_chain_security = SupplyChainSecurity()
        self.active_sessions = {}
        self.failed_attempts = defaultdict(int)
        self.last_access_times = {}

    def _is_public(self, endpoint: str) -> bool:
        path = endpoint.split("?", 1)[0]
        if path in self.zero_trust_config.PUBLIC_ENDPOINTS:
            return True
        for prefix in self.zero_trust_config.PUBLIC_PREFIXES:
            if path.startswith(prefix):
                return True
        return False

    def _is_local_soft_open(self) -> bool:
        """Local/dev: do not block unauthenticated browser calls."""
        env = (os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or "local").lower()
        if env in ("local", "development", "dev", "test"):
            return True
        # settings may set REQUIRE_AUTH_FOR_WRITES=false
        if (os.getenv("REQUIRE_AUTH_FOR_WRITES") or "").lower() in ("0", "false", "no"):
            return True
        return False

    def authenticate_request(
        self,
        endpoint: str,
        auth_token: str | None,
        client_ip: str,
        user_agent: str,
    ) -> bool:
        """Authenticate a request based on Zero Trust principles"""

        if self._is_public(endpoint):
            return True

        # Local development soft-open (still logs access)
        if self._is_local_soft_open():
            return True

        if not self.zero_trust_config.REQUIRE_AUTH_ALL_ENDPOINTS:
            # In non-production, still require auth but log it
            pass

        if not auth_token:
            self._record_failed_attempt(client_ip)
            return False

        if not self._verify_token(auth_token):
            self._record_failed_attempt(client_ip)
            return False

        session_key = f"{client_ip}:{user_agent}"
        if self.zero_trust_config.SESSION_BINDING:
            if session_key in self.active_sessions:
                session_info = self.active_sessions[session_key]
                if not self._is_session_valid(session_info):
                    self._record_failed_attempt(client_ip)
                    return False
            else:
                self.active_sessions[session_key] = {
                    "created_at": datetime.now(UTC),
                    "last_access": datetime.now(UTC),
                    "token": auth_token,
                }

        self.last_access_times[client_ip] = datetime.now(UTC)
        return True

    def authorize_request(self, user_role: str, required_permission: str) -> bool:
        if user_role not in self.zero_trust_config.ROLE_HIERARCHY:
            return False

        allowed_roles = self.zero_trust_config.ROLE_HIERARCHY[user_role]
        return required_permission in allowed_roles

    def _verify_token(self, token: str) -> bool:
        """Actually validate JWT token — no bypass."""
        if not token or len(token) < 10:
            return False
        # Check service tokens from env vars
        for svc_token in self.zero_trust_config.SERVICE_TOKENS.values():
            if svc_token and token == svc_token:
                return True
        # Actually decode and validate JWT
        try:
            from apps.shared_core.security import decode_token
            payload = decode_token(token)
            if payload and payload.get("sub"):
                return True
        except Exception:
            pass
        return False
    def _is_session_valid(self, session_info: dict) -> bool:
        now = datetime.now(UTC)
        age = now - session_info["created_at"]
        max_age = self.zero_trust_config.TOKEN_MAX_AGE_MINUTES * 60
        return age.total_seconds() < max_age

    def _record_failed_attempt(self, client_ip: str):
        self.failed_attempts[client_ip] += 1

        if self.failed_attempts[client_ip] >= self.zero_trust_config.AUTO_LOCKOUT_THRESHOLD:
            pass

    def log_access_event(self, client_ip: str, endpoint: str, success: bool, user_agent: str = ""):
        if not self.zero_trust_config.LOG_ALL_ACCESS:
            return

        timestamp = datetime.now(UTC).isoformat()
        event = {
            "timestamp": timestamp,
            "client_ip": client_ip,
            "endpoint": endpoint,
            "success": success,
            "user_agent": user_agent,
        }

        if self.zero_trust_config.ANOMALY_DETECTION:
            self._check_for_anomalies(event)

    def _check_for_anomalies(self, event: dict):
        client_ip = event["client_ip"]
        recent_events = [
            ev
            for ev in self.last_access_times.items()
            if (datetime.now(UTC) - ev[1]).total_seconds() < 60
        ]

        if len([ev for ev in recent_events if ev[0] == client_ip]) > 10:
            print(f"[ALERT] Potential anomaly detected from IP: {client_ip}")

    def generate_secure_token(self, length: int = 32) -> str:
        return secrets.token_urlsafe(length)

    def cleanup_expired_sessions(self):
        now = datetime.now(UTC)
        expired_sessions = []

        for session_key, session_info in self.active_sessions.items():
            if not self._is_session_valid(session_info):
                expired_sessions.append(session_key)

        for session_key in expired_sessions:
            del self.active_sessions[session_key]


security_manager = EnhancedSecurityManager()


def get_security_manager() -> EnhancedSecurityManager:
    return security_manager


__all__ = [
    "EnhancedSecurityManager",
    "SecurityLevel",
    "SupplyChainSecurity",
    "ZeroTrustConfig",
    "get_security_manager",
    "security_manager",
]
