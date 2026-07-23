# Strapi CMS | سیستم مدیریت محتوای Econojin

> **نکته:** این ماژول **سیستم مدیریت محتوای بدون سر (Headless CMS)** پلتفرم Econojin است.
> مبتنی بر Strapi v5 برای مدیریت صفحات بازاریابی، پست‌های وبلاگ، و محتوای چندمستاجری (multi-tenant).

## مسئولیت‌ها

این ماژول سه وظیفه‌ی اصلی دارد:

1. **مدیریت محتوای بازاریابی** — صفحات لندینگ، محتوای تبلیغاتی و کمپین‌ها
2. **مدیریت وبلاگ** — پست‌ها، دسته‌بندی‌ها، برچسب‌ها و نظرات
3. **محتوای چندمستاجری** — مدیریت محتوای اختصاصی هر tenant

## ساختار

```
cms/
├── package.json                # ★ وابستگی‌های Strapi
├── README.md                   # این فایل
├── config/                     # ★ تنظیمات Strapi
│   ├── admin.js                #   تنظیمات پنل ادمین
│   ├── api.js                  #   تنظیمات API
│   ├── database.js             #   تنظیمات دیتابیس
│   ├── middlewares.js           #   Middlewareها
│   ├── plugins.js              #   پلاگین‌ها
│   └── server.js               #   تنظیمات سرور
├── src/                        # ★ کدهای Strapi
│   ├── admin/                  #   سفارشی‌سازی پنل ادمین
│   ├── api/                    #   API endpoints
│   ├── extensions/             #   افزونه‌ها
│   └── index.js                #   نقطه ورود
├── build/                      # خروجی build شده
└── __tests__/                  # تست‌ها
```

## تکنولوژی‌ها

| تکنولوژی | نسخه | توضیح |
|----------|------|--------|
| **Strapi** | v5 | Headless CMS |
| **Node.js** | 18+ | runtime |
| **PostgreSQL** | 15+ | دیتابیس پیش‌فرض production |
| **SQLite** | — | دیتابیس توسعه محلی |

## اجرای محلی

```bash
# از مسیر cms
cd apps/cms

# نصب وابستگی‌ها
pnpm install

# اجرای سرور توسعه
pnpm dev

# Build برای production
pnpm build

# شروع در حالت production
pnpm start
```

## متغیرهای محیطی

یک فایل `.env` در مسیر `apps/cms/` ایجاد کنید:

```ini
# آدرس عمومی (برای لینک‌های محتوا و تصاویر)
PUBLIC_URL=http://localhost:1337

# دیتابیس (PostgreSQL برای production)
DATABASE_URL=postgres://user:password@localhost:5432/econojin_cms

# امنیت
ADMIN_JWT_SECRET=your-secret-key-here      # کلید امن پنل ادمین
STRAPI_TOKEN=your-strapi-token             # توکن webhookها و سرویس‌ها

# میزبان و پورت
STRAPI_HOST=0.0.0.0
STRAPI_PORT=1337
```

## یکپارچگی با سایر ماژول‌ها

```
apps/web (React) ────→ Strapi API ────→ apps/cms
                          ↕
apps/main.py (FastAPI) ←─── Strapi Webhook ───→ apps/cms
```

- **apps/web** — محتوای بازاریابی و وبلاگ را از Strapi API دریافت می‌کند
- **apps/main.py** — از طریق webhookها از تغییرات محتوا مطلع می‌شود
- **Strapi** — به عنوان سرویس جداگانه اجرا می‌شود

## نکات مهم

### امنیت
- `ADMIN_JWT_SECRET` باید یک مقدار امن و تصادفی باشد (حداقل 32 کاراکتر)
- در production حتماً از HTTPS استفاده کنید
- دسترسی به پنل ادمین را محدود به IPهای مشخص کنید

### دیتابیس
- در محیط **توسعه**: SQLite (پیش‌فرض)
- در محیط **production**: PostgreSQL
- برای مهاجرت بین محیط‌ها از Strapi Content Transfer استفاده کنید

### Performance
- از CDN برای تصاویر و فایل‌های استاتیک استفاده کنید
- کش کردن پاسخ‌های API با Redis (از طریق پلاگین)
- محدود کردن درخواست‌های همزمان با rate limiting

## توسعه و تست

```bash
# تست‌ها
cd apps/cms && pnpm test

# ساختار API
# Strapi به صورت خودکار APIهای RESTful بر اساس Content-Typeها ایجاد می‌کند
# مثال: GET /api/pages, POST /api/pages, ...
```

## تغییرات مهم

- **فاز ۲:** مهاجرت به Strapi v5
- **فاز ۲:** پشتیبانی از multi-tenant
- **فاز ۲:** یکپارچگی webhook با FastAPI backend
- **فاز ۲:** بهبود امنیت و performance
