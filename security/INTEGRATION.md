# Integration Guide

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
