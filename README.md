# Econojin (اکو نوژین)

ابرپروژه جامع خدمات رایگان برای کشاورزی، آموزش، محیط زیست و جامعه — با بک‌اند FastAPI، فرانت Next.js و آماده استقرار روی سرویس‌های رایگان.

> رایگان · آفلاین‌اول (در حال توسعه) · چندزبانه (fa/en) · امنیت JWT و OTP · مدل‌های علمی و EcoCoin

---

## وضعیت پروژه (خرداد ۱۴۰۵)

| لایه | پیشرفت | توضیح |
|------|--------|--------|
| API (`api/`) | ~۷۰٪ | ۱۵+ ماژول، auth/farmer/calendar/store با DB |
| Web (`apps/web`) | ~۷۵٪ | داشبورد، ۱۵+ صفحه، Leaflet، چت AI، OTP |
| Admin (`apps/admin`) | ~۳۰٪ | داشبورد، ماژول‌ها، AI، شبیه‌ساز |
| Legacy (`scripts/`) | مرجع | مدل‌های قدیمی؛ تدریجاً به `api/` منتقل می‌شود |

جزئیات کارهای باقی‌مانده: [`TODO.md`](TODO.md) · نقشه راه: [`docs/ROADMAP_FA.md`](docs/ROADMAP_FA.md)

---

## معماری

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  apps/web       │     │  apps/admin     │     │  apps/cms        │
│  Next.js 14     │     │  Next.js        │     │  (Strapi — آینده)│
│  /fa  /en       │     │                 │     │                  │
└────────┬────────┘     └────────┬────────┘     └──────────────────┘
         │                       │
         └───────────┬───────────┘
                     │  REST + JWT
                     ▼
         ┌───────────────────────┐
         │  api/main.py          │
         │  FastAPI + SQLAlchemy │
         │  SQLite / PostgreSQL  │
         └───────────────────────┘
```

---

## ساختار مخزن

```
econojin.com/
├── api/                    # بک‌اند اصلی (FastAPI)
│   ├── main.py             # نقطه ورود و mount روترها
│   ├── core/               # config, DB, security, middleware
│   ├── modules/            # weather, calendar, auth, farmer, store, ...
│   └── services/           # sms, llm, rothc_full, simulation_engine
├── apps/
│   ├── web/                # اپ کاربر (پورت 3001)
│   └── admin/              # پنل مدیریت
├── scripts/                # اسکریپت‌ها و مدل‌های legacy
├── tests/                  # pytest (API)
├── docker/                 # Dockerfile.api
├── docs/                   # مستندات استقرار و امنیت
├── .env.example            # متغیرهای بک‌اند
└── docker-compose.apps.yml # استک محلی Docker
```

---

## قابلیت‌های پیاده‌سازی‌شده

### بک‌اند
- احراز هویت JWT + ورود OTP (Kavenegar / Twilio)
- کشاورزان، تقویم (CRUD)، فروشگاه (CRUD) با SQLite/Postgres
- هواشناسی، حسابداری، GIS (مساحت + لایه نقشه)
- شبیه‌ساز RothC (مدل کامل از `scripts/rothc.py`) و AquaCrop ساده
- EcoCoin — ماینر طبیعی با فرمول اکوسیستم
- چت AI — OpenAI / Azure (اختیاری) + fallback داخلی
- امنیت: Rate limit، Security headers، CORS

### فرانت‌اند (`apps/web`)
- مسیرهای چندزبانه: `/fa/...` و `/en/...` (next-intl)
- داشبورد زنده، `ModuleDashboard` مشترک، MediaHero
- نقشه Leaflet (OSM + ماهواره)، ویجت چت AI
- React Query (تقویم، فروشگاه)، فرم‌های فعال
- لوگوی تایپوگرافی: `src/components/brand/Logo.tsx`

---

## پیش‌نیازها

- **Node.js** 20+ و **pnpm** 8+
- **Python** 3.11+ و **pip**
- (اختیاری) Docker برای `docker-compose.apps.yml`

---

## راه‌اندازی سریع

### ۱. بک‌اند

```powershell
cd d:\econojin.com
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# ویرایش .env در صورت نیاز (JWT_SECRET، SMS، LLM)

