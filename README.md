# Econojin (اکو نوژین)

پروژه monorepo برای پلتفرم کاربردی کشاورزی، آموزش، محیط زیست و جامعه که از FastAPI برای بک‌اند و Vite/React برای فرانت‌اند استفاده می‌کند.

> توسعه پایدار · چندزبانه · AI و مدل‌های علمی · معماری ماژولار با بسته‌های مشترک

---

## وضعیت فعلی پروژه

| لایه | وضعیت | توضیح |
|------|--------|--------|
| Backend | فعال | FastAPI در `apps/main.py`، چند ماژول `apps/*`، دیتابیس async SQLAlchemy |
| Frontend | فعال | React + Vite در `apps/web/`، Axios، Supabase auth و API client |
| CMS | ساده | Strapi در `apps/cms/` برای محتوا و مقالات |
| Shared packages | فعال | `packages/*` برای UI، types، config و کتابخانه‌های مشترک |

جزئیات کارهای باز: [`TODO.md`](TODO.md) · نقشه راه: [`docs/ROADMAP_FA.md`](docs/ROADMAP_FA.md)

---

## معماری کلی

```
┌───────────────────┐          ┌───────────────────┐
│ apps/web/         │          │ apps/cms/         │
│ - Vite + React    │          │ - Strapi v5       │
│ - Axios / Supabase│          │ - CMS content     │
└────────┬──────────┘          └────────┬──────────┘
         │                              │
         │ HTTP / REST / JWT            │
         ▼                              │
┌───────────────────────────────────────────────────┐
│ apps/main.py                                      │
│ - FastAPI app                                     │
│ - CORS, logging, error handlers                   │
│ - Loads routers from apps/users, ai_agents, etc.   │
└────────┬──────────────────────────────────────────┘
         │
         ▼
┌───────────────────────────────────┐
│ apps/shared_core/                 │
│ - async SQLAlchemy session         │
│ - database utilities               │
│ - reusable services                 │
└───────────────────────────────────┘
```

---

## ساختار مخزن

```
econojin.com/
├── apps/
│   ├── main.py
│   ├── api/                 # API scaffold and shared backend module
│   ├── users/               # auth, user management, user endpoints
│   ├── ai_agents/           # AI agent endpoints and logic
│   ├── simulation/          # simulation APIs and domain services
│   ├── shared_core/         # DB session, shared backend utilities
│   ├── shared_ai/           # AI helpers and RAG tools
│   ├── shared_knowledge/    # knowledge modeling and content store
│   ├── shared_sim/          # shared simulation utilities
│   ├── shared/              # common backend models/services
│   ├── web/                 # frontend app
│   └── cms/                 # Strapi CMS package
├── packages/                # shared TS packages and config
├── docs/                    # مستندات فنی و استقرار
├── docker-compose.apps.yml  # لوکال compose stack
├── package.json             # monorepo scripts
├── pnpm-workspace.yaml      # workspace packages
├── turbo.json               # Turbo task config
├── pyproject.toml           # Python project config
├── .env.example             # backend environment example
└── apps/web/.env.example    # frontend environment example
```

---

## پیش‌نیازها

- Node.js 20+
- pnpm 11+
- Python 3.11+
- pip
- (اختیاری) Docker برای اجرا با Docker Compose

---

## راه‌اندازی محلی

### ۱. نصب وابستگی‌ها

```powershell
cd d:\econojin.com
pnpm install
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### ۲. راه‌اندازی بک‌اند

```powershell
copy .env.example .env
# فایل .env را با مقادیر واقعی مثل DATABASE_URL، SECRET_KEY و LLM_PROVIDER پر کنید
python apps/main.py
```

- API: `http://127.0.0.1:8000`
- مستندات Swagger: `http://127.0.0.1:8000/docs`
- سلامت: `http://127.0.0.1:8000/health`

### ۳. راه‌اندازی فرانت‌اند

```powershell
cd apps/web
copy .env.example .env.local
# VITE_API_BASE_URL را به آدرس بک‌اند تنظیم کنید
pnpm dev
```

- اپ: `http://localhost:5173`

### ۴. راه‌اندازی CMS (اختیاری)

```powershell
cd apps/cms
pnpm install
pnpm dev
```

### ۵. اجرای هم‌زمان در monorepo

