# Spider Web Security Policy - econojin.com

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
