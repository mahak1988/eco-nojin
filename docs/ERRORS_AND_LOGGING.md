# Errors and Logging — راهنمای خطا و لاگ‌گیری

این سند نحوه‌ی مشاهده، تحلیل و رفع خطاها در محیط توسعه `Eco Nojin` را توضیح می‌دهد.

## ۱. نحوهٔ نمایش لاگ‌های FastAPI

### اجرای سرور

```powershell
cd d:\econojin.com
.\.venv\Scripts\activate
python apps/main.py
```

### لاگ‌های مهم

- `✅ دیتابیس مقداردهی اولیه شد` — اتصال پایگاه‌داده موفق.
- `✅ ماژول AI بارگذاری شد` — بارگذاری LLM/AI با موفقیت انجام شد.
- `⚠️  init_db خطا:` — خطا در راه‌اندازی اتصال دیتابیس.
- `❌ خطای پیش‌بینی‌نشده:` — یک خطای داخلی غیرقابل پیش‌بینی رخ داده.
- `🛑 Eco Nojin API - در حال خاموش شدن` — سرور در حال خاموش شدن است.

### محل لاگ

- لاگ‌ها در کنسول استاندارد (stdout) چاپ می‌شوند.
- در صورت استفاده از Docker Compose، خروجی را با `docker compose logs` مشاهده کنید.

## ۲. ساختار ارور هندلینگ در FastAPI

### هندلرهای عمومی در `apps/main.py`

- `global_exception_handler`:
  - تمام Exceptions را می‌گیرد.
  - پاسخ استاندارد با کد `500` و پیغام `Internal Server Error` می‌دهد.
- `not_found_handler`:
  - مسیرهای ناشناس را با کد `404` مدیریت می‌کند.

### نمونه پاسخ خطا

```json
{
  "error": "Internal Server Error",
  "message": "یک خطای داخلی رخ داد."
}
```

## ۳. خطاهای رایج و راه حل سریع

### ۳.۱. خطاهای `dotenv`

- مطمئن شوید فایل `.env` در ریشه پروژه وجود دارد.
- مقادیر لازم را از `.env.example` کپی کنید.
- اگر `load_dotenv` مقادیر را نمی‌خواند، مسیر فایل را با `Path(__file__).resolve().parent.parent / ".env"` بررسی کنید.

### ۳.۲. خطاهای دیتابیس

- `DATABASE_URL` باید به فرمت `sqlite+aiosqlite:///./apps/econojin.db` یا PostgreSQL معتبر باشد.
- اگر از SQLite استفاده می‌کنید، بررسی کنید فایل `apps/econojin.db` قابل نوشتن باشد.
- اگر PostgreSQL استفاده می‌کنید، مطمئن شوید که سرویس پایگاه‌داده اجرا شده و credentials صحیح‌اند.

### ۳.۳. خطای `ImportError` یا مسیرهای Python

- `apps/main.py` ریشه پروژه را به `sys.path` اضافه می‌کند.
- اگر خطاهای import دریافت می‌کنید، بررسی کنید `PROJECT_ROOT` درست تعیین شده باشد.
- برای ماژول‌هایین که در `apps/*` هستند، نام‌گذاری مسیرها باید با `sys.path.insert(0, str(PROJECT_ROOT))` همخوانی داشته باشد.

### ۳.۴. خطاهای CORS

- مقدار `ALLOWED_ORIGINS` را در `.env` بررسی کنید.
- مقدار پیش‌فرض شامل `http://localhost:5173`, `http://localhost:3000`, `http://localhost:8000` است.
- اگر front-end روی پورت دیگری اجرا می‌شود، آن را به `ALLOWED_ORIGINS` اضافه کنید.

## ۴. لاگ‌گیری frontend

### اجرای فرانت‌اند

```powershell
cd apps/web
pnpm dev
```

### خطاهای معمول Vite

- `VITE_API_BASE_URL` مقداردهی نشده
  - روش حل: `apps/web/.env.local` بسازید و مقدار `VITE_API_BASE_URL=http://localhost:8000` را اضافه کنید.
- `Failed to load module` یا aliasهای وارداتی
  - روش حل: بررسی `apps/web/vite.config.ts` و مطابقت پوشه‌های `@econojin/*` با `tsconfig.json`.

### خطاهای Axios

- `Network Error` یا 404
  - بررسی کنید بک‌اند روی آدرس `VITE_API_BASE_URL` اجرا شده باشد.
- `401 Unauthorized`
  - مطمئن شوید درخواست auth سالم است و توکن معتبر ارسال شده است.

## ۵. روش سریع بررسی خطاها

1. سرور FastAPI را اجرا کنید و خروجی را بررسی کنید.
2. در مرورگر، مسیر `/docs` را باز کنید تا مستندات و مدل‌های request/response را ببینید.
3. اگر خطای frontend دارید، کنسول مرورگر و terminal Vite را بررسی کنید.
4. در محیط Docker، `docker compose logs` را اجرا کنید.

## ۶. نکته‌های عملی برای توسعه‌دهنده جدید

- ابتدا `apps/main.py` را بخوانید؛ این فایل نقطه شروع backend است.
- سپس `apps/shared_core/database/session.py` را برای درک اتصال DB مرور کنید.
- برای مشاهده مسیرهای API، `apps/users/router.py`, `apps/ai_agents/router.py`, و `apps/simulation/router.py` را باز کنید.
- برای اتصال frontend به backend، فایل `apps/web/src/services/supabase.ts` و `apps/web/src/api/index.ts` را بررسی کنید.
