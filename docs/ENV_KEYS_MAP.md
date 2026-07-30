# نقشهٔ دقیق `.env` و کلیدها — Econojin

**به‌روز:** 2026-07-30  
**منبع کد:** `apps/shared_core/config.py` (Pydantic Settings، `env_file=".env"`)

---

## ۱. محل فایل‌ها روی ویندوز شما

| فایل | مسیر دقیق |
|------|-----------|
| Backend env | `D:\econojin.com\.env` |
| Template (git) | `D:\econojin.com\.env.example` |
| Frontend env | `D:\econojin.com\apps\web\.env.local` |
| FE template | `D:\econojin.com\apps\web\.env.example` |
| GEE JSON | `D:\econojin.com\secrets\gee-sa.json` |
| JWT PEM (prod) | `D:\econojin.com\secrets\jwt_private.pem` و `jwt_public.pem` |
| SQLite DB | `D:\econojin.com\apps\econojin.db` |

**دستور یک‌بار:**

```powershell
cd D:\econojin.com
Copy-Item .env.example .env
Copy-Item apps\web\.env.example apps\web\.env.local
New-Item -ItemType Directory -Force -Path secrets | Out-Null
```

`.env` و `secrets/` را commit نکنید.

---

## ۲. متغیر ↔ محل استفاده در کد

| متغیر env | فیلد Settings | مصرف |
|-----------|---------------|------|
| `DATABASE_URL` | `DATABASE_URL` | SQLAlchemy async |
| `ENVIRONMENT` | `ENVIRONMENT` | docs/middleware/prod checks |
| `SECRET_KEY` / `JWT_SECRET_KEY` | `jwt_secret` | JWT HS256 |
| `ALGORITHM` | `ALGORITHM` | HS256 یا RS256 |
| `JWT_*_KEY_PATH` | paths | RS256 PEM |
| `COOKIE_*` / token names | cookies | HttpOnly auth |
| `REQUIRE_AUTH_FOR_WRITES` | flag | RBAC writes |
| `BACKEND_CORS_ORIGINS` | CORS list | FE origins |
| `REDIS_URL` / `CELERY_BROKER_URL` | queue | Celery |
| `GEE_*` | GEE provider | NDVI live |
| `COPERNICUS_*` | Copernicus | Sentinel download |
| `OPEN_METEO_URL` | weather | no-key forecast |
| `OPENWEATHER_API_KEY` | (optional apps) | OWM proxy |
| `LLM_*` | AI agents | default `fake` |
| `SENTRY_DSN` | monitoring | errors |
| `BLOCKCHAIN_*` / wallet | EcoCoin | testnet |
| `VITE_API_BASE_URL` | FE only | production API URL |
| `VITE_USE_MOCK` | FE only | mock vs live |

---

## ۳. چه زمانی کلید ثبت کنید؟

طبق درخواست شما: **بعد از فاز ۱۰** ثبت‌نام و احراز هویت سرویس‌ها و قرار دادن کلیدها.

تا آن زمان پروژه با:

- SQLite  
- `LLM_PROVIDER=fake`  
- satellite synthetic / Open-Meteo  

کار می‌کند.

| کلید | ثبت‌نام | فایل |
|------|---------|------|
| OpenWeather (اختیاری) | openweathermap.org | `OPENWEATHER_API_KEY` در `.env` |
| GEE SA | Google Cloud + Earth Engine | `secrets/gee-sa.json` + `GEE_*` |
| Copernicus | dataspace.copernicus.eu | `COPERNICUS_USERNAME/PASSWORD` |
| Sentinel Hub | sentinel-hub.com | `SENTINEL_HUB_*` |
| Sentry | sentry.io | `SENTRY_DSN` |
| LLM | Groq/OpenAI/… | `LLM_API_KEY` + `LLM_PROVIDER` |
| JWT RS256 | openssl محلی | `secrets/*.pem` |

**هرگز** مقدار واقعی کلید را در چت یا GitHub نگذارید.

---

## ۴. هم‌ترازی با اسکریپت local

`scripts/run_local.ps1` این‌ها را override می‌کند اگر ست نشده باشند:

- `ENVIRONMENT=local`
- `DATABASE_URL=sqlite+aiosqlite:///./apps/econojin.db`
- `REQUIRE_AUTH_FOR_WRITES=false`
- `COOKIE_SECURE=false`

بعد از پر کردن `.env`، برای اعمال کامل یک‌بار API را restart کنید.
