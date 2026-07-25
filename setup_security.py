#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
setup_security.py — Spider Web Security Architecture (8 Layers)
'''
from __future__ import annotations
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEC = ROOT / 'security'

def w(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    print(f'  + {rel}')

def main() -> int:
    apply = '--apply' in sys.argv
    print('=' * 60)
    print('  Spider Web Security Architecture')
    print('=' * 60)
    if not apply:
        print('  Report mode. Run with --apply')
        return 0

    # ── Layer 2: Nginx Security Headers ──
    w('security/nginx/security-headers.conf', '''
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://*.supabase.co https://*.qdrant.io; frame-ancestors 'self';" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=(self), payment=()" always;
server_tokens off;
proxy_hide_header X-Powered-By;
''')

    # ── Layer 2: Nginx Rate Limit & Anti-Bot ──
    w('security/nginx/rate-limit.conf', '''
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=general_limit:10m rate=30r/s;
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

map $http_user_agent $blocked_agent {
    default 0;
    ~*(sqlmap|nikto|nmap|masscan|dirbuster|gobuster|wfuzz|hydra|burp|zap) 1;
    ~*(python-requests|curl|wget|scrapy|bot|crawler|spider) 1;
    "" 1;
}

client_max_body_size 10m;
client_body_buffer_size 128k;
client_header_buffer_size 1k;
large_client_header_buffers 4 8k;
client_body_timeout 12;
client_header_timeout 12;
keepalive_timeout 15;
send_timeout 10;
''')

    # ── Layer 2: Nginx Anti-Phishing ──
    w('security/nginx/anti-phishing.conf', '''
location ~* "(\\.|%2e)(\\.|%2e)(%2f|/)" { return 403; }
location ~* "(union|select|insert|drop|delete|update|cast|create|exec|script)" { return 403; }
location ~* "(<script|javascript:|vbscript:|onload=|onerror=)" { return 403; }
location ~* "\\.(env|git|svn|htaccess|htpasswd|ini|log|bak|sql|conf)$" { deny all; return 404; }
location ~* "/(\\.git|\\.env|\\.svn|node_modules|__pycache__)" { deny all; return 404; }
if ($request_method !~ ^(GET|POST|PUT|PATCH|DELETE|OPTIONS)$) { return 405; }
''')

    # ── Layer 3-4: FastAPI Security Middleware ──
    w('security/middleware/__init__.py', '"""Spider Web Security Middleware."""\n')

    w('security/middleware/security_middleware.py', '''
"""Spider Web Security - FastAPI Security Middleware (Layers 3-4)."""
from __future__ import annotations
import re, time
from collections import defaultdict
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

CONFIG = {
    "rate_limit_per_minute": 60,
    "rate_limit_login_per_minute": 5,
    "max_request_size": 10 * 1024 * 1024,
    "blocked_agents": ["sqlmap","nikto","nmap","masscan","dirbuster",
                       "gobuster","wfuzz","hydra","burp","zap","scrapy"],
    "suspicious_patterns": [
        r"(?i)(union\\s+select|insert\\s+into|drop\\s+table|delete\\s+from)",
        r"(?i)(<script|javascript:|vbscript:|on\\w+\\s*=)",
        r"(?i)(\\.\\./|\\.\\.\\\\|%2e%2e)",
        r"(?i)(cmd\\.exe|/bin/sh|/bin/bash|powershell)",
    ],
    "security_headers": {
        "X-Frame-Options": "SAMEORIGIN",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Cache-Control": "no-store, no-cache, must-revalidate",
    },
}

class RateLimiter:
    def __init__(self):
        self._req = defaultdict(list)
    def allowed(self, key: str, limit: int, window: int = 60) -> bool:
        now = time.time()
        self._req[key] = [t for t in self._req[key] if now - t < window]
        if len(self._req[key]) >= limit:
            return False
        self._req[key].append(now)
        return True

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, config=None):
        super().__init__(app)
        self.cfg = config or CONFIG
        self.rl = RateLimiter()
        self._patterns = [re.compile(p) for p in self.cfg["suspicious_patterns"]]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        ip = request.client.host if request.client else "unknown"
        ua = (request.headers.get("user-agent") or "").lower()
        if not ua:
            return JSONResponse(status_code=403, content={"detail": "User-Agent required"})
        for b in self.cfg["blocked_agents"]:
            if b in ua:
                return JSONResponse(status_code=403, content={"detail": "Access denied"})
        is_login = "/login" in request.url.path or "/auth" in request.url.path
        limit = self.cfg["rate_limit_login_per_minute"] if is_login else self.cfg["rate_limit_per_minute"]
        if not self.rl.allowed(ip, limit):
            return JSONResponse(status_code=429, content={"detail": "Too many requests"},
                                headers={"Retry-After": "60"})
        cl = request.headers.get("content-length")
        if cl and int(cl) > self.cfg["max_request_size"]:
            return JSONResponse(status_code=413, content={"detail": "Request too large"})
        check = f"{request.url.path}?{request.query_params}"
        for pat in self._patterns:
            if pat.search(check):
                return JSONResponse(status_code=403, content={"detail": "Suspicious request"})
        response = await call_next(request)
        for h, v in self.cfg["security_headers"].items():
            response.headers[h] = v
        response.headers.pop("server", None)
        return response
