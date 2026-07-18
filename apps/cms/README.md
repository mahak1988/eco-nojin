# Strapi CMS

This package contains the Strapi v5 headless CMS for managing marketing pages, blog posts, and tenant content.

## Running locally

```bash
cd apps/cms
pnpm install
pnpm dev
```

## Environment variables

Create a local environment file for Strapi and configure the service values:

- `PUBLIC_URL` — آدرس عمومی Strapi برای لینک‌های محتوا و تصاویر.
- `DATABASE_URL` — تنظیم اتصال پایگاه‌داده Strapi.
- `ADMIN_JWT_SECRET` — کلید امن ورود به پنل ادمین.
- `STRAPI_TOKEN` — توکن داخلی برای webhookها و سرویس‌ها.
- `STRAPI_HOST` — میزبان Strapi در محیط لوکال.
- `STRAPI_PORT` — پورت Strapi.

## Notes

- Strapi را به عنوان سرویس جداگانه اجرا کنید و به `apps/web` و `apps/main.py` اجازه دهید از `PUBLIC_URL` یا `STRAPI_URL` استفاده کنند.
- برای محیط production، `DATABASE_URL` باید به PostgreSQL یا دیتابیس مستقل دیگری اشاره کند.
- `ADMIN_JWT_SECRET` باید یک مقدار امن و تصادفی باشد.
