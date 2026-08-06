# فاز ۵ — تکمیل‌شده

**تاریخ:** ۱۴۰۵-۰۵-۱۵  
**شاخه:** `main`

## اهداف و وضعیت

| # | هدف | وضعیت |
|---|-----|--------|
| 1 | Version history واقعی محتوا در DB | ✅ مدل `ContentVersion` + `ContentVersionService` |
| 2 | موتور امتیازدهی توصیه‌ها (ML سبک) | ✅ `recommendation_engine.py` |
| 3 | Playwright کامل‌تر | ✅ `playwright.config.ts` + e2e گسترش‌یافته |
| 4 | Route guard مبتنی بر permission | ✅ `PermissionGuard` + `ROUTE_PERMISSIONS` |

## فایل‌ها

- `apps/shared_core/models.py` — جدول `content_versions`
- `apps/admin_panel/content_version_service.py`
- `apps/admin_panel/recommendation_engine.py`
- `frontend/src/components/PermissionGuard.tsx`
- `frontend/playwright.config.ts`
- `frontend/e2e/admin-smoke.spec.ts`

## Migration

پس از deploy، جدول را بسازید:

```bash
# Alembic یا create_all
python -c "from apps.shared_core.database.session import Base, engine; ..."
```

یا migration اختصاصی برای `content_versions`.

## اجرا Playwright

```bash
cd apps/admin_panel/frontend
npm i -D @playwright/test
npx playwright install chromium
npx playwright test
```

**فاز ۵ ثبت شد.**
