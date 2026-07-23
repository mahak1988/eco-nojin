"""
Econojin Spider Security - Protection Layer
لایه دوم: محافظت در برابر حملات injection و XSS
"""
import re
import html
import os
import logging
from typing import Any, Dict, List, Optional, Union
from functools import wraps

logger = logging.getLogger("econojin.security")


class InputSanitizer:
    """
    پاکسازی ورودی‌ها برای جلوگیری از حملات injection
    """
    
    # الگوهای خطرناک
    DANGEROUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # Script tags
        r"javascript:",  # JavaScript protocol
        r"vbscript:",  # VBScript protocol
        r"on\w+\s*=",  # Event handlers (onclick, onerror, etc.)
        r"<iframe[^>]*>",  # iframe tags
        r"<object[^>]*>",  # object tags
        r"<embed[^>]*>",  # embed tags
        r"<form[^>]*>",  # form tags
        r"expression\s*\(",  # CSS expression
        r"url\s*\(\s*['\"]?javascript:",  # CSS javascript URL
        r"data:text/html",  # Data URI with HTML
        r"<\?php",  # PHP tags
        r"<%",  # ASP tags
    ]
    
    # SQL keywords that might indicate injection
    SQL_KEYWORDS = [
        "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "UNION",
        "ALTER", "CREATE", "TRUNCATE", "EXEC", "EXECUTE",
        "xp_", "sp_", "0x", "CHAR(", "CONCAT(", "BENCHMARK(",
        "SLEEP(", "WAITFOR", "DELAY", "--", ";--", "/*", "*/",
    ]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.DANGEROUS_PATTERNS]
    
    def sanitize_string(self, value: str, context: str = "general") -> str:
        """
        پاکسازی یک رشته ورودی
        
        Args:
            value: رشته ورودی
            context: زمینه استفاده (general, sql, html, url)
        
        Returns:
            رشته پاکسازی شده
        """
        if not isinstance(value, str):
            return value
        
        original = value
        
        # حذف null bytes
        value = value.replace("\x00", "")
        
        # حذف یا encoding کاراکترهای خاص
        if context == "html":
            value = html.escape(value)
        
        # بررسی الگوهای خطرناک
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                logger.warning(f"🚨 Dangerous pattern detected in input: {pattern.pattern}")
                value = pattern.sub("", value)
        
        # Trim whitespace
        value = value.strip()
        
        # Limit length
        max_length = int(os.getenv("MAX_INPUT_LENGTH", "10000"))
        if len(value) > max_length:
            logger.warning(f"⚠️ Input truncated from {len(original)} to {max_length} chars")
            value = value[:max_length]
        
        return value
    
    def sanitize_dict(self, data: Dict[str, Any], context: str = "general") -> Dict[str, Any]:
        """
        پاکسازی تمام مقادیر در یک دیکشنری
        """
        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            clean_key = self.sanitize_string(str(key), "general")
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[clean_key] = self.sanitize_string(value, context)
            elif isinstance(value, dict):
                sanitized[clean_key] = self.sanitize_dict(value, context)
            elif isinstance(value, list):
                sanitized[clean_key] = [
                    self.sanitize_string(v, context) if isinstance(v, str) else v
                    for v in value
                ]
            else:
                sanitized[clean_key] = value
        
        return sanitized
    
    def contains_sql_injection(self, value: str) -> bool:
        """
        بررسی وجود SQL Injection در ورودی
        """
        if not isinstance(value, str):
            return False
        
        value_upper = value.upper()
        
        # بررسی کلمات کلیدی SQL
        for keyword in self.SQL_KEYWORDS:
            if keyword in value_upper:
                # بررسی ترکیبات خطرناک
                if any(
                    dangerous in value 
                    for dangerous in ["'", '"', "--", ";", "/*", "*/", "xp_", "sp_"]
                ):
                    logger.warning(f"🚨 Potential SQL Injection detected: {keyword}")
                    return True
        
        # بررسی الگوهای SQL Injection معروف
        sql_patterns = [
            r"'\s*OR\s+'1'\s*=\s*'1",  # ' OR '1'='1
            r"'\s*OR\s+1\s*=\s*1",  # ' OR 1=1
            r";\s*DROP\s+TABLE",  # ; DROP TABLE
            r"UNION\s+SELECT",  # UNION SELECT
            r"'\s*;\s*--",  # '; --
            r"'\s*OR\s*''='",  # ' OR ''='
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"🚨 SQL Injection pattern detected: {pattern}")
                return True
        
        return False


