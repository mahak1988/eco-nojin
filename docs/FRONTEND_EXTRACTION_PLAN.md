# 🏗️ طرح استخراج و یکپارچه‌سازی پروژه‌های برتر گیت‌هاب در EcoNojin

> برنامه جامع استخراج کد، الگوها و معماری از ۱۲ پروژه برتر و الحاق به پروژه EcoNojin با تغییرات اصلاحی

---

## 📋 فهرست پروژه‌های مبدأ

| # | پروژه مبدأ | ⭐ | ماژول استخراج | بسته مقصد در EcoNojin |
|---|-----------|---|--------------|---------------------|
| ۱ | shadcn/ui | ۷۰K | کامپوننت‌های UI | `packages/ui` |
| ۲ | bulletproof-react | ۲۵K | معماری امنیتی، hooks، api layer | `packages/lib`, `packages/hooks` |
| ۳ | next-shadcn-dashboard | ۶.۷K | Dashboard layout, routing, auth | `apps/web` |
| ۴ | materio-mui-nextjs | ۲K | Admin panel, data tables | `packages/ui` |
| ۵ | Vercel Admin | ۱.۶K | Postgres integration, NextAuth | `packages/lib/api` |
| ۶ | next-enterprise | ۶K | Testing setup, CI/CD, SEO | Root config |
| ۷ | TailAdmin | ۱.۲K | ۶۰+ UI components, charts | `packages/ui` |
| ۸ | cruip Mosaic | ۲.۸K | Dashboard design, chart configs | `packages/ui`, `apps/web` |
| ۹ | horizon-ui | ۴۸۰ | Theme system, dark mode | `packages/ui` |
| ۱۰ | shadboard | ۶۹۴ | shadcn setup, layouts | `apps/web` |
| ۱۱ | Claude Agent Monitor | ۸۱۸ | WebSocket, real-time, Kanban | `apps/admin_panel`, `apps/ai_agents` |
| ۱۲ | justboil admin | ۵۹۲ | Tailwind 4.x, modular structure | `packages/config-tailwind` |

---

## 🏗️ معماری هدف در EcoNojin

```
econojin-monorepo/
├── apps/
│   ├── web/                 ← NEW: React + Vite + Next.js SPA (از next-shadcn + Vercel template)
│   ├── admin_panel/         ← بهبود: Admin dashboard (از materio-mui + TailAdmin)
│   ├── ai_agents/           ← بهبود: AI agents panel (از Claude Agent Monitor)
│   ├── api/                 ← بهبود: API layer security (از bulletproof-react)
│   └── cms/                 ← بهبود: Content management
├── packages/
│   ├── ui/                  ← ارتقا: shadcn/ui + TailAdmin + horizon components
│   ├── hooks/               ← ارتقا: bulletproof-react hooks + custom hooks
│   ├── lib/                 ← ارتقا: API client, validation, security utils
│   ├── types/               ← ارتقا: Enterprise type definitions
│   ├── features/            ← ارتقا: Feature modules (GIS, blockchain, etc.)
│   └── config-*/            ← بهبود: ESLint, TypeScript, Tailwind configs
├── scripts/
│   └── extract_components.py ← NEW: Script خودکار استخراج و تبدیل
└── docs/
    ├── ARCHITECTURE.md      ← به‌روزرسانی
    └── TOP_GITHUB_FRONTEND_PROJECTS.md ✓
```

---

## 📦 فاز اول: بسته‌های پایه (Packages)

### ۱.۱ ارتقای `packages/ui` — استخراج از shadcn/ui + TailAdmin

**وضعیت فعلی:** ۱۱ کامپوننت پایه (button, card, input, select, badge, progress, toast, label, MapViewer, BookingCalendar)

**کامپوننت‌های جدید برای اضافه کردن:**

