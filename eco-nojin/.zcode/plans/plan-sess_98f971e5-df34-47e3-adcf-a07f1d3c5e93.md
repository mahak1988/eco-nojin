# برنامه جامع توسعه پنل ادمین، یکپارچه‌سازی فایل‌ها و برنامه UI/UX

## خلاصه وضعیت فعلی (یافته‌های بررسی)

**بک‌اند کامل و استاندارد است:** `apps/admin_panel` (router/service/schemas/repository) با ۵ endpoint کارا: `/admin`، `/admin/settings`، `/admin/audit-logs`، `/admin/reports` + مدیریت کاربران از طریق `apps/users/router.py`. مدل‌های `AdminSetting`، `AuditLog`، `SystemReport` در `shared_core/models.py` موجود است.

**فرانت‌اند ادمین ناقص است:** `AdminDashboardPage.tsx` فقط یک صفحه آمار ساده است (۶ کارت عددی) در حالی که بک‌اند ۴ بخش دیگر را پشتیبانی می‌کند. `adminService.ts` همه متدها را دارد اما فرانت‌اند از settings/audit/reports/users استفاده نمی‌کند.

**تکراری‌ها و ناهماهنگی‌ها:**
- `apps/shared` (قالب خالی auto-scaffolded، ورژن 0.1.0) در کنار `apps/shared_core` (اصلی، ورژن 1.0.0) — تداخل.
- `fa.json` فقط ۵۳۳ خط در حالی که `en.json` ۹۲۴ خط است — کلیدهای حیاتی `simulators`, `satellites`, `scenarios`, `audiences`, `alerts`, `commandPalette`, `ecoCoin`, `footer`, `team`, `blog`, `careers`, `contactUs`, `daneshyar`, `decisionYar`، بخش‌های `drought`، `biodiversity`، `energy`، `ecosystem` در فارسی غایب هستند.
- مسیر `/api/v1/users/` (بک‌اند) در `API_ENDPOINTS` فرانت‌اند نیست.

---

## بخش ۱ — توسعه پنل ادمین فرانت‌اند (تب‌دار کامل در /admin)

### فایل‌های جدید
1. **`apps/web/src/pages/Admin/AdminPanelPage.tsx`** (جایگزین AdminDashboardPage فعلی)
   - کانتینر اصلی با ۵ تب (sidebar یا tab bar داخلی)
   - مدیریت state تب فعال + query key‌های اختصاصی هر بخش
   - استفاده از `framer-motion` برای انیمیشن جابه‌جایی تب‌ها (مطابق الگوی StatCard/PageHeader موجود)

2. **`apps/web/src/pages/Admin/tabs/DashboardTab.tsx`** — نسخه ارتقایافته داشبورد فعلی با کارت‌های شاخص + mini-chart‌های recharts (روند هفتگی)

3. **`apps/web/src/pages/Admin/tabs/UsersTab.tsx`** — جدول کاربران با جستجو، صفحه‌بندی، دکمه‌های فعال/غیرفعال‌سازی و ارتقا به superuser. متصل به `/api/v1/users/` (endpoint موجود).

4. **`apps/web/src/pages/Admin/tabs/SettingsTab.tsx`** — جدول + فرم ویرایش inline برای AdminSetting (key/value/description/is_active). متصل به `/admin/settings`.

5. **`apps/web/src/pages/Admin/tabs/AuditLogsTab.tsx`** — جدول لاگ‌های حسابرسی با فیلتر `event_type`، صفحه‌بندی، نمایش `actor_email` و `event_data` به‌صورت JSON expandable.

6. **`apps/web/src/pages/Admin/tabs/ReportsTab.tsx`** — لیست SystemReport با badge وضعیت (pending/running/completed/failed) و نمایش `report_data`.

### فایل‌های اصلاحی
7. **`apps/web/src/services/adminService.ts`** — افزودن متدهای `listUsers`، `deactivateUser`، `promoteToSuperuser`، `triggerReport`.
8. **`apps/web/src/types/api.ts`** — افزودن `users.list`، `users.byId` به `API_ENDPOINTS`.
9. **`apps/web/src/App.tsx`** — مسیر `/admin/*` را به AdminPanelPage جدید هدایت کند (با sub-routes اختیاری `?tab=users`).
10. **`apps/web/src/i18n/locales/en.json` و `fa.json`** — افزودن بلوک کامل `admin.tabs.*` برای ۵ تب + رشته‌های جدول‌ها.