class SQLInjectionProtector:
    """
    محافظت در برابر SQL Injection
    """
    
    def __init__(self):
        self.sanitizer = InputSanitizer()
    
    def validate_query_params(self, params: Dict[str, Any]) -> bool:
        """
        اعتبارسنجی پارامترهای query برای جلوگیری از SQL Injection
        """
        for key, value in params.items():
            if isinstance(value, str):
                if self.sanitizer.contains_sql_injection(value):
                    logger.critical(f"🚨 SQL Injection attempt blocked in param '{key}'")
                    return False
        return True
    
    def protect_query(self, query: str, params: Optional[Dict] = None) -> tuple[str, bool]:
        """
        محافظت از query SQL
        
        Returns:
            tuple: (query_pakshirafeh, is_safe)
        """
        if params:
            if not self.validate_query_params(params):
                return "", False
        
        # بررسی خود query
        if self.sanitizer.contains_sql_injection(query):
            logger.critical("🚨 SQL Injection attempt blocked in query")
            return "", False
        
        return query, True


class XSSProtector:
    """
    محافظت در برابر Cross-Site Scripting (XSS)
    """
    
    def __init__(self):
        self.sanitizer = InputSanitizer()
    
    def sanitize_output(self, content: str, allow_html: bool = False) -> str:
        """
        پاکسازی خروجی برای جلوگیری از XSS
        
        Args:
            content: محتوای خروجی
            allow_html: آیا HTML مجاز است؟
        
        Returns:
            محتوای پاکسازی شده
        """
        if not isinstance(content, str):
            return content
        
        if allow_html:
            # فقط تگ‌های امن را مجاز بدان
            allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li']
            # TODO: Implement proper HTML sanitization with whitelist
            return self.sanitizer.sanitize_string(content, "html")
        else:
            # Escape all HTML
            return html.escape(content)
    
    def validate_json_body(self, data: Dict[str, Any]) -> bool:
        """
        اعتبارسنجی بدنه JSON برای جلوگیری از XSS
        """
        def check_value(value: Any) -> bool:
            if isinstance(value, str):
                # بررسی اسکریپت‌ها
                dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onclick=']
                for pattern in dangerous_patterns:
                    if pattern.lower() in value.lower():
                        logger.warning(f"🚨 XSS pattern detected: {pattern}")
                        return False
            elif isinstance(value, dict):
                return all(check_value(v) for v in value.values())
            elif isinstance(value, list):
                return all(check_value(v) for v in value)
            return True
        
        return check_value(data)


class CSRFProtector:
    """
    محافظت در برابر Cross-Site Request Forgery (CSRF)
    """
    
    def __init__(self):
        self.secret_key = os.getenv("CSRF_SECRET_KEY", os.getenv("SECRET_KEY", "fallback-secret-key"))
        self.token_lifetime = int(os.getenv("CSRF_TOKEN_LIFETIME", "3600"))  # 1 hour
    
    def generate_token(self, session_id: str) -> str:
        """
        تولید توکن CSRF
        """
        import hashlib
        import time
        
        timestamp = int(time.time())
        token_data = f"{session_id}:{timestamp}:{self.secret_key}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        
        return f"{timestamp}:{token_hash}"
    
    def validate_token(self, token: str, session_id: str) -> bool:
        """
        اعتبارسنجی توکن CSRF
        """
        import time
        import hashlib
        
        try:
            timestamp_str, provided_hash = token.split(":")
            timestamp = int(timestamp_str)
            
            # بررسی انقضا
            current_time = int(time.time())
            if current_time - timestamp > self.token_lifetime:
                logger.warning("🚨 CSRF token expired")
                return False
            
            # بازسازی و مقایسه hash
            token_data = f"{session_id}:{timestamp}:{self.secret_key}"
            expected_hash = hashlib.sha256(token_data.encode()).hexdigest()
            
            if provided_hash != expected_hash:
                logger.warning("🚨 CSRF token mismatch")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"CSRF validation error: {e}")
            return False
    
    def get_token_from_request(self, headers: Dict[str, str], body: Dict[str, Any]) -> Optional[str]:
        """
        استخراج توکن CSRF از درخواست
        """
        # بررسی header
        token = headers.get("X-CSRF-Token") or headers.get("x-csrf-token")
        
        # بررسی body
        if not token and body:
            token = body.get("csrf_token") or body.get("_csrf")
        
        return token


def csrf_protect(func):
    """
    Decorator برای محافظت CSRF روی endpointها
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract request from args or kwargs
        request = kwargs.get('request') or (args[0] if args else None)
        
        if request:
            # Only check for state-changing methods
            if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
                csrf = CSRFProtector()
                
                # Get token from request
                token = csrf.get_token_from_request(
                    dict(request.headers),
                    getattr(request, "state", {})
                )
                
                # Skip validation if no token (let endpoint handle it)
                if token:
                    session_id = getattr(request, "session", {}).get("id", "default")
                    if not csrf.validate_token(token, session_id):
                        from fastapi import HTTPException, status
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid CSRF token"
                        )
        
        return await func(*args, **kwargs)
    
    return wrapper
