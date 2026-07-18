# Gap Analysis — مستندات پروژه

این سند بخش‌های ضعیف یا ناقص مستندات فعلی را شناسایی می‌کند.

## ۱. اسناد معماری

- `docs/ARCHITECTURE.md` به روز شد، اما هنوز نیاز دارد:
  - شرح کامل مسیرهای API و نام دقیق روترها (`apps/main.py`, `apps/users/*`, `apps/ai_agents/*`, `apps/simulation/*`).
  - نمودار اتصال بین `apps/web`, `apps/main.py`, و `apps/cms/`.
  - توضیح دقیق باکس `shared_core` و `shared_ai` برای توسعه‌دهندگان جدید.

## ۲. راه‌اندازی و محیط

- `README.md` ریشه اکنون به روز است، اما:
  - فایل `.env.example` اصلی باید با مقادیر واقعی `SECRET_KEY`، `LLM_PROVIDER`، و `ALLOWED_ORIGINS` توضیح‌دار شود.
  - `apps/web/.env.example` باید مقدار پیش‌فرض `VITE_SUPABASE_URL` و `VITE_SUPABASE_ANON_KEY` را روشن کند.

## ۳. اسناد ماژول‌ها

- `apps/api/README.md`, `apps/web/README.md`, `apps/cms/README.md` وجود دارد ولی:
  - `apps/cms/README.md` هنوز عمومی است و اطلاعات محیط Strapi کامل نیست.
  - `apps/api/README.md` باید مسیرهای اصلی API و نحوه‌ی اضافه کردن روتر جدید را شرح دهد.
  - دیگر بسته‌های `apps/shared_*` و `packages/*` مستندات کامل عملیات ندارند.

## ۴. مستندات خطا و لاگ‌گیری

- هیچ سند مستقل و منظم برای:
  - نحوه خواندن لاگ‌های FastAPI
  - نحوه خطایابی `dotenv` و مسیریابی `DATABASE_URL`
  - گزارش خطاهای React/Vite و Sentry موجود نیست.

## ۵. اسناد تست و CI

- دستورهای کلی وجود دارند، ولی:
  - ساختار تست frontend (`Vitest` / Playwright) توضیح داده نشده.
  - دستور اجرای تست‌های یکپارچه و محیط لازم برای E2E ذکر نشده.

## ۶. اسناد deployment

- `docs/DEPLOYMENT.md` و `docs/FREE_STACK.md` وجود دارند ولی:
  - وضعیت واقعی `apps/main.py` و `apps/web/` با مستندات احتمالی `render/Neon/Vercel` ناسازگار است.
  - اتصال Supabase/Strapi در مستندات deployment باید دقیق‌تر شرح داده شود.

## نتیجه‌گیری

پیشنهاد اصلی:
1. `docs/ARCHITECTURE.md` را جزئی‌تر و با دیاگرام‌های واقعی تکمیل کنیم.
2. `docs/ERRORS_AND_LOGGING.md` جدید بسازیم.
3. `README.md` ریشه را با جزئیات دقیق‌تر شروع و env sync کرده‌ایم.
4. READMEهای `apps/cms` و `apps/api` را با نمونه‌های مشخص‌تر کامل کنیم.