### اصول طراحی
- **RBAC حفظ شود:** `<ProtectedRoute requireSuperuser>` فعلی سر جایش می‌ماند.
- **استفاده مجدد از کامپوننت‌های موجود:** `StatCard`، `PageHeader`، `Card`، `Button`، `LoadingSpinner`، `PagePlaceholder`.
- **Tailwind logical properties** (ms/me/start/end) برای RTL/LTR خودکار.
- **React Query** برای cache/invalidation (الگوی `["admin","dashboard"]` موجود).

---

## بخش ۲ — ادغام shared و حذف تکراری‌ها

1. **حذف `apps/shared/`** (ماژول قالب خالی، ورژن 0.1.0، مدل `Shared` بی‌کاربرد).
   - بررسی ایمپورت‌ها قبل از حذف (جستجوی `from apps.shared import`) — اگر رفرنسی نبود، حذف ایمن است.
   - فایل README آن آرشیو شود در گزارش فنی.
2. **`apps/shared_core`** به‌عنوان **مرجع رسمی** معرفی شود؛ مدل‌های `AdminSetting`, `AuditLog`, `SystemReport`, `SharedCore` همگی اینجا می‌مانند.
3. **مستندسازی** در `apps/shared_core/README.md`: "این ماژول مرجع رسمی shared است؛ apps/shared قدیمی منسوخ شده."
4. **بررسی ایمن** shared_ai، shared_knowledge، shared_sim: این‌ها ماژول‌های واقعی با کد کاربردی هستند (RAG، fallback، ecocoin) → **دست‌نخورده باقی می‌مانند**.

---

## بخش ۳ — همگام‌سازی i18n (fa.json ↔ en.json)

### افزودن به `fa.json` (ترجمه فارسی):
- `simulators.*` (همه ۸ شبیه‌ساز: climate, hydrology, crop, carbon, soilErosion, flood, drought, biodiversity)
- `satellites.*` (۱۵ ماهواره + شاخص‌های طیفی)
- `scenarios.*` (۱۰ سناریوی آماده)
- `audiences.*` (۵ نقش + KPIها)
- `alerts.*` (۶ نوع هشدار + badge شمارنده)
- `commandPalette.*`
- `ecoCoin.*` (کیف پول، استخراج، چالش‌ها، پاداش‌ها)
- `footer.*`، `team.*`، `blog.*`، `careers.*`، `contactUs.*`، `daneshyar.*`، `decisionYar.*`
- `drought.*`، `biodiversity.*`، `energy.*`، `ecosystem.*`
- `common.appName`, `appTagline`, `loadingPage`, `retry`, `back`, `yes`, `no`, `all`, `soon`, `backToDashboard`, `language`, `persian`, `english`, `toman`
- `error.unauthorized`, `error.unauthorizedDesc`, `error.boundaryTitle`, `error.boundaryDescription`, `error.boundaryRetry`, `error.loadingSession`
- `admin.tabs.*` (برای پنل جدید)
- `hydrology.*` (با کلیدهای جدول)
- `soil.*`, `documents.*`, `carbon.*`, `gis.*`، `profile.*`

**نتیجه:** fa.json از ۵۳۳ خط به ~۹۵۰ خط هماهنگ با en.json.

---

## بخش ۴ — استانداردسازی و همگام‌سازی فایل‌های مشترک

1. **بررسی API endpoints** بین `apps/main.py` (بک‌اند) و `apps/web/src/types/api.ts` (فرانت‌اند):
   - افزودن گروه `users: { list: "/users", byId: (id) => "/users/${id}" }` به فرانت‌اند.
   - اعتبارسنجی مسیرها (`/api/v1` prefix در api-client با prefix روترهای بک‌اند همخوان است).
2. **حذف فایل‌های `.backup*`** در apps/web/src/ و apps/main.py.backup_* (به همراه ذکر در گزارش).
3. **هماهنگ‌سازی کلید واژه‌های appName:** "Econojin" در en.json با "Eco Nojin" در main.py بک‌اند — استاندارد به **"Econojin"** (یک کلمه) در همه جا.
4. **بررسی TypeScript types** برای data models مشترک (User، AdminSetting، AuditLog، SystemReport) در `types/index.ts` — هماهنگ با Pydantic schemas.

---

## بخش ۵ — گزارش فنی

