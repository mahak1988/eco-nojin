# فاز ۰ — تثبیت پایه: TODO List

**وضعیت:** در حال اجرا (بخشی از فاز ۱ امنیتی تکمیل شد)
**شروع:** مرداد ۱۴۰۵
**به‌روزرسانی:** ۱۴۰۵/۰۵/۱۵ — model_registry کامل + RateLimit/Audit/SpiderGuard شرطی

---

## هفته ۱: رفع بدهی‌های بحرانی

### T-01: تکمیل Alembic migrations کامل  
**وضعیت:** 🔄 در حال انجام (پیش‌نیاز model_registry ✅)  
**فایل‌های هدف:** `alembic/versions/`, `alembic/env.py`, `apps/shared_core/database/session.py`  
**اقدامات:**
- [x] بررسی تمام models ثبت‌شده → `model_registry.py` گسترش یافت (users, rbac, farms, crops, planting, inventory, monitoring, simulation.*, ai_agents, shared_*, api.models.*)
- [ ] شناسایی جداول موجود در migration‌های قبلی
- [ ] ایجاد migration یکپارچه برای تمام مدل‌ها
- [ ] تست migration در SQLite
- [ ] افزودن auto-upgrade در startup
- [ ] جایگزینی `create_all()` در production

### T-02: جایگزینی create_all با Alembic  
**وضعیت:** ⏳ منتظر T-01  
**فایل‌های هدف:** `apps/shared_core/database/session.py`

### T-03: محدود کردن CORS origins  
**وضعیت:** ✅ انجام‌شده (از قبل)  
**فایل‌های هدف:** `apps/main.py`, `apps/shared_core/config.py`  
**یادداشت:** CORS از `settings.all_cors_origins` خوانده می‌شود؛ `*` حذف شده.

### T-04: فعال‌سازی rate limiting  
**وضعیت:** ✅ انجام‌شده (فاز ۱)  
**فایل‌های هدف:** `apps/shared_core/middleware/rate_limit.py`, `apps/shared_core/security_init.py`  
**یادداشت:** `RateLimitMiddleware` + `AuditLogMiddleware` + `SpiderGuardMiddleware` به‌صورت شرطی بر اساس `ENABLE_*` در `initialize_security` ثبت می‌شوند.

### T-05: مدیریت secrets  
**وضعیت:** ✅ پایه انجام‌شده  
**فایل‌های هدف:** `.env.example`, `apps/shared_core/config.py`  
**یادداشت:** validation production برای SECRET_KEY؛ پیشنهاد RS256؛ gen_jwt_keys.sh موجود.

---

## هفته ۲: رفع بدهی‌های بالا

### T-06: مهاجرت مدل‌های علمی  
**وضعیت:** ⏳

### T-07: اتصال صفحات frontend  
**وضعیت:** ⏳

### T-08: استانداردسازی API responses  
**وضعیت:** ⏳

### T-09: افزایش تست coverage  
**وضعیت:** ⏳

### T-10: پاکسازی legacy code  
**وضعیت:** ⏳

---

## هفته ۳: تست و تثبیت

### T-11: externalize hardcoded values  
**وضعیت:** ⏳

### T-12: تکمیل TypeScript types  
**وضعیت:** ⏳
