# فاز ۰ — تثبیت پایه: TODO List

**وضعیت:** در حال اجرا
**شروع:** مرداد ۱۴۰۵

---

## هفته ۱: رفع بدهی‌های بحرانی

### T-01: تکمیل Alembic migrations کامل  
**وضعیت:** 🔄 در حال انجام  
**فایل‌های هدف:** `alembic/versions/`, `alembic/env.py`, `apps/shared_core/database/session.py`  
**اقدامات:**
- [ ] بررسی تمام models ثبت‌شده
- [ ] شناسایی جداول موجود در migration‌های قبلی
- [ ] ایجاد migration یکپارچه برای تمام مدل‌ها
- [ ] تست migration در SQLite
- [ ] افزودن auto-upgrade در startup
- [ ] جایگزینی `create_all()` در production

### T-02: جایگزینی create_all با Alembic  
**وضعیت:** ⏳ منتظر T-01  
**فایل‌های هدف:** `apps/shared_core/database/session.py`

### T-03: محدود کردن CORS origins  
**وضعیت:** ⏳  
**فایل‌های هدف:** `apps/main.py`, `apps/shared_core/config.py`

### T-04: فعال‌سازی rate limiting  
**وضعیت:** ⏳  
**فایل‌های هدف:** `apps/shared_core/middleware/rate_limit.py`

### T-05: مدیریت secrets  
**وضعیت:** ⏳  
**فایل‌های هدف:** `.env.example`, `apps/shared_core/config.py`

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
