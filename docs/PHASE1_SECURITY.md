# فاز ۱ — امنیت و Hardening (اجرایی)

**وضعیت:** پیاده‌سازی در مخزن (2026-07-30)  
**محیط:** Zero-Install (بدون نیاز به کلید بیرونی)

## تحویل‌پذیرها

| آیتم | فایل / رفتار |
|------|----------------|
| Rate limit auth | `ENABLE_RATE_LIMIT=true` (پیش‌فرض) — `RateLimitMiddleware` |
| Audit log | `ENABLE_AUDIT_LOG=true` — لاگ JSON مسیرهای `/auth` |
| SpiderGuard | پیش‌فرض **خاموش** در local؛ روشن در production یا `ENABLE_SPIDERGUARD=true` |
| curl دیگر bot نیست | الگوهای UA فقط crawler واقعی |
| JWT secret از Settings | بدون hardcode در service |
| تولید کلید | `scripts/gen_jwt_keys.ps1` / `.sh` |
| health.security | stack + flags |
| CI bandit | `.github/workflows/security-bandit.yml` |

## env پیشنهادی local

```env
ENABLE_RATE_LIMIT=true
ENABLE_AUDIT_LOG=true
ENABLE_SPIDERGUARD=false
AUTH_RATE_LIMIT_MAX=10
AUTH_RATE_LIMIT_WINDOW_SECONDS=60
REQUIRE_AUTH_FOR_WRITES=false
ALGORITHM=HS256
```

Production:

```env
ENVIRONMENT=production
REQUIRE_AUTH_FOR_WRITES=true
ENABLE_SPIDERGUARD=true
ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=./secrets/jwt_private.pem
JWT_PUBLIC_KEY_PATH=./secrets/jwt_public.pem
COOKIE_SECURE=true
```

## تأیید بعد از pull

```powershell
cd D:\econojin.com
git pull origin main
.\scripts\run_local.ps1
# ترمینال دیگر:
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/health
```

در JSON باید `security.rate_limit: true` و `security.stack` شامل `RateLimitMiddleware` باشد.

## معیار پذیرش فاز ۱

- [x] Middleware امنیتی از env قابل کنترل
- [x] local بدون بلاک curl
- [x] اسکریپت تولید SECRET/RS256
- [x] مستند KEY_ROTATION موجود
- [x] bandit workflow
- [ ] کاربر: `git pull` + restart و چک health.security
