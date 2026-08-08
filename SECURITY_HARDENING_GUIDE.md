# 🔐 مستندات ایمن‌سازی Econojin

**تاریخ:** ۱۷ مرداد ۱۴۰۵
**نسخه:** ۱.۰

## یافته‌های بحرانی رفع شده

### ۱. بای‌پس احراز هویت (C-1)
- **فایل:** `apps/shared_core/zero_trust_security.py`
- **تغییر:** تابع `_is_local_soft_open()` همیشه `False` برمی‌گرداند
- **تأثیر:** احراز هویت در همه محیط‌ها اجباری است

### ۲. توکن‌های سرویس Hardcoded (C-2)
- **فایل:** `apps/shared_core/zero_trust_security.py`
- **تغییر:** توکن‌ها از متغیرهای محیطی خوانده می‌شوند
- **متغیرها:** `SERVICE_TOKEN_API`, `SERVICE_TOKEN_CMS`, `SERVICE_TOKEN_AI`, `SERVICE_TOKEN_SIM`, `SERVICE_TOKEN_ML`

### ۳. اعتبارسنجی JWT واقعی (C-10)
- **فایل:** `apps/shared_core/zero_trust_security.py`
- **تغییر:** `_verify_token()` حالا JWT را decode و اعتبارسنجی می‌کند

### ۴. حذف فایل‌های حساس (C-6, C-8, C-11)
- `.env.backup` حذف شد
- `.env.docker` از git tracking خارج شد
- `service.py.backup_*` حذف شد

### ۵. حذف کلید Supabase از فرانت‌اند (C-4, C-9)
- `SUPABASE_SECRET_KEY` از `apps/web/.env` و `apps/cms/.env` حذف شد

### ۶. پسوردهای Docker Compose (C-7)
- تمام پسوردهای hardcoded با `${POSTGRES_PASSWORD:-changeme}` جایگزین شدند

## یافته‌های با شدت بالا رفع شده

| # | آسیب‌پذیری | فایل | تغییر |
|---|-----------|------|-------|
| H-1 | User Enumeration | auth_router.py | همیشه verify_password اجرا می‌شود |
| H-2 | نشت /health | main.py | حذف اطلاعات حساس |
| H-3 | /debug/routers عمومی | zero_trust_security.py | از public حذف شد |
| H-4 | /docs عمومی | main.py | در همه محیط‌ها غیرفعال |
| H-5 | Rate limiter ناقص | rate_limit.py | همه تلاش‌ها شمارش می‌شوند |
| H-6 | Middleware تکراری | main.py | حذف ثبت دوبله |

## یافته‌های متوسط رفع شده

| # | آسیب‌پذیری | تغییر |
|---|-----------|-------|
| M-11 | بدون CSP | CSP + X-Frame-Options + nosniff در index.html |
| M-13 | Cookie ناامن | COOKIE_SECURE=true, SameSite=strict |
| H-6-FE | Open Redirect | اعتبارسنجی مسیر redirect در RequireAuth |
| H-7-Infra | Redis بدون رمز | requirepass در همه composeها |
| H-7-Infra | MQTT باز | allow_anonymous false |
| L-4 | رمز ضعیف | complexity: uppercase + lowercase + digit |
| L-9 | توکن منقضی | expiry check در authStore.ts |

## تقویت سیستم امنیتی عنکبوتی

### الگوهای حمله تشخیص داده شده (۶۶ الگو):

| دسته | تعداد | نمونه |
|------|-------|-------|
| SQL Injection | ۱۷ | union select, or 1=1, information_schema |
| XSS | ۱۴ | script, javascript:, onerror, iframe |
| Path Traversal | ۱۰ | ../, ..\, /etc/passwd |
| SSRF | ۱۳ | 169.254.169.254, metadata.google.internal |
| Command Injection | ۱۲ | ; cat, | wget, $(, backtick |

### تابع تشخیص:
`detect_attack_pattern(url_path, query_string, headers) -> str | None`

## متغیرهای محیطی جدید

```env
SERVICE_TOKEN_API=<random-32-char-hex>
SERVICE_TOKEN_CMS=<random-32-char-hex>
SERVICE_TOKEN_AI=<random-32-char-hex>
SERVICE_TOKEN_SIM=<random-32-char-hex>
SERVICE_TOKEN_ML=<random-32-char-hex>
REDIS_PASSWORD=<strong-password>
POSTGRES_PASSWORD=<strong-password>
```

## نحوه آزمایش

```bash
# Test auth is required
curl http://localhost:8000/api/v1/users/me
# Expected: 401

# Test with valid token
curl -H "Authorization: Bearer <jwt>" http://localhost:8000/api/v1/users/me
# Expected: 200

# Test attack detection
curl "http://localhost:8000/api/v1/users?q=' OR 1=1--"
# Expected: 403 (SQL Injection detected)
```