ساخت فایل **`docs/ADMIN_PANEL_AND_INTEGRATION_REPORT.md`** شامل:
1. خلاصه اجرایی وضعیت فعلی (بک‌اند کامل، فرانت‌اند ناقص، تکراری‌ها)
2. معماری Admin Panel (نمودار ER + فلو داده)
3. جدول مقایسه endpoint‌های بک‌اند ↔ سرویس فرانت‌اند
4. تصمیمات معماری (چرا تب‌دار در همان مسیر به‌جای پروژه جدا)
5. نقشه راه اجرایی (Checklist با موفقیت‌سنجه)
6. متون i18n استانداردشده
7. ریسک‌ها و نکات نگهداری

---

## بخش ۶ — برنامه UI/UX برای زیباترین و حرفه‌ای‌ترین وبسایت

ساخت فایل **`docs/UI_UX_PREMIUM_DESIGN_PLAN.md`** شامل:

### الهام‌بخش‌ها (Reference Benchmark)
- **Stripe.com** (دقت تایپوگرافی + micro-interactions + gradient mesh)
- **Linear.app** (سرعت، mode تاریک، keyboard-first)
- **Vercel Dashboard** (ساختار داشبورد تمیز)
- **Apple Environment** (انیمیشن‌های scroll + داده‌محور)
- **Notion** (تمیز و سازمان‌یافته)

### سیستم طراحی پیشنهادی
1. **Design Tokens:** پالت رنگ سبز-زمردی (هماهنگ با brand موجود `#10b981`) + خاکستری نوت‌رال، فونت Vazirmatn (فارسی) و Inter (انگلیسی).
2. **Glassmorphism + Soft Shadows:** کارت‌های شیشه‌ای با `backdrop-blur` برای hero.
3. **Micro-interactions:** Framer Motion برای ورود صفحات، hover lift، number count-up آمار.
4. **Dark Mode کامل:** از طریق `class="dark"` در html (پشتیبانی tailwind فعلی).
5. **RTL/LTR flip** اتوماتیک با logical properties (در حال حاضر موجود، تقویت می‌شود).
6. **Data Visualization:** Recharts با تم یکپارچه (نه رنگ‌های پیش‌فرض).
7. **Page Transitions:** AnimatePresence + route-based fade/slide.
8. **Skeleton Loaders:** جایگزین spinner در جدول‌ها.
9. **Toast Notifications:** برای موفقیت/خطای mutation‌ها (اکتشاف: `sonner` یا `react-hot-toast`).

### رودمپ پیاده‌سازی UI (۳ فاز)
- **فاز ۱:** سبک‌سازی پنل ادمین + داشبورد اصلی (همراه این کار).
- **فاز ۲:** بازطراحی صفحه Home با hero gradient mesh و scroll-driven.
- **فاز ۳:** Charts یکپارچه + Dark Mode روی همه صفحات.

---

## ترتیب اجرا (Workflow)

1. حذف ایمن `apps/shared/` پس از تأیید عدم رفرنس
2. توسعه فایل‌های Admin Panel فرانت‌اند (۶ فایل جدید + ۴ اصلاحی)
3. تکمیل `fa.json` با همه کلیدهای غایب
4. افزودن endpoint‌های users به api.ts و adminService.ts
5. هماهنگ‌سازی appName "Econojin"
6. پاک‌سازی فایل‌های backup
7. ساخت گزارش فنی `ADMIN_PANEL_AND_INTEGRATION_REPORT.md`
8. ساخت برنامه UI/UX `UI_UX_PREMIUM_DESIGN_PLAN.md`
9. اجرای `pnpm tsc --noEmit` برای اعتبارسنجی TypeScript
10. گزارش نهایی به کاربر

## ریسک‌ها و محدودیت‌ها
- حذف `apps/shared` نیازمند بررسی کامل import‌هاست (با grep تأیید می‌شود).
- اجرای build ممکن است به‌خاطر سایر خطاهای موجود پروژه fail شود — صرفاً `tsc --noEmit` روی فایل‌های جدید انجام می‌شود.
- فرض بر این است که endpoint‌های `/admin/settings` و `/admin/audit-logs` و `/admin/reports` به‌درستی در main.py ثبت شده‌اند (تأیید شد).

## خروجی نهایی
- ۶ فایل فرانت‌اند جدید برای Admin Panel
- ۴ فایل فرانت‌اند اصلاحی
- ۱ فایل بک‌اند README به‌روزرسانی (shared_core)
- ۲ فایل i18n هماهنگ (en + fa)
- ۲ سند Markdown (گزارش فنی + برنامه UI/UX)
- حذف ۱ ماژول تکراری (apps/shared)
- پاک‌سازی فایل‌های backup