```powershell
cd d:\econojin.com
pnpm install
pnpm dev:web
pnpm dev:cms
```

### ۶. اجرای محلی با Docker Compose

```powershell
docker compose -f docker-compose.apps.yml up --build
```

---

## متغیرهای محیطی مهم

### Backend (`.env`)

- `DATABASE_URL` — `sqlite+aiosqlite:///./apps/econojin.db` یا PostgreSQL
- `SECRET_KEY` — کلید JWT یا رمزنگاری
- `ALGORITHM` — معماری JWT (مثلاً `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` — زمان انقضای توکن
- `LLM_PROVIDER` — `groq` | `gemini` | `openrouter` | `ollama` | `fake`
- `GROQ_API_KEY`, `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`, `OLLAMA_BASE_URL`
- `APP_URL` — آدرس اپ در محیط اجرا
- `ALLOWED_ORIGINS` — لیست منابع مجاز برای CORS

### Strapi CMS (`apps/cms`)

- `PUBLIC_URL` — آدرس عمومی Strapi
- `DATABASE_URL` — پایگاه‌داده Strapi (PostgreSQL یا SQLite)
- `ADMIN_JWT_SECRET` — کلید امن پنل ادمین Strapi
- `STRAPI_TOKEN` — توکن کاربردی برای webhookها و API داخلی
- `STRAPI_HOST` و `STRAPI_PORT` — میزبان و پورت سرویس Strapi در محیط لوکال

### Frontend (`apps/web/.env.local`)

- `VITE_API_BASE_URL` — آدرس بک‌اند برای فراخوانی API
- `VITE_DEFAULT_LANG` — `fa` یا `en`
- `VITE_SUPABASE_URL` — آدرس Supabase (اختیاری)
- `VITE_SUPABASE_ANON_KEY` — کلید anon Supabase
- `VITE_SENTRY_DSN` — Sentry DSN برای لاگ‌گیری
- `VITE_GA_MEASUREMENT_ID` — Google Analytics

---

## اجرای تست

```powershell
# Python backend tests
pytest tests/ -v

# Frontend type check
pnpm --filter @econojin/web type-check

# Lint global workspace
pnpm lint
```

---

## Deployment and CI

### GitHub Actions

این مخزن از فرایند CI زیر استفاده می‌کند:

- `api-tests`:
  - نصب Python 3.12
  - `pip install -r requirements.txt`
  - اجرای `pytest tests/test_api_core.py -v`
  - با `REQUIRE_AUTH_FOR_WRITES=false`
- `web-typecheck`:
  - نصب pnpm و Node.js 20
  - `pnpm --filter @econojin/web type-check`
- `playwright`:
  - `uvicorn apps/main.py --host 127.0.0.1 --port 8000 &`
  - اجرای `pnpm --filter @econojin/web test:e2e`
  - مقداردهی `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`

### Build & Deploy

- `deploy.yml`:
  - نصب Python 3.12.10
  - اجرای تست‌ها و coverage
  - ساخت و انتشار ایمیج داکر به GitHub Container Registry

### Recommended Deployment

- فرانت‌اند را به عنوان کانتینر Vite یا Cloudflare Pages منتشر کنید.
- بک‌اند را به یک سرویس FastAPI مانند Render، Fly.io یا خود-hosted Docker deploy کنید.
- اگر از Strapi استفاده می‌کنید، آن را به صورت کانتینر مجزا با `PUBLIC_URL` و `DATABASE_URL` راه‌اندازی کنید.
- برای CI، `main` و `develop` باید فقط پس از گذراندن `api-tests` و `web-typecheck` مرج شوند.

---

## اسناد مهم

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/GAP_ANALYSIS.md`](docs/GAP_ANALYSIS.md)
- [`docs/ERRORS_AND_LOGGING.md`](docs/ERRORS_AND_LOGGING.md)
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)
- [`docs/FREE_STACK.md`](docs/FREE_STACK.md)

---

## مشارکت

1. روی شاخه feature کار کنید.
2. تغییرات را با PR ارسال کنید.
3. قبل از merge تست‌ها را اجرا کنید.

---

## مجوز

این پروژه تحت مجوز موجود در فایل `License` منتشر می‌شود.

مطابق فایل [`License`](License) در ریشه مخزن.
