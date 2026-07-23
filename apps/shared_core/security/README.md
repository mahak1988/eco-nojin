# مستندات امنیت چندلایه عنکبوتی Econojin

## 🕸️ معرفی سیستم امنیت عنکبوتی

سیستم امنیت چندلایه عنکبوتی (Spider Security System) یک معماری امنیتی دفاع در عمق است که از چندین لایه محافظتی برای مقابله با حملات مختلف استفاده می‌کند. این سیستم مانند تار عنکبوت، مهاجمان را در دام خود گرفتار کرده و شناسایی می‌کند.

---

## 📋 فهرست لایه‌های امنیتی

### لایه ۱: Middlewareهای امنیتی (`middleware.py`)

#### 1.1 SecurityHeadersMiddleware
- **X-Frame-Options**: جلوگیری از Clickjacking
- **X-Content-Type-Options**: جلوگیری از MIME Sniffing  
- **X-XSS-Protection**: فعال‌سازی XSS Filter مرورگر
- **Content-Security-Policy**: محدود کردن منابع قابل اعتماد
- **Referrer-Policy**: کنترل اطلاعات Referrer
- **Strict-Transport-Security**: اجبار HTTPS (در production)
- **Permissions-Policy**: محدود کردن ویژگی‌های مرورگر

#### 1.2 RateLimitMiddleware
- محدودیت درخواست بر اساس IP (پیش‌فرض: ۱۲۰ درخواست در دقیقه)
- محدودیت شدیدتر برای endpointهای حساس (۱۰ درخواست در دقیقه)
- الگوریتم Sliding Window برای دقت بیشتر
- endpointهای تحت حفاظت ویژه:
  - `/api/v1/auth/login`
  - `/api/v1/auth/register`
  - `/api/v1/users`

#### 1.3 HoneypotMiddleware (تله عنکبوتی)
- ایجاد endpointهای جعلی برای شناسایی اسکنرها
- مسیرهای honeypot شامل:
  - `/admin`, `/wp-admin`, `/phpmyadmin`
  - `/.env`, `/.git/config`
  - `/backup.sql`, `/database.sql`
  - و سایر مسیرهای حساس جعلی
- مسدود کردن خودکار IP بعد از ۳ تخلف
- لاگ کامل فعالیت‌های مشکوک

#### 1.4 SpiderSecurityMiddleware
- ترکیب تمام لایه‌های امنیتی
- مدیریت لیست سیاه IPها
- پشتیبانی از لیست سفید برای تست
- تصمیم‌گیری هوشمند برای مسدودسازی

---

### لایه ۲: محافظت در برابر Injection (`protection.py`)

#### 2.1 InputSanitizer
- پاکسازی ورودی‌ها از کدهای مخرب
- تشخیص و حذف Script Tags
- حذف Event Handlerها (onclick, onerror, etc.)
- محدود کردن طول ورودی‌ها
- پاکسازی دیکشنری‌ها و لیست‌ها

#### 2.2 SQLInjectionProtector
- تشخیص کلمات کلیدی SQL خطرناک
- بررسی الگوهای معروف SQL Injection
- اعتبارسنجی پارامترهای query
- محافظت از queryهای SQL

#### 2.3 XSSProtector
- پاکسازی خروجی برای جلوگیری از XSS
- HTML Escape برای محتوای غیرمجاز
- اعتبارسنجی بدنه JSON
- تشخیص اسکریپت‌های مخرب

#### 2.4 CSRFProtector
- تولید توکن‌های CSRF مبتنی بر زمان
- اعتبارسنجی توکن‌ها
- استخراج توکن از header یا body
- Decorator برای محافظت آسان endpointها

---

### لایه ۳: Fingerprinting (`fingerprint.py`)

#### RequestFingerprinter
- ایجاد fingerprint منحصر به فرد برای هر کلاینت
- تحلیل رفتار درخواست‌ها
- شناسایی ربات‌ها و اسکریپت‌ها
- تشخیص اسکن endpointهای حساس
- تعیین سطح ریسک (MINIMAL, LOW, MEDIUM, HIGH, CRITICAL)
- پاکسازی خودکار fingerprintهای قدیمی

**ویژگی‌های تحلیل:**
- سرعت درخواست‌ها (requests per second)
- تنوع endpointها
- الگوهای User-Agent
- دسترسی به endpointهای حساس

---

### لایه ۴: تشخیص ناهنجاری (`anomaly.py`)

#### AnomalyDetector
- ثبت و تحلیل ترافیک درخواست‌ها
- تشخیص ۵ نوع ناهنجاری:

1. **VOLUME_SPIKE**: افزایش ناگهانی حجم درخواست‌ها
2. **TRAFFIC_SPIKE**: افزایش ۵ برابری نسبت به میانگین
3. **HIGH_ERROR_RATE**: نرخ خطای بالای ۳۰٪
4. **SLOW_RESPONSE**: زمان پاسخ کند (>۵ ثانیه)
5. **SEQUENTIAL_SCANNING**: اسکن ترتیبی IDها
6. **LOW_ENDPOINT_DIVERSITY**: تنوع کم endpointها
7. **BURST_TRAFFIC**: ترافیک انفجاری (>۲۰ درخواست در ثانیه)

