# فاز ۴ — تکمیل‌شده

**تاریخ:** ۱۴۰۵-۰۵-۱۵  
**شاخه:** `main`

## اهداف

| # | هدف | وضعیت |
|---|-----|--------|
| 1 | حذف mock از advanced-settings / versions / intelligent-analytics / auto-recommendations / advanced-alerts | ✅ `derived_analytics.py` + اتصال به AdminService |
| 2 | API مجوزها برای فرانت | ✅ `GET /admin/me/permissions` |
| 3 | Cookie-only در production | ✅ `VITE_COOKIE_ONLY` / `import.meta.env.PROD` |
| 4 | CI Playwright برای ادمین | ✅ `.github/workflows/admin-panel-e2e.yml` |
| 5 | UI بینش هوشمند | ✅ `IntelligentInsightsPage` |

## فایل‌ها

- `apps/admin_panel/derived_analytics.py`
- `apps/admin_panel/router.py` — endpointهای demock + permissions
- `frontend/src/contexts/AuthContext.tsx`
- `frontend/src/pages/IntelligentInsightsPage.tsx`
- `.github/workflows/admin-panel-e2e.yml`

## متغیر محیطی

```bash
# فرانت — اجبار cookie-only حتی در dev
VITE_COOKIE_ONLY=true
```

در production به‌صورت پیش‌فرض token در localStorage ذخیره نمی‌شود.

## فاز ۵ پیشنهادی

1. ذخیره version history واقعی محتوا در DB
2. مدل ML واقعی برای recommendations
3. Playwright کامل با backend fixture
4. Permission-based route guards در FE

**فاز ۴ ثبت شد.**
