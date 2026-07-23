# امنیت چندلایه عنکبوتی Econojin

## 🕸️ سیستم امنیت عنکبوتی (نسخه جدید)

این سند مستندات کامل سیستم امنیت چندلایه عنکبوتی است که به‌تازگی به پروژه Econojin اضافه شده است.

### معماری لایه‌ها

## لایه ۱ — Middlewareهای امنیتی (`apps/shared_core/security/middleware.py`)

### SecurityHeadersMiddleware
- `X-Frame-Options: DENY` - جلوگیری از Clickjacking
- `X-Content-Type-Options: nosniff` - جلوگیری از MIME Sniffing
- `X-XSS-Protection: 1; mode=block` - فعال‌سازی XSS Filter
- `Content-Security-Policy` - محدود کردن منابع قابل اعتماد
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security` - اجبار HTTPS (production)
- `Permissions-Policy` - محدود کردن ویژگی‌های مرورگر
- حذف هدرهای حساس (`Server`, `X-Powered-By`)

### RateLimitMiddleware
- محدودیت پیش‌فرض: ۱۲۰ درخواست در دقیقه per IP
- محدودیت شدید برای endpointهای حساس: ۱۰ درخواست در دقیقه
  - `/api/v1/auth/login`
  - `/api/v1/auth/register`
  - `/api/v1/users`
- الگوریتم Sliding Window
- هدرهای informative: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### HoneypotMiddleware (تله عنکبوتی)
- مسیرهای honeypot شامل:
  - `/admin`, `/wp-admin`, `/phpmyadmin`
  - `/.env`, `/.git/config`
  - `/backup.sql`, `/database.sql`
  - `/config.php`, `/wp-login.php`
  - و سایر مسیرهای حساس جعلی
- مسدود کردن خودکار IP بعد از ۳ تخلف
- لاگ کامل فعالیت‌ها در `HONEYPOT_LOG_FILE`

### SpiderSecurityMiddleware
- ترکیب تمام لایه‌های امنیتی
- مدیریت لیست سیاه IPها در `SECURITY_BLACKLIST_FILE`
- پشتیبانی از لیست سفید (`SECURITY_WHITELIST_IPS`)
- تصمیم‌گیری هوشمند برای مسدودسازی

---

## لایه ۲ — محافظت در برابر Injection (`apps/shared_core/security/protection.py`)

### InputSanitizer
- پاکسازی Script Tags و JavaScript Protocol
- حذف Event Handlerها (onclick, onerror, etc.)
- محدود کردن طول ورودی‌ها (`MAX_INPUT_LENGTH`)
- پاکسازی دیکشنری‌ها و لیست‌ها

### SQLInjectionProtector
- تشخیص کلمات کلیدی SQL خطرناک
- بررسی الگوهای معروف SQL Injection:
  - `' OR '1'='1`
  - `UNION SELECT`
  - `; DROP TABLE`
- اعتبارسنجی پارامترهای query

### XSSProtector
- HTML Escape برای خروجی‌ها
- اعتبارسنجی بدنه JSON
- تشخیص اسکریپت‌های مخرب

### CSRFProtector
- تولید توکن‌های مبتنی بر زمان و HMAC-SHA256
- اعتبارسنجی توکن با بررسی انقضا
- استخراج از header یا body
- Decorator `@csrf_protect` برای endpointها

---

## لایه ۳ — Fingerprinting (`apps/shared_core/security/fingerprint.py`)

### RequestFingerprinter
- ایجاد fingerprint منحصر به فرد بر اساس:
  - User-Agent
  - Accept-Language
  - Accept-Encoding
  - Client IP
  - Timestamp (گروه‌بندی ۵ دقیقه‌ای)
- تحلیل رفتار درخواست‌ها
- شناسایی ربات‌ها و اسکریپت‌ها
- تعیین سطح ریسک: MINIMAL, LOW, MEDIUM, HIGH, CRITICAL
- پاکسازی خودکار fingerprintهای قدیمی (۲۴ ساعت)

---

## لایه ۴ — تشخیص ناهنجاری (`apps/shared_core/security/anomaly.py`)

### AnomalyDetector
- ثبت و تحلیل ترافیک درخواست‌ها
- تشخیص ۷ نوع ناهنجاری:

| نوع ناهنجاری | توضیح | آستانه |
|-------------|-------|--------|
| VOLUME_SPIKE | افزایش ناغونی حجم | >500 req/min |
| TRAFFIC_SPIKE | افزایش ۵ برابری | 5x میانگین |
| HIGH_ERROR_RATE | نرخ خطای بالا | >30% |
| SLOW_RESPONSE | زمان پاسخ کند | >5 ثانیه |
| SEQUENTIAL_SCANNING | اسکن ترتیبی IDها | ۱۰ ID متوالی |
| LOW_ENDPOINT_DIVERSITY | تنوع کم endpointها | <3 unique |
| BURST_TRAFFIC | ترافیک انفجاری | >20 req/sec |

- محاسبه امتیاز ریسک (۰-۱۰۰)
- توصیه‌های عملیاتی:
  - ≥75: BLOCK
  - ≥50: RATE_LIMIT
  - ≥25: MONITOR
  - <25: WATCH

---

## لایه ۵ — احراز هویت (`apps/users/auth_router.py`)

- JWT (HS256) با `SECRET_KEY` قوی
- Access Token: ۲۴ ساعت اعتبار
- Refresh Token: ۷ روز اعتبار
- Validation رمز عبور:
  - حداقل ۱۲ کاراکتر
  - حداقل یک حرف بزرگ
  - حداقل یک حرف کوچک
  - حداقل یک عدد
- RBAC (Role-Based Access Control)

---

## لایه ۶ — فرانت‌اند

- Middleware Next.js: محافظت مسیرهای حساس
- Interceptor axios: ریدایرکت خودکار به `/login` در 401
- ذخیره session: localStorage + cookie هم‌زمان

---

## 🔧 متغیرهای محیطی

```bash
# تنظیمات Rate Limiting
RATE_LIMIT_PER_MINUTE=120
RATE_LIMIT_PER_HOUR=1000