- محاسبه امتیاز ریسک
- ارائه توصیه‌های عملیاتی (BLOCK, RATE_LIMIT, MONITOR, WATCH)

---

## 🔧 نصب و راه‌اندازی

### 1. افزودن به main.py

```python
from apps.shared_core.security.middleware import SpiderSecurityMiddleware

# افزودن middleware به اپلیکیشن
app.add_middleware(SpiderSecurityMiddleware)
```

### 2. متغیرهای محیطی

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
ENV_STATE=production  # یا development
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

### فایل‌های لاگ

- **honeypot.log**: فعالیت‌های honeypot
- **security_blacklist.json**: لیست سیاه IPها
- **لاگ اصلی برنامه**: رویدادهای امنیتی

---

## 🎯 سناریوهای تشخیص و مقابله

### سناریو ۱: اسکن آسیب‌پذیری
```
مهاجم -> تلاش برای دسترسی به /.env, /wp-admin, /.git
واکنش: 
  1. Honeypot فعال می‌شود
  2. پاسخ 404 بازگردانده می‌شود
  3. IP لاگ می‌شود
  4. بعد از ۳ بار تکرار، IP مسدود می‌شود
```

### سناریو ۲: حمله Brute Force
```
مهاجم -> ارسال ۱۰۰+ درخواست login در دقیقه
واکنش:
  1. Rate Limit فعال می‌شود
  2. پاسخ 429 Too Many Requests
  3. IP به لیست سیاه اضافه می‌شود
```

### سناریو ۳: SQL Injection
```
مهاجم -> ارسال `' OR '1'='1` در پارامترها
واکنش:
  1. InputSanitizer الگو را تشخیص می‌دهد
  2. درخواست پاکسازی یا رد می‌شود
  3. لاگ امنیتی ثبت می‌شود
```

### سناریو ۴: ربات اسکنر
```
ربات -> ارسال درخواست‌های سریع با User-Agent مشکوک
واکنش:
  1. Fingerprint ایجاد می‌شود
  2. امتیاز ریسک افزایش می‌یابد
  3. در صورت رسیدن به آستانه، مسدود می‌شود
```

---

## 🔐 بهترین روش‌ها

### برای Production
1. ✅ فعال‌سازی HTTPS اجباری
2. ✅ تنظیم `ENV_STATE=production`
3. ✅ استفاده از `SECRET_KEY` قوی
4. ✅ پیکربندی Cloudflare WAF
5. ✅ فعال‌سازی HSTS
6. ✅ چرخش دوره‌ای کلیدها

### برای Development
1. ✅ افزودن IPهای تیم به `SECURITY_WHITELIST_IPS`
2. ✅ تنظیم `ENV_STATE=development`
3. ✅ غیرفعال‌کردن موقت برخی محدودیت‌ها

---

## 📈 آنالیز و گزارش‌گیری

### دسترسی به آمار IP

```python
from apps.shared_core.security.anomaly import AnomalyDetector

detector = AnomalyDetector()
stats = detector.get_ip_statistics("192.168.1.100")
print(stats)
```

### خروجی نمونه:
```json
{
  "total_requests": 150,
  "error_count": 45,
  "error_rate": 0.30,
  "avg_response_time": 0.25,
  "unique_endpoints": 5,
  "methods": {"GET": 100, "POST": 50},
  "time_range": {
    "first": "2026-05-31T10:00:00",
    "last": "2026-05-31T10:30:00"
  }
}
```

---

## 🛡️ مقایسه با استانداردها

| استاندارد | پوشش |
|-----------|------|
| OWASP Top 10 | ✅ ۹/۱۰ مورد |
| CIS Controls | ✅ ۷/۱۸ مورد |
| NIST CSF | ✅ Protect & Detect |

---

## 🔄 به‌روزرسانی و نگهداری

### وظایف روزانه
- بررسی لاگ‌های honeypot
- مانیتورینگ لیست سیاه

### وظایف هفتگی
- پاکسازی fingerprintهای قدیمی
- بررسی آمار ناهنجاری‌ها
- به‌روزرسانی الگوهای تشخیص

### وظایف ماهانه
- بازبینی سیاست‌های rate limiting
- تست نفوذ داخلی
- به‌روزرسانی مستندات

---

## 📞 پشتیبانی و گزارش باگ

برای گزارش مشکلات امنیتی یا پیشنهاد بهبود:
- ایمیل: security@econojin.local
- مستندات: `/docs/SECURITY.md`

---

## ✨ مجوز

این سیستم تحت مجوز MIT منتشر شده است.

---

**تاریخ آخرین به‌روزرسانی**: 2026-05-31  
**نسخه**: 1.0.0  
**تیم توسعه**: Econojin Security Team
