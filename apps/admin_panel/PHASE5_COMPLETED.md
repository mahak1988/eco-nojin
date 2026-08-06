# فاز ۵ — تکمیل‌شده

**تاریخ:** ۱۴۰۵-۰۵-۱۵  
**شاخه:** `main`  
**Package manager:** `pnpm`

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

پس از deploy، جدول `content_versions` را بسازید (Alembic یا `create_all`).

## اجرا با pnpm

از ریشه monorepo یا پوشه فرانت:

```bash
# نصب وابستگی‌ها (ریشه workspace)
pnpm install

# Playwright
cd apps/admin_panel/frontend
pnpm add -D @playwright/test
pnpm exec playwright install chromium
pnpm run test:e2e
```

یا از ریشه (اگر فیلتر workspace تعریف شده):

```bash
pnpm --filter @econojin/admin-panel test:e2e
```

**فاز ۵ ثبت شد.**