# تنظیمات Honeypot
HONEYPOT_LOG_FILE=/var/log/econojin/honeypot.log

# تنظیمات Blacklist
SECURITY_BLACKLIST_FILE=/var/lib/econojin/blacklist.json
SECURITY_WHITELIST_IPS=127.0.0.1,192.168.1.1

# تنظیمات Anomaly Detection
ANOMALY_RPM_THRESHOLD=500
ANOMALY_ERROR_RATE=0.3
ANOMALY_RESPONSE_TIME_MULT=3.0
ANOMALY_IP_SPIKE=100

# تنظیمات CSRF
CSRF_SECRET_KEY=your-secret-key-here
CSRF_TOKEN_LIFETIME=3600

# تنظیمات عمومی
MAX_INPUT_LENGTH=10000
SUSPICIOUS_THRESHOLD=10
ENV_STATE=production
```

---

## 📊 لاگ‌ها و مانیتورینگ

### انواع لاگ‌ها

| سطح | نماد | توضیح |
|-----|------|-------|
| WARNING | ⚠️ | هشدارهای امنیتی |
| CRITICAL | 🚨 | حملات شناسایی شده |
| INFO | ✅ | رویدادهای عادی |
| BLOCK | 🚫 | IP مسدود شده |
| HONEYPOT | 🕸️ | فعال‌سازی تله |

---

## 🎯 سناریوهای تشخیص و مقابله

### سناریو ۱: اسکن آسیب‌پذیری
```
مهاجم -> /.env, /wp-admin, /.git
واکنش: Honeypot → 404 → لاگ → مسدودسازی (بعد از ۳ بار)
```

### سناریو ۲: حمله Brute Force
```
مهاجم -> ۱۰۰+ درخواست login در دقیقه
واکنش: Rate Limit → 429 → Blacklist
```

### سناریو ۳: SQL Injection
```
مهاجم -> ' OR '1'='1
واکنش: InputSanitizer → تشخیص → رد درخواست → لاگ
```

### سناریو ۴: ربات اسکنر
```
ربات -> درخواست‌های سریع با User-Agent مشکوک
واکنش: Fingerprint → تحلیل → افزایش ریسک → مسدودسازی
```

---

## 🔐 توصیه‌های Production

1. ✅ HTTPS اجباری
2. ✅ تنظیم `ENV_STATE=production`
3. ✅ استفاده از `SECRET_KEY` قوی (حداقل ۳۲ بایت)
4. ✅ پیکربندی Cloudflare WAF
5. ✅ فعال‌سازی HSTS
6. ✅ چرخش دوره‌ای کلیدها
7. ✅ مانیتورینگ مستمر لاگ‌ها
8. ✅ Backup منظم از blacklist

---

## 📚 مستندات تکمیلی

- مستندات کامل: `/apps/shared_core/security/README.md`
- گزارش‌های امنیتی: `/reports/guardian_*.md`
- لاگ honeypot: `/tmp/honeypot.log`

---

**تاریخ آخرین به‌روزرسانی**: 2026-05-31  
**نسخه سیستم امنیت عنکبوتی**: 1.0.0  
**تیم توسعه**: Econojin Security Team