| کامپوننت | مبدأ | توضیح | اولویت |
|---------|------|-------|--------|
| `alert-dialog.tsx` | shadcn/ui | دیالوگ‌های هشدار | بالا |
| `avatar.tsx` | shadcn/ui + TailAdmin | تصویر پروفایل | بالا |
| `checkbox.tsx` | shadcn/ui | چک‌باکس با accessibility | بالا |
| `command.tsx` | shadcn/ui | Command palette / search | متوسط |
| `dialog.tsx` | shadcn/ui | دیالوگ مودال | بالا |
| `dropdown-menu.tsx` | shadcn/ui | منوی کشویی | بالا |
| `form.tsx` | shadcn/ui | فرم با validation | بالا |
| `popover.tsx` | shadcn/ui | پاپ‌اوور | بالا |
| `sheet.tsx` | shadcn/ui | Sheet/Sidebar کشویی | بالا |
| `table.tsx` | TailAdmin + shadcn | جدول داده با sort/filter | بالا |
| `tabs.tsx` | shadcn/ui | تب‌ها | بالا |
| `charts/*` | TailAdmin | ApexCharts wrapper | متوسط |
| `data-table.tsx` | TailAdmin | جدول داده پیشرفته | بالا |
| `sidebar.tsx` | cruip Mosaic | سایدبار حرفه‌ای | بالا |
| `header.tsx` | cruip Mosaic | هدر با notification | بالا |
| `stats-card.tsx` | TailAdmin | کارت آمار | متوسط |
| `kanban-board.tsx` | Claude Agent Monitor | برد کانبان | متوسط |