''')

    # ── Layer 4: Anti-Phishing ──
    w('security/middleware/anti_phishing.py', '''
"""Spider Web Security - Anti-Phishing Protection."""
from __future__ import annotations
import re
from urllib.parse import urlparse

class AntiPhishingGuard:
    ALLOWED_DOMAINS = {"econojin.com","www.econojin.com","supabase.co","qdrant.io","github.com"}
    SUSPICIOUS_TLDS = {".tk",".ml",".ga",".cf",".gq",".xyz",".top",".work",".click"}

    @classmethod
    def is_suspicious_url(cls, url: str) -> tuple[bool, str]:
        try:
            parsed = urlparse(url)
        except Exception:
            return True, "Invalid URL"
        host = parsed.hostname or ""
        if host and not any(host.endswith(d) for d in cls.ALLOWED_DOMAINS):
            for tld in cls.SUSPICIOUS_TLDS:
                if host.endswith(tld):
                    return True, f"Suspicious TLD: {tld}"
        if re.match(r"^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$", host):
            return True, "IP instead of domain"
        if "@" in url or "%00" in url:
            return True, "Suspicious characters"
        return False, ""

    @classmethod
    def sanitize_input(cls, text: str) -> str:
        for url in re.findall(r"https?://[^\\s<>\\"]+", text):
            bad, _ = cls.is_suspicious_url(url)
            if bad:
                text = text.replace(url, "[URL-removed]")
        return text
''')

    # ── Layer 6: AI Security ──
    w('security/middleware/ai_security.py', '''
"""Spider Web Security - AI/LLM Prompt Injection Prevention."""
from __future__ import annotations
import re

class AISecurityGuard:
    INJECTION = [
        re.compile(r"(?i)ignore\\s+(all\\s+)?previous\\s+instructions"),
        re.compile(r"(?i)disregard\\s+(all\\s+)?(prior|previous|above)"),
        re.compile(r"(?i)you\\s+are\\s+now\\s+(a|an|the)"),
        re.compile(r"(?i)system\\s*:\\s*"),
        re.compile(r"(?i)\\[\\s*INST\\s*\\]"),
        re.compile(r"(?i)<\\s*/?\\s*system\\s*>"),
        re.compile(r"(?i)pretend\\s+(you|to\\s+be)"),
        re.compile(r"(?i)jailbreak|DAN\\s+mode|developer\\s+mode"),
    ]
    OUTPUT = [
        re.compile(r"(?i)(api[_-]?key|secret[_-]?key|password|token)\\s*[:=]"),
        re.compile(r"(?i)postgresql://[^\\s]+"),
        re.compile(r"(?i)sk-[a-zA-Z0-9]{20,}"),
        re.compile(r"(?i)ghp_[a-zA-Z0-9]{36}"),
    ]

    @classmethod
    def detect_injection(cls, prompt: str) -> tuple[bool, str]:
        for p in cls.INJECTION:
            if p.search(prompt):
                return True, "Prompt injection detected"
        return False, ""

    @classmethod
    def sanitize_prompt(cls, prompt: str) -> str:
        s = prompt
        for p in cls.INJECTION:
            s = p.sub("[FILTERED]", s)
        return s[:10000]

    @classmethod
    def filter_output(cls, output: str) -> str:
        s = output
        for p in cls.OUTPUT:
            s = p.sub("[REDACTED]", s)
        return s
''')

    # ── Layer 7: Security Config ──
    w('security/config.py', '''
"""Spider Web Security - Central Configuration."""
from __future__ import annotations
import os

class SecurityConfig:
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    PASSWORD_MIN_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    RATE_LIMIT_API = 60
    RATE_LIMIT_LOGIN = 5
    RATE_LIMIT_AI_CHAT = 20
    ALLOWED_ORIGINS = [
        "https://econojin.com", "https://www.econojin.com",
        "http://localhost:5173", "http://localhost:3000",
    ]
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {".png",".jpg",".jpeg",".gif",".pdf",".csv",".json"}
    HSTS_MAX_AGE = 31536000
