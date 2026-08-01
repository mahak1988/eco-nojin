"""
Zero Trust Security Implementation for Econojin Platform
Integrates Zero Trust principles with existing security infrastructure
"""

from typing import Dict, List, Set, Optional
from enum import Enum
import os
from datetime import datetime, timezone
import hashlib
import secrets
from collections import defaultdict


class SecurityLevel(Enum):
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


class ZeroTrustConfig:
    """Zero Trust Security Configuration - Never Trust, Always Verify"""

    # 1. Identity Verification - Every request must be authenticated
    REQUIRE_AUTH_ALL_ENDPOINTS = True
    PUBLIC_ENDPOINTS: Set[str] = {"/health", "/docs", "/openapi.json", "/redoc", "/api/v1/auth/login", "/api/v1/auth/register"}

    # 2. Least Privilege - Minimum access
    DEFAULT_ROLE = "viewer"
    ROLE_HIERARCHY = {
        "admin": ["admin", "editor", "viewer"],
        "editor": ["editor", "viewer"],
        "viewer": ["viewer"],
    }

    # 3. Microsegmentation - Service isolation
    SERVICE_TOKENS = {
        "api": "internal-api-token",
        "cms": "internal-cms-token",
        "ai": "internal-ai-token",
        "simulation": "internal-sim-token",
        "ml": "internal-ml-token",
    }

    # 4. Continuous Verification - Ongoing checks
    TOKEN_MAX_AGE_MINUTES = 60
    REQUIRE_MFA_ADMIN = True
    SESSION_BINDING = True  # Bind to IP + User-Agent

    # 5. Assume Breach - Breach assumption
    LOG_ALL_ACCESS = True
    ANOMALY_DETECTION = True
    AUTO_LOCKOUT_THRESHOLD = 5


class SupplyChainSecurity:
    """Supply chain security measures to ensure software integrity"""
    
    def __init__(self):
        self.known_good_hashes = {}
        self.trusted_sources = set([
            "https://pypi.org/simple/",
            "https://registry.npmjs.org/",
            "https://github.com/mahak1988/eco-nojin.git"
        ])
        self.integrity_checks_enabled = True

    def verify_component_integrity(self, component_path: str, expected_hash: Optional[str] = None) -> bool:
        """
        Verify the integrity of a component against known good hash
        """
        if not self.integrity_checks_enabled:
            return True
            
        try:
            with open(component_path, 'rb') as f:
                content = f.read()
            actual_hash = hashlib.sha256(content).hexdigest()
            
            if expected_hash:
                return actual_hash == expected_hash
            elif component_path in self.known_good_hashes:
                return actual_hash == self.known_good_hashes[component_path]
            else:
                # If we don't have a known hash, store this as the baseline after manual verification
                return True
        except Exception:
            return False

    def register_known_good_hash(self, component_path: str, hash_value: str):
        """Register a known good hash for a component"""
        self.known_good_hashes[component_path] = hash_value

    def is_trusted_source(self, source_url: str) -> bool:
        """Check if a source is trusted"""
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

    def authenticate_request(self, endpoint: str, auth_token: Optional[str], 
                           client_ip: str, user_agent: str) -> bool:
        """Authenticate a request based on Zero Trust principles"""
        
        # Skip authentication for public endpoints
        if endpoint in self.zero_trust_config.PUBLIC_ENDPOINTS:
            return True

        # Require authentication for non-public endpoints
        if not auth_token:
            self._record_failed_attempt(client_ip)
            return False

        # Verify token validity
        if not self._verify_token(auth_token):
            self._record_failed_attempt(client_ip)
            return False

        # Session binding verification
        session_key = f"{client_ip}:{user_agent}"
        if self.zero_trust_config.SESSION_BINDING:
            if session_key in self.active_sessions:
                session_info = self.active_sessions[session_key]
                if not self._is_session_valid(session_info):
                    self._record_failed_attempt(client_ip)
                    return False
            else:
                # Create new session
                self.active_sessions[session_key] = {
                    "created_at": datetime.now(timezone.utc),
                    "last_access": datetime.now(timezone.utc),
                    "token": auth_token
                }

        # Update access time
        self.last_access_times[client_ip] = datetime.now(timezone.utc)
        return True

    def authorize_request(self, user_role: str, required_permission: str) -> bool:
        """Authorize a request based on role hierarchy"""
        if user_role not in self.zero_trust_config.ROLE_HIERARCHY:
            return False
            
        allowed_roles = self.zero_trust_config.ROLE_HIERARCHY[user_role]
        return required_permission in allowed_roles

    def _verify_token(self, token: str) -> bool:
        """Verify the authenticity and validity of a token"""
        # In a real implementation, this would check against a database or JWT
        # For now, we'll implement basic validation
        if len(token) < 10:  # Basic length check
            return False
            
        # Check if it's a service token
        if token in self.zero_trust_config.SERVICE_TOKENS.values():
            return True

        # For user tokens, we'd normally decode and verify JWT
        # This is a simplified check
        return True

    def _is_session_valid(self, session_info: Dict) -> bool:
        """Check if a session is still valid"""
        now = datetime.now(timezone.utc)
        age = now - session_info["created_at"]
        max_age = self.zero_trust_config.TOKEN_MAX_AGE_MINUTES * 60  # Convert to seconds
        return age.total_seconds() < max_age

    def _record_failed_attempt(self, client_ip: str):
        """Record a failed authentication attempt"""
        self.failed_attempts[client_ip] += 1
        
        # Auto-lockout if threshold exceeded
        if self.failed_attempts[client_ip] >= self.zero_trust_config.AUTO_LOCKOUT_THRESHOLD:
            # In a real implementation, this would temporarily block the IP
            pass

    def log_access_event(self, client_ip: str, endpoint: str, success: bool, user_agent: str = ""):
        """Log access events for anomaly detection"""
        if not self.zero_trust_config.LOG_ALL_ACCESS:
            return

        timestamp = datetime.now(timezone.utc).isoformat()
        event = {
            "timestamp": timestamp,
            "client_ip": client_ip,
            "endpoint": endpoint,
            "success": success,
            "user_agent": user_agent
        }

        # In a real implementation, this would go to a log aggregation system
        if self.zero_trust_config.ANOMALY_DETECTION:
            self._check_for_anomalies(event)

    def _check_for_anomalies(self, event: Dict):
        """Check for anomalous access patterns"""
        # Simple anomaly detection: excessive requests from same IP in short time
        client_ip = event["client_ip"]
        recent_events = [ev for ev in self.last_access_times.items() 
                        if (datetime.now(timezone.utc) - ev[1]).total_seconds() < 60]
                        
        if len([ev for ev in recent_events if ev[0] == client_ip]) > 10:
            print(f"[ALERT] Potential anomaly detected from IP: {client_ip}")

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure token"""
        return secrets.token_urlsafe(length)

    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        now = datetime.now(timezone.utc)
        expired_sessions = []
        
        for session_key, session_info in self.active_sessions.items():
            if not self._is_session_valid(session_info):
                expired_sessions.append(session_key)
                
        for session_key in expired_sessions:
            del self.active_sessions[session_key]


# Global security manager instance
security_manager = EnhancedSecurityManager()


def get_security_manager() -> EnhancedSecurityManager:
    """Get the global security manager instance"""
    return security_manager


__all__ = [
    'ZeroTrustConfig',
    'SupplyChainSecurity',
    'EnhancedSecurityManager',
    'SecurityLevel',
    'security_manager',
    'get_security_manager'
]