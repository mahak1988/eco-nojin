# Econojin (اکو نوژین)

<p align="center">
  <strong>پلتفرم جامع کشاورزی، آموزش، محیط زیست و جامعه</strong>
  <br>
  توسعه پایدار · چندزبانه · AI و مدل‌های علمی · معماری ماژولار
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react" alt="React">
  <img src="https://img.shields.io/badge/Vite-5-646CFF?logo=vite" alt="Vite">
  <img src="https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

---

## 📋 فهرست

- [معرفی](#معرفی)
- [معماری](#معماری)
- [وضعیت فعلی](#وضعیت-فعلی)
- [پیش‌نیازها](#پیش‌نیازها)
- [راه‌اندازی محلی](#راه‌اندازی-محلی)
- [ساختار پروژه](#ساختار-پروژه)
- [تکنولوژی‌ها](#تکنولوژی‌ها)
- [API Reference](#api-reference)
- [تست](#تست)
- [استقرار](#استقرار)
- [مشارکت](#مشارکت)

---

## 🚀 معرفی

**Econojin** یک پلتفرم جامع و ماژولار برای مدیریت یکپارچه حوزه‌های **کشاورزی، آب، محیط زیست، اقتصاد و جامعه** است. این پروژه با معماری **monorepo** و با استفاده از **FastAPI** در بک‌اند و **React/Vite** در فرانت‌اند ساخته شده است.

### ویژگی‌های کلیدی

- ✅ **بک‌اند FastAPI** با ۱۱+ ماژول فعال (users, auth, ai_agents, accounting, ecocoin, monitoring, simulation, alerts, ...)
- ✅ **احراز هویت JWT + OTP** با پشتیبانی از SMS (Kavenegar/Twilio)
- ✅ **پایگاه داده** SQLite (توسعه) / PostgreSQL + PostGIS (تولید)
- ✅ **AI/LLM** با پشتیبانی از Groq, Gemini, OpenRouter, Ollama
- ✅ **شبیه‌سازهای علمی** (RothC, AquaCrop)
- ✅ **EcoCoin** — ارز دیجیتال بومی برای پاداش‌های زیست‌محیطی
- ✅ **فرانت‌اند React** با ۱۶ صفحه و پشتیبانی از i18n (fa/en)
- ✅ **Docker** آماده برای استقرار
- ✅ **CI/CD** با GitHub Actions

---

## 🏗 معماری

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
│ - FastAPI app با ۱۱+ روتر ماژول                    │
│ - CORS, logging, error handlers                   │
│ - تنظیمات متمرکز از shared_core/config.py          │
└────────┬──────────────────────────────────────────┘
         │
         ▼
┌───────────────────────────────────────────────────┐
│ apps/shared_core/                                 │
│ - config.py    ← Pydantic v2 Settings (جدید)      │
│ - security.py  ← JWT + Argon2/Bcrypt (جدید)       │
│ - deps.py      ← DI pattern (جدید)                │
│ - crud.py      ← Base CRUD generic (جدید)         │
│ - database/    ← async SQLAlchemy session          │
└───────────────────────────────────────────────────┘
```

### ماژول‌های بک‌اند

| ماژول | مسیر | وضعیت |
|-------|------|--------|
| 👤 Users | `/api/v1/users` | ✅ فعال |
| 🔐 Authentication | `/api/v1/auth` | ✅ فعال (JWT + OTP) |
| 🤖 AI Agents | `/api/v1/ai-agents` | ✅ فعال |
| 💰 Accounting | `/api/v1/accounting` | ✅ فعال |
| 🪙 EcoCoin | `/api/v1/ecocoin` | ✅ فعال |
| 📊 Monitoring | `/api/v1/monitoring` | ✅ فعال |
| 🔬 Simulator | `/api/v1/simulator` | ✅ فعال |
| 🛠️ Admin | `/api/v1/admin` | ✅ فعال |
| 🔬 Simulation | `/api/v1/simulation` | ✅ فعال |
| 🏫 Agriculture Schools | `/api/v1/agriculture-schools` | ✅ فعال |
| ⚠️ Alerts | `/api/v1/alerts` | ✅ فعال |

---

## 📊 وضعیت فعلی

| لایه | وضعیت | توضیح |
|------|--------|--------|
| **بک‌اند** | ~۷۰٪ | ۱۱ روتر ماژول؛ auth/farmer/calendar با DB واقعی |
| **فرانت‌اند** | ~۴۰٪ | ۱۶ صفحه؛ calendar/weather به API وصل |
| **پنل ادمین** | ~۱۰٪ | اسکلت اولیه |
| **مدل‌های علمی** | ~۲۰٪ | RothC, AquaCrop در scripts/ |
| **زیرساخت** | ~۶۰٪ | Docker, CI/CD, Alembic migrations |

جزئیات بیشتر: [`TODO.md`](TODO.md) · [`docs/ROADMAP_FA.md`](docs/ROADMAP_FA.md)

---

## 📋 پیش‌نیازها

- **Node.js** 20+
- **pnpm** 11+
- **Python** 3.11+
- **pip**
- **Docker** (اختیاری — برای اجرا با Docker Compose)

---

## 🚀 راه‌اندازی محلی

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
# فایل .env را با مقادیر واقعی پر کنید
python apps/main.py
```

- **API:** `http://127.0.0.1:8000`
- **مستندات Swagger:** `http://127.0.0.1:8000/docs`
- **سلامت:** `http://127.0.0.1:8000/health`
- **ماژول‌ها:** `http://127.0.0.1:8000/modules`

### ۳. راه‌اندازی فرانت‌اند

```powershell
cd apps/web
copy .env.example .env.local
pnpm dev
```

- **اپ:** `http://localhost:5173`

### ۴. اجرا با Docker Compose

```powershell
docker compose -f docker-compose.apps.yml up --build
```

---

## 📁 ساختار پروژه

```
econojin.com/
├── apps/
│   ├── main.py                 # ★ نقطه ورود بک‌اند FastAPI
│   ├── conftest.py             # ★ تست fixtures (جدید)
│   ├── shared_core/            # ★ ماژول مرکزی (جدید)
│   │   ├── config.py           #   Pydantic v2 Settings
│   │   ├── security.py         #   JWT + Argon2/Bcrypt
│   │   ├── deps.py             #   Dependency Injection
│   │   ├── crud.py             #   Base CRUD Generic
│   │   └── database/           #   async SQLAlchemy
│   ├── web/                    # فرانت‌اند React/Vite
│   ├── users/                  # احراز هویت
│   ├── ai_agents/              # AI agents
│   ├── simulation/             # شبیه‌سازها
│   ├── admin_panel/            # پنل ادمین
│   ├── api/                    # API routes
│   └── cms/                    # Strapi CMS
├── packages/                   # بسته‌های اشتراکی TypeScript
│   ├── ui/                     # کامپوننت‌های UI
│   ├── types/                  # تایپ‌های مشترک
│   ├── hooks/                  # React hooks
│   └── api-client/             # API client
├── docker/                     # Dockerfileها
├── docs/                       # مستندات
├── infrastructure/             # Docker, K8s, Terraform
├── monitoring/                 # Prometheus, Grafana
├── scripts/                    # اسکریپت‌های کاربردی
├── data/                       # داده‌ها
├── database/                   # migrations
├── tests/                      # تست‌ها
└── supabase/                   # Supabase config
```

---

## 🛠 تکنولوژی‌ها

| بخش | تکنولوژی |
|-----|----------|
| **بک‌اند** | Python 3.12+, FastAPI, SQLAlchemy async, Pydantic v2, Uvicorn |
| **فرانت‌اند** | React 18, Vite 5, TypeScript, Tailwind CSS 3, Axios |
| **State Management** | Zustand + TanStack React Query |
| **Routing** | react-router-dom v6 |
| **Auth** | JWT + OTP (Argon2/Bcrypt) + Supabase (اختیاری) |
| **AI/LLM** | Groq, Gemini, OpenRouter, Ollama |
| **دیتابیس** | SQLite (dev) / PostgreSQL + PostGIS (prod) |
| **ORM** | SQLAlchemy async + Alembic |
| **Password Hashing** | Argon2 (primary) + Bcrypt (fallback) |
| **Package Manager** | pnpm 11 + Turbo repo |
| **CMS** | Strapi v5 |
| **CI/CD** | GitHub Actions |
| **Container** | Docker + Docker Compose |
| **مانیتورینگ** | Prometheus + Grafana + Sentry |

---

## 📚 API Reference

### نقاط پایانی عمومی

| مسیر | متد | توضیح |
|------|------|--------|
| `/` | GET | اطلاعات API |
| `/health` | GET | وضعیت سلامت |
| `/modules` | GET | لیست ماژول‌های فعال |
| `/docs` | GET | مستندات Swagger |
| `/redoc` | GET | مستندات ReDoc |

### نقاط پایانی احراز هویت

| مسیر | متد | توضیح |
|------|------|--------|
| `/api/v1/auth/login` | POST | ورود با ایمیل و رمز عبور |
| `/api/v1/auth/register` | POST | ثبت‌نام کاربر جدید |
| `/api/v1/auth/otp/request` | POST | درخواست کد OTP |
| `/api/v1/auth/otp/verify` | POST | تأیید کد OTP |

---

## 🧪 تست

```powershell
# Python backend tests
pytest apps/ -v

# Frontend type check
pnpm --filter @econojin/web type-check

# Lint global workspace
pnpm lint
```

---

## 🌐 استقرار

### Docker (توصیه‌شده)

```powershell
# Production build
docker compose -f docker-compose.prod.yml up --build

# Local development
docker compose -f docker-compose.apps.yml up --build
```

### استقرار دستی

- **فرانت‌اند:** Vercel / Cloudflare Pages
- **بک‌اند:** Render / Fly.io / VPS با Docker
- **دیتابیس:** Neon (PostgreSQL) / Supabase
- **CMS:** Strapi کانتینریز شده

مستندات کامل: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) · [`docs/DEPLOY_VERCEL_NEON.md`](docs/DEPLOY_VERCEL_NEON.md)

---

## 🤝 مشارکت

1. روی شاخه `feature/*` کار کنید
2. تغییرات را با PR به `develop` ارسال کنید
3. قبل از merge تست‌ها را اجرا کنید
4. از commit messages معنادار استفاده کنید

---

## 📄 مجوز

این پروژه تحت مجوز **MIT** منتشر می‌شود. فایل کامل مجوز در [`License`](License) موجود است.

---

<p align="center">
  <strong>Econojin</strong> — پلتفرمی برای توسعه پایدار و هوشمند 🌱
</p>