''')

    # ── Layer 1: Cloudflare WAF ──
    w('security/cloudflare/waf-rules.json', '''
{
  "rules": [
    {"name":"Block SQLi","action":"block","expression":"(http.request.uri.query contains \\"union select\\") or (http.request.uri.query contains \\"drop table\\")"},
    {"name":"Block XSS","action":"block","expression":"(http.request.uri.query contains \\"<script\\")"},
    {"name":"Block Traversal","action":"block","expression":"(http.request.uri contains \\"../\\")"},
    {"name":"Rate Limit Login","action":"rate_limit","expression":"(http.request.uri.path contains \\"/login\\")"},
    {"name":"Block Bots","action":"block","expression":"(http.user_agent contains \\"sqlmap\\") or (http.user_agent contains \\"nikto\\")"},
    {"name":"Block Sensitive","action":"block","expression":"(http.request.uri.path ends_with \\".env\\") or (http.request.uri.path contains \\"/.git/\\")"}
  ]
}
''')

    # ── Security Audit ──
    w('security/audit.py', '''
#!/usr/bin/env python3
"""Spider Web Security - Automated Audit."""
from __future__ import annotations
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main() -> int:
    print("=" * 60)
    print("  Spider Web Security Audit")
    print("=" * 60)
    issues = []
    gi = ROOT / ".gitignore"
    if gi.exists():
        c = gi.read_text(encoding="utf-8")
        for p in [".env", "*.pem", "*.key"]:
            if p not in c:
                issues.append(f"WARN: {p} not in .gitignore")
    for f in ["security/middleware/security_middleware.py",
              "security/middleware/anti_phishing.py",
              "security/middleware/ai_security.py",
              "security/config.py",
              "security/nginx/security-headers.conf"]:
        if not (ROOT / f).exists():
            issues.append(f"MISSING: {f}")
    env = ROOT / ".env"
    if env.exists():
        c = env.read_text(encoding="utf-8")
        if re.search(r"(?i)(password|secret|key)\\s*=\\s*(changeme|password|123456|admin)", c):
            issues.append("CRITICAL: weak password in .env")
    crit = len([i for i in issues if i.startswith("CRITICAL")])
    warn = len([i for i in issues if i.startswith("WARN")])
    miss = len([i for i in issues if i.startswith("MISSING")])
    for i in issues:
        print(f"  {i}")
    if not issues:
        print("  All checks passed")
    print(f"\\n  Summary: {crit} critical | {warn} warn | {miss} missing")
    return 1 if crit else 0

if __name__ == "__main__":
    sys.exit(main())
''')

    # ── Security Policy ──
    w('security/SECURITY_POLICY.md', '''# Spider Web Security Policy - econojin.com

## 8-Layer Defense Architecture

| Layer | Name | Technology |
|-------|------|------------|
| 1 | Edge | Cloudflare WAF + DDoS |
| 2 | Proxy | Nginx (Headers, Rate Limit, Anti-Bot) |
| 3 | Gateway | FastAPI (JWT, RBAC, CORS) |
| 4 | Middleware | Anti-Bot, Anti-Phishing, Input Validation |
| 5 | Application | Secure Code, Error Handling |
| 6 | AI Security | Prompt Injection Prevention |
| 7 | Data | Encryption, Access Control |
| 8 | Contract | ReentrancyGuard, AccessControl |

## Policies
- Password: min 8 chars, upper+lower+digit+special, bcrypt/argon2
- Rate Limit: API 60/min, Login 5/min, AI 20/min
- Anti-Bot: UA blocking, IP rate limit, CAPTCHA
- Anti-Phishing: URL validation, TLD filter, CSP
- Anti-Injection: Pydantic validation, parameterized queries
- Report: security@econojin.com
''')

    # ── Integration Guide ──
    w('security/INTEGRATION.md', '''# Integration Guide

## FastAPI
    from security.middleware.security_middleware import SecurityMiddleware
    app.add_middleware(SecurityMiddleware)

## Nginx
    include /etc/nginx/security/security-headers.conf;
    include /etc/nginx/security/rate-limit.conf;
    include /etc/nginx/security/anti-phishing.conf;

## AI Agents
    from security.middleware.ai_security import AISecurityGuard
    ok, reason = AISecurityGuard.detect_injection(user_input)
    if ok: return {"error": "Invalid input"}
    safe = AISecurityGuard.sanitize_prompt(user_input)
    output = AISecurityGuard.filter_output(llm.invoke(safe))
''')

    # ── Run audit ──
    print('\\n' + '-' * 60)
    print('  Running audit...')
    subprocess.run([sys.executable, str(SEC / 'audit.py')], cwd=ROOT)

    print('\\n' + '=' * 60)
    print('  Done! Next:')
    print('     git add security/')
    print('     git commit -m "security: spider web architecture (8 layers)"')
    print('     git push')
    print('=' * 60)
    return 0

if __name__ == '__main__':
    sys.exit(main())