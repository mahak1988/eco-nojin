# ممیزی `apps/cms` و برنامه تکامل

**تاریخ:** ۱۴۰۵-۰۵-۱۶  
**پشته:** Strapi v5 (Headless CMS)

---

## ۱. خلاصه وضعیت

ماژول CMS اسکلت گسترده‌ای دارد (content-types، ده‌ها service، middleware tenant، مستندات فاز)، اما **از نظر قابلیت اجرا و یکپارچگی واقعی ناقص** است: وابستگی‌ها ناقص، config با قرارداد Strapi v5 ناسازگار، و بسیاری از serviceها بدون ثبت در lifecycle / بدون وابستگی نصب‌شده‌اند.

| لایه | ارزیابی |
|------|----------|
| Content-types (pages, blog, …) | اسکلت موجود — نیاز به controllers/routes/services استاندارد Strapi |
| Config | اصلاح Phase-0 انجام شد |
| Services (۳۰+ فایل) | کد زیاد؛ بسیاری وابسته به `ioredis`/`axios`/`xss` بدون ذکر در package.json |
| Tests | تقریباً نمادین (shape test) |
| یکپارچگی FastAPI / admin_panel | مستند شده؛ wiring عملی محدود |

---

## ۲. ایرادات و بدهی فنی شناسایی‌شده

### بحرانی (P0)
1. **`package.json` ناقص:** اسکریپت `dev`/`test` نبود؛ `pg` / `better-sqlite3` / users-permissions صریح نبود.  
2. **فرمت middleware اشتباه:** فایل `config/middleware.ts` به‌صورت object بود؛ Strapi v5 آرایه در `middlewares.ts` می‌خواهد.  
3. **کلیدهای امنیتی ضعیف:** پیش‌فرض `change-me-in-production` برای JWT.  
4. **GraphQL در plugins فعال بدون پکیج** `@strapi/plugin-graphql`.  
5. **`src/api/index.ts` اشتباه:** کلاینت Axios/Vite داخل درخت API استراپی.  
6. **`multiTenancy` داخل `database.ts`:** گزینهٔ native Knex/Strapi نیست؛ گمراه‌کننده بود.

### بالا (P1)
7. سرویس‌ها (`cache-service` → Redis، `webhook-service` → axios) بدون dependency و بدون bootstrap.  
8. middlewareهای `tenant-isolation` / `rate-limit` ثبت‌نشده در `middlewares.ts`.  
9. README با اسکریپت‌ها و نام فایل‌های config هم‌خوان نبود.  
10. تست‌ها به نوع `Cms` ارجاع می‌دادند بدون `src/types`.

### متوسط (P2)
11. حجم زیاد serviceهای پیشرفته (AI، e-commerce، A/B) نسبت به هستهٔ پایدار.  
12. عدم وجود `.env.example` قبل از Phase-0.  
13. عدم CI اختصاصی برای `apps/cms`.

---

## ۳. اصلاحات انجام‌شده در این commit (Phase-0)

- `package.json`: `dev`, `test`, `pg`, `better-sqlite3`, users-permissions, vitest  
- `config/middlewares.ts` استاندارد Strapi v5  
- `config/database.ts` sqlite محلی / postgres prod  
- `config/server.ts` + `admin.ts` با سخت‌گیری production  
- `config/plugins.ts` بدون GraphQL اجباری  
- `.env.example`  
- پاک‌سازی `src/api/index.ts` + `src/types/index.ts`  
- این سند

---

## ۴. برنامه توسعه و تکامل

### فاز A — پایدارسازی اجرا (۱–۲ هفته)
- [ ] `pnpm install` در `apps/cms` و `pnpm dev` تا بالا آمدن Admin  
- [ ] تکمیل schema + `routes`/`controllers`/`services` برای: pages, blog-posts, categories, tags  
- [ ] Permissions عمومی خواندن برای published content  
- [ ] ثبت `tenant-isolation` به‌صورت middleware سفارشی (با احتیاط)  
- [ ] اتصال webhook امضادار به FastAPI

### فاز B — یکپارچگی محصول (۲–۳ هفته)
- [ ] کلاینت محتوا در `apps/web` (فقط REST published)  
- [ ] نمایش/ویرایش سطح‌بالا در admin_panel در صورت نیاز (proxy توکن)  
- [ ] Media + CDN env  
- [ ] Cache اختیاری Redis (dependency + feature flag)

### فاز C — کیفیت و امنیت (موازی)
- [ ] تست integration روی APIهای content-type  
- [ ] CI: build Strapi + vitest  
- [ ] حذف یا قرنطینه serviceهای استفاده‌نشده (AI/e-commerce تا اولویت کسب‌وکار)  
- [ ] Rate-limit واقعی (Redis یا gateway)

### فاز D — تکامل
- [ ] i18n محتوا (fa/en)  
- [ ] پیش‌نویس / انتشار زمان‌بندی‌شده  
- [ ] GraphQL فقط در صورت نیاز محصول  
- [ ] Multi-tenant بالغ (ستون tenant + policy، نه schema جدا مگر الزام)

---

## ۵. اصول پیشنهادی

1. **هسته کوچک، پایدار** قبل از serviceهای پیشرفته.  
2. **هر dependency در package.json** قبل از import.  
3. **اسرار فقط از env**؛ fail-fast در production.  
4. **pnpm** هم‌راستا با monorepo.  
5. **مستندات فاز** را با وضعیت واقعی کد همگام نگه دارید.

---

## ۶. دستور شروع محلی

```bash
cd apps/cms
cp .env.example .env
pnpm install
pnpm dev
# Admin: http://localhost:1337/admin
```
