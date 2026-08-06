# فاز ۱ — کارهای باقی‌مانده (فرانت‌اند) — تکمیل‌شده

**تاریخ:** ۱۴۰۵-۰۵-۱۵  
**Commit:** `83cd9aa` روی `main`

## خلاصه

کارهای باقی‌مانده فاز ۱ پنل ادمین (لایه فرانت‌اند و اتصال واقعی به API) پیاده‌سازی و روی `main` ثبت شد.

## موارد انجام‌شده

| # | کار | فایل | وضعیت |
|---|-----|------|--------|
| 1 | Authorization interceptor (Bearer از localStorage + withCredentials) | `frontend/src/api/adminApi.ts` | ✅ |
| 2 | مدیریت 401 و پاک‌سازی توکن | `frontend/src/api/adminApi.ts` | ✅ |
| 3 | اتصال Dashboard به `GET /api/v1/admin/` واقعی | `frontend/src/pages/Dashboard.tsx` | ✅ |
| 4 | نمایش آمار واقعی (users / settings / logs / reports) | `Dashboard.tsx` | ✅ |
| 5 | اتصال Monitoring به `GET /api/v1/admin/health` | `frontend/src/pages/MonitoringPage.tsx` | ✅ |
| 6 | Loading / Error / Auto-refresh ۳۰ثانیه | `MonitoringPage.tsx` | ✅ |
| 7 | برچسب‌های فارسی + `dir="rtl"` | Dashboard + Monitoring | ✅ |

## نحوه تأیید

```bash
# API
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000

# Admin FE
cd apps/admin_panel/frontend && pnpm install && pnpm dev
```

1. ورود با کاربر superuser و ذخیره `access_token` در localStorage  
2. باز کردن داشبورد → باید تعداد کاربران/تنظیمات/لاگ‌ها از API بیاید  
3. باز کردن «نظارت» → وضعیت DB / Redis / محیط واقعی نمایش داده شود  

## نکات بعدی (خارج از فاز ۱)

- یکپارچه‌سازی کامل cookie-only (حذف وابستگی به localStorage)
- فارسی‌سازی کامل صفحه Users و سایر صفحات انگلیسی باقی‌مانده
- همگام‌سازی کامل routeهای App.tsx با تمام آیتم‌های Sidebar
