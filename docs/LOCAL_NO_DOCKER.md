# اجرای محلی بدون Docker

**سند اصلی و کامل‌تر:** [ZERO_INSTALL_LOCAL.md](./ZERO_INSTALL_LOCAL.md)  
**فاز ۱ روی همین پشته:** [PHASE1_RESTART.md](./PHASE1_RESTART.md)

## مشکل رایج

```
VIRTUAL_ENV=eco-nojin\.venv does not match ... .venv
Project virtual environment directory ... cannot be used (no Python executable)
```

علت: پوشهٔ `.venv` شکسته است یا مسیر `D:\econojin.com` با `D:\econojin.com\eco-nojin` یکی نیست و `uv run` محیط اشتباه را می‌گیرد.

## راه‌حل سریع (PowerShell)

```powershell
cd D:\econojin.com\eco-nojin   # یا همان جایی که apps\main.py هست
git pull origin main

# تعمیر venv
.\scripts\fix_venv.ps1

# یا یک‌جا اجرا (توصیه‌شده):
.\scripts\run_local.ps1
```

**استفاده نکنید از `uv run`** مگر uv را جداگانه برای همین پروژه تنظیم کرده باشید. به‌جای آن:

```powershell
.\scripts\fix_venv.ps1
python -m uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

## متغیرهای محیطی (جایگزین Docker)

| متغیر | مقدار محلی |
|--------|------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./apps/econojin.db` |
| `ENVIRONMENT` | `local` |
| `REQUIRE_AUTH_FOR_WRITES` | `false` |
| `COOKIE_SECURE` | `false` |
| `ALEMBIC_USE_SQLITE` | `1` |

Postgres/Redis فقط وقتی سرویس جدا (مثلاً Neon) دارید لازم است؛ **SQLite برای توسعه و فاز ۱ کافی است.**

## فرانت

```powershell
cd apps\web
npm install
npm run dev
```

## جایگزین production بدون Docker محلی

- API: سرویس ابری + `DATABASE_URL` به Neon/Supabase  
- FE: Vercel / Cloudflare Pages  
- نیازی به Docker Desktop روی لپ‌تاپ توسعه‌دهنده نیست