python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

- API: http://127.0.0.1:8000  
- مستندات: http://127.0.0.1:8000/docs  
- سلامت: http://127.0.0.1:8000/api/v1/health  

### ۲. فرانت‌اند

```powershell
cd apps\web
copy .env.example .env.local
# NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

pnpm install
pnpm dev
```

- اپ: http://localhost:3001/fa  
- ورود: http://localhost:3001/fa/login (در dev کد OTP در پاسخ API: `dev_code`)

### ۳. پنل ادمین

```powershell
cd apps\admin
pnpm dev
```

### ۴. Monorepo (از ریشه)

```powershell
pnpm install
pnpm dev:web
pnpm dev:admin
```

---

## متغیرهای محیط مهم

نمونه کامل در [`.env.example`](.env.example) و [`apps/web/.env.example`](apps/web/.env.example).

| متغیر | کاربرد |
|--------|--------|
| `DATABASE_URL` | SQLite محلی یا Neon Postgres |
| `JWT_SECRET` | امضای توکن (production: حتماً قوی) |
| `OTP_DEV_MODE` | `true` = نمایش کد در API؛ `false` + SMS واقعی |
| `SMS_PROVIDER` | `kavenegar` \| `twilio` \| `none` |
| `LLM_ENABLED` | `true` + `OPENAI_API_KEY` یا Azure |
| `NEXT_PUBLIC_API_URL` | آدرس API برای فرانت |

---

## تست

```powershell
# API
pytest tests/ -v

# TypeScript
cd apps\web
pnpm type-check

# E2E (Playwright — API باید روشن باشد)
pnpm test:e2e
```

---

## استقرار (رایگان)

| سرویس | نقش |
|--------|-----|
| [Vercel](https://vercel.com) | فرانت `apps/web` |
| [Render](https://render.com) / Railway | API |
| [Neon](https://neon.tech) | PostgreSQL |
| GitHub Actions | CI (`.github/workflows/econojin-apps-ci.yml`) |

راهنمای گام‌به‌گام: [`docs/DEPLOY_VERCEL_NEON.md`](docs/DEPLOY_VERCEL_NEON.md) · [`docs/FREE_STACK.md`](docs/FREE_STACK.md)

```powershell
docker compose -f docker-compose.apps.yml up --build
```

---

## API — ماژول‌های فعال

| Prefix | توضیح |
|--------|--------|
| `/api/v1/auth` | login، OTP، profile |
| `/api/v1/farmers` | CRUD کشاورز |
| `/api/v1/calendar` | CRUD رویداد |
| `/api/v1/store` | CRUD فروشگاه |
| `/api/v1/weather` | پیش‌بینی و هشدار |
| `/api/v1/accounting` | خلاصه و تراکنش |
| `/api/v1/gis` | مساحت، لایه، NDVI |
| `/api/v1/simulation` | RothC، AquaCrop، coupling |
| `/api/v1/ai` | چت |
| `/api/v1/ecomining` | EcoCoin و ماین |
| `/api/v1/dashboard` | آمار داشبورد |

---

## مستندات

- [`docs/ROADMAP_FA.md`](docs/ROADMAP_FA.md) — نقشه راه محصول
- [`docs/SECURITY.md`](docs/SECURITY.md) — امنیت چندلایه
- [`docs/DEPLOY_VERCEL_NEON.md`](docs/DEPLOY_VERCEL_NEON.md) — استقرار production
- [`docs/FREE_STACK.md`](docs/FREE_STACK.md) — سرویس‌های رایگان
- [`TODO.md`](TODO.md) — کارهای باز و انجام‌شده

---

## مجوز

مطابق فایل [`License`](License) در ریشه مخزن.

---

## مشارکت

1. `TODO.md` را برای کارهای باز ببینید.  
2. شاخه feature بسازید و PR ارسال کنید.  
3. قبل از merge: `pytest tests/` و `pnpm type-check` در `apps/web`.
