"""
Security Initialization Module
Sets up all security components for the Econojin platform
integrating features from both main apps and eco-nojin project
"""

from .security_config import get_security_config, is_production
from .middleware.security_middleware import SecurityMiddleware
from .security_extended import security_integrator, apply_security_best_practices
from .zero_trust_security import security_manager, ZeroTrustConfig
from apps.spider_security.middleware import SpiderGuardMiddleware
from fastapi import FastAPI, Request
import logging


logger = logging.getLogger(__name__)


def initialize_security(app: FastAPI) -> list:
    """
    Initialize all security components for the application.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        List of security middleware names that were added
    """
    security_stack = []
    
    # Get security configuration
    config = get_security_config()
    
    # Add security middleware from main security module
    app.add_middleware(SecurityMiddleware)
    security_stack.append("SecurityMiddleware")
    logger.info("SecurityMiddleware enabled")
    
    # Add SpiderGuard middleware for bot detection
    app.add_middleware(
        SpiderGuardMiddleware,
        max_requests=config["rate_limiting"]["default_requests_per_minute"],
        window_seconds=config["rate_limiting"]["burst_window_seconds"],
    )
    security_stack.append("SpiderGuardMiddleware")
    logger.info("SpiderGuardMiddleware enabled")
    
    # Apply extended security features
    best_practices = apply_security_best_practices()
    logger.info(f"Applied {len(best_practices)} security best practices")
    
    # Log security configuration
    if is_production():
        logger.info("Production security settings applied")
    else:
        logger.info(f"Development security settings applied (env: {config.get('environment', 'unknown')})")
    
    # Initialize Zero Trust security
    zero_trust_config = ZeroTrustConfig()
    logger.info("Zero Trust security initialized")
    
    return security_stack


def authenticate_request(request: Request) -> bool:
    """
    Authenticate a request using Zero Trust principles.
    
    Args:
        request: FastAPI request object
        
    Returns:
        True if request is authenticated, False otherwise
    """
    endpoint = request.url.path
    auth_token = request.headers.get("authorization", "")
    if auth_token.startswith("Bearer "):
        auth_token = auth_token[7:]
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    
    # Use the security manager to authenticate
    is_authenticated = security_manager.authenticate_request(
        endpoint, auth_token, client_ip, user_agent
    )
    
    # Log the access event
    security_manager.log_access_event(
        client_ip, endpoint, is_authenticated, user_agent
    )
    
    return is_authenticated


def apply_response_security_headers(response_headers: dict) -> dict:
    """
    Apply security headers to response.
    
    Args:
        response_headers: Dictionary of response headers
        
    Returns:
        Updated dictionary with security headers
    """
    config = get_security_config()
    
    # Add security headers from configuration
    response_headers.update(config["security_headers"])
    
    # Remove server header to prevent information disclosure
    if "server" in response_headers:
        del response_headers["server"]
    
    return response_headers


def validate_request_safety(request_data: str) -> bool:
    """
    Validate request data against suspicious patterns.
    
    Args:
        request_data: Request data to validate
        
    Returns:
        True if request is safe, False otherwise
    """
    config = get_security_config()
    
    for pattern in config["input_validation"]["suspicious_patterns"]:
        import re
        if re.search(pattern, request_data, re.IGNORECASE):
            return False
    
    return True


def get_security_monitoring_config():
    """
    Get security monitoring configuration.
    
    Returns:
        Dictionary with monitoring settings
    """
    config = get_security_config()
    return config["monitoring"]


# For backward compatibility
__all__ = [
    'initialize_security',
    'apply_response_security_headers',
    'validate_request_safety',
    'authenticate_request',
    'get_security_monitoring_config'
]