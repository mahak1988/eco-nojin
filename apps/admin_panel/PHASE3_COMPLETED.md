# فاز ۳ — تکمیل‌شده

**تاریخ:** ۱۴۰۵-۰۵-۱۵  
**شاخه:** `main`

## اهداف و وضعیت

| # | هدف | وضعیت |
|---|-----|--------|
| 1 | فارسی‌سازی Invoices / Payments / Journal + API واقعی | ✅ |
| 2 | RBAC در منوی فرانت (فیلتر بر اساس role / superuser) | ✅ |
| 3 | صفحه ۴۰۳ «دسترسی مجاز نیست» | ✅ ForbiddenPage |
| 4 | اسکلت تست e2e دود (Playwright) | ✅ `e2e/admin-smoke.spec.ts` |
| 5 | cookie-first (از فاز قبل) + مستند hybrid | ✅ |

## فایل‌ها

- `pages/accounting/InvoicesPage.tsx`
- `pages/accounting/PaymentsPage.tsx`
- `pages/accounting/JournalEntriesPage.tsx`
- `components/AdminSidebar.tsx` — فیلتر `roles`
- `pages/ForbiddenPage.tsx`
- `e2e/admin-smoke.spec.ts`

## نکات

- منوهای Users / Audit / Monitoring / Security فقط برای `admin` و `superuser`
- حسابداری برای `admin` / `superuser` / `manager`
- در صورت ۴۰۳ از API، می‌توان در صفحات از `ForbiddenPage` استفاده کرد

## فاز ۴ پیشنهادی

1. حذف کامل mockهای advanced در `router.py` بک‌اند
2. نصب و CI برای Playwright
3. cookie-only بدون localStorage در production
4. Permission API از بک‌اند برای منوهای دقیق‌تر

**فاز ۳ ثبت شد.**