**تغییرات اصلاحی:**
- تغییر نام کلاس‌ها از `shadcn-*` به `econojin-*`
- اضافه کردن prefix `ec-` به تمام کلاس‌های Tailwind
- استفاده از `tailwind-merge` و `clsx` (موجود)
- تطبیق رنگ‌ها با تم EcoNojin (سبز #16a34a)
- اضافه کردن RTL support برای فارسی

### ۱.۲ ارتقای `packages/hooks` — استخراج از bulletproof-react

**وضعیت فعلی:** خالی (بدون hook در `src/index.ts`)

**هوک‌های جدید:**

| هوک | مبدأ | توضیح |
|----|------|-------|
| `useAuth` | bulletproof-react | مدیریت احراز هویت |
| `useDebounce` | bulletproof-react | دیبانس برای search |
| `useDisclosure` | ✓ موجود | مدیریت state باز/بسته |
| `useMediaQuery` | bulletproof-react | رسپانسیو |
| `usePagination` | TailAdmin | پیجینیشن |
| `usePermission` | bulletproof-react | کنترل دسترسی |
| `useLocalStorage` | bulletproof-react | ذخیره محلی |
| `useWebSocket` | Claude Agent Monitor | اتصال WebSocket |
| `useRealTime` | Claude Agent Monitor | داده‌های لحظه‌ای |
| `useInfiniteScroll` | bulletproof-react | اسکرroll نامحدود |

### ۱.۳ ارتقای `packages/lib` — استخراج از bulletproof-react + Vercel

**وضعیت فعلی:** axios + zod

**ماژول‌های جدید:**

| ماژول | مبدأ | توضیح |
|------|------|-------|
| `api/client.ts` | bulletproof-react | HTTP client با interceptors |
| `api/auth.ts` | Vercel Admin | احراز هویت یکپارچه |
| `utils/security.ts` | bulletproof-react | XSS protection, sanitization |
| `utils/format.ts` | next-enterprise | فرمت‌کننده تاریخ/عدد |
| `validation/schemas.ts` | next-enterprise | اسکیم‌های Zod |
| `error-handler.ts` | bulletproof-react | مدیریت خطای سراسری |

### ۱.۴ ارتقای `packages/types` — استخراج از bulletproof-react

**انواع جدید:**

| نوع | توضیح |
|-----|-------|
| `api.types.ts` | Response/Request types با error handling |
| `auth.types.ts` | User, Session, Permission types |
| `common.types.ts` | Shared utility types |
| `pagination.types.ts` | Pagination, sorting, filtering |

---

## 📱 فاز دوم: اپلیکیشن‌های فرانت‌اند

### ۲.۱ ایجاد `apps/web` — از next-shadcn-dashboard-starter + Vercel

**ساختار پیشنهادی:**

```
apps/web/
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
├── postcss.config.js
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── layout.tsx                # Root layout با providers
│   │   ├── page.tsx                  # Home page
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx            # Dashboard layout با sidebar
│   │   │   ├── page.tsx              # Dashboard overview
│   │   │   ├── analytics/page.tsx
│   │   │   ├── settings/page.tsx
│   │   │   └── users/page.tsx
│   │   └── api/                      # API routes (اختیاری)
│   ├── components/
│   │   ├── ui/                       # Re-export از @econojin/ui
│   │   ├── dashboard/
│   │   │   ├── sidebar.tsx           # از cruip Mosaic
│   │   │   ├── header.tsx            # از cruip Mosaic
│   │   │   ├── stats-cards.tsx       # از TailAdmin
│   │   │   └── recent-activity.tsx
│   │   ├── charts/
│   │   │   ├── area-chart.tsx        # از TailAdmin
│   │   │   ├── bar-chart.tsx         # از TailAdmin
│   │   │   └── pie-chart.tsx         # از TailAdmin
│   │   └── maps/
│   │       └── MapViewer.tsx         # موجود
│   ├── hooks/                        # Re-export از @econojin/hooks
│   ├── lib/                          # Re-export از @econojin/lib
│   ├── providers/
│   │   ├── auth-provider.tsx         # از bulletproof-react
│   │   ├── theme-provider.tsx        # از horizon-ui
│   │   └── query-provider.tsx        # TanStack Query
│   ├── config/
│   │   ├── navigation.ts            # Route config
│   │   └── site.ts                  # Site metadata
│   ├── i18n/                         # چندزبانه
│   │   ├── fa.json
│   │   └── en.json
│   ├── styles/
│   │   └── globals.css
│   └── middleware.ts                 # از Vercel template
```

### ۲.۲ ارتقای `apps/admin_panel` — از materio-mui-nextjs + TailAdmin

**کامپوننت‌های جدید برای admin_panel:**
- DataTable پیشرفته با sort/filter/export
- Form builder با validation
- User management dashboard
- Analytics dashboard با chart

### ۲.۳ ارتقای `apps/ai_agents` — از Claude Agent Monitor

**قابلیت‌های جدید:**
- WebSocket real-time monitoring
- Kanban board برای agent status
- Agent orchestration dashboard
- Tool usage analytics

---

## 🔒 فاز سوم: امنیت و معماری

### ۳.۱ از bulletproof-react

| الگوی امنیتی | محل پیاده‌سازی |
|-------------|----------------|
| HTTP Interceptors برای refresh token | `packages/lib/api/client.ts` |
| Error Boundary سراسری | `apps/web/src/providers/` |
| Input sanitization | `packages/lib/utils/security.ts` |
| Permission-based routing | `packages/hooks/usePermission.ts` |
| Rate limiting UI | `packages/lib/api/interceptors.ts` |
| Content Security Policy | `apps/web/next.config.js` |

### ۳.۲ از next-enterprise

| قابلیت | محل پیاده‌سازی |
|--------|----------------|
| ESLint config پیشرفته | `packages/config-eslint` |
| TypeScript strict | `packages/config-typescript` |
| Jest + React Testing Library | Root + `apps/web` |
| Playwright E2E tests | `apps/web/e2e/` |
| GitHub Actions CI/CD | `.github/workflows/` |
| SEO (metadata, sitemap) | `apps/web/src/app/layout.tsx` |

---

## 🔧 فاز چهارم: زیرساخت و اسکریپت‌ها

### ۴.۱ اسکریپت استخراج خودکار

```bash
scripts/extract_github_components.py
```

این اسکریپت:
1. کلون کردن ریپوها در `repos/`
2. کپی کردن فایل‌های مورد نظر
3. اعمال تغییرات نام (shadcn → econojin)
4. به‌روزرسانی importها
5. افزودن کامنت انتساب (attribution)

### ۴.۲ به‌روزرسانی پیکربندی‌ها

**tailwind.config.ts:**
```typescript
// اضافه کردن:
// - prefix: 'ec-'
// - colors: EcoNojin palette (green, earth, water)
// - RTL support
// - dark mode strategy
```

**tsconfig.json** (در هر بسته):
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

---

## 📅 برنامه زمان‌بندی پیشنهادی

| فاز | مدت | خروجی‌ها |
|-----|------|---------|
| **فاز ۱**: بسته‌های پایه | ۲-۳ روز | packages/ui (۲۰+ کامپوننت), packages/hooks (۱۰+ hook), packages/lib (ماژول‌های امنیتی) |
| **فاز ۲**: اپلیکیشن‌ها | ۳-۵ روز | apps/web (صفحات کامل), apps/admin_panel (ارتقا) |
| **فاز ۳**: امنیت | ۱-۲ روز | CI/CD, testing, security middleware |
| **فاز ۴**: زیرساخت | ۱ روز | اسکریپت استخراج, config files |
| **کل پروژه** | **۷-۱۱ روز** | |

---

## ✅ چک‌لیست نهایی

### اولویت بالا (فوری)
- [ ] استخراج ۱۵ کامپوننت اصلی از shadcn/ui به `packages/ui`
- [ ] استخراج Dashboard layout از next-shadcn-dashboard-starter
- [ ] استخراج security patterns از bulletproof-react
- [ ] استخراج DataTable از TailAdmin
- [ ] ایجاد `apps/web` با ساختار کامل
- [ ] اضافه کردن احراز هویت (NextAuth/Clerk)

### اولویت متوسط
- [ ] WebSocket monitoring از Claude Agent Monitor
- [ ] Charts از TailAdmin/cruip
- [ ] Kanban board
- [ ] i18n setup
- [ ] E2E tests با Playwright

### اولویت پایین (بهبود)
- [ ] Add RTL support کامل
- [ ] PWA support
- [ ] Storybook برای کامپوننت‌ها
- [ ] Bundle analysis

---

## 📝 نکات حقوقی و انتساب

تمامی پروژه‌های مبدأ دارای مجوز MIT هستند و می‌توان از کد آنها استفاده کرد. الزامات:

1. **حفظ کپی‌رایت**: در هر فایل استخراج‌شده، کامنت انتساب اضافه شود
2. **عدم تغییر مجوز**: محصول نهایی MIT باقی بماند
3. **افزودن LICENSE**: فایل LICENSE اصلی پروژه را به‌روز کنیم

**الگوی کامنت انتساب:**
```typescript
/**
 * EcoNojin UI Component
 * Adapted from: shadcn/ui (MIT) - https://github.com/shadcn-ui/ui
 * Modifications: EcoNojin theme colors, RTL support, Persian locale
 */
```

---

## 🔗 لینک‌های مفید

| پروژه | لینک |
|-------|------|
| shadcn/ui | https://ui.shadcn.com/docs |
| bulletproof-react | https://github.com/alan2207/bulletproof-react |
| next-shadcn-dashboard | https://github.com/Kiranism/next-shadcn-dashboard-starter |
| TailAdmin | https://github.com/TailAdmin/free-react-tailwind-admin-dashboard |
| cruip Mosaic | https://github.com/cruip/tailwind-dashboard-template |
| Vercel Admin | https://github.com/vercel/nextjs-postgres-nextauth-tailwindcss-template |
| next-enterprise | https://github.com/Blazity/next-enterprise |
| Claude Agent Monitor | https://github.com/hoangsonww/Claude-Code-Agent-Monitor |
| materio-mui | https://github.com/themeselection/materio-mui-nextjs-admin-template-free |
| horizon-ui | https://github.com/horizon-ui/horizon-tailwind-react |
| shadboard | https://github.com/Qualiora/shadboard |
| justboil admin | https://github.com/justboil/admin-one-react-tailwind |