# Econojin (اکو نوژین)

پلتفرم جامع علمی-کاربردی برای کشاورزی پایدار، آموزش، محیط زیست و توسعه جامعه

> **نسخه:** 1.0.0 | **Python:** 3.10+ | **Node.js:** 20+ | **مجوز:** MIT

**ویژگی‌های کلیدی:**
- 🌱 مدل‌سازی اکولوژیکی و ردیابی کربن
- 🤖 هوش مصنوعی و عوامل خودمختار (AI Agents)
- 📊 شبیه‌سازی‌های علمی (AquaCrop, RothC, SWAT+)
- 🌍 پشتیبانی چندزبانه (فارسی/انگلیسی)
- 🔐 امنیت چندلایه با JWT و Rate Limiting
- 📦 معماری ماژولار با بسته‌های مشترک

---

## وضعیت فعلی پروژه

| لایه | وضعیت | توضیح |
|------|--------|--------|
| Backend | ~۶۰٪ | FastAPI در `apps/main.py`، ۱۵ روتر ماژول، Auth/Farmer/Calendar متصل به DB |
| Frontend | ~۴۰٪ | React + Vite در `apps/web/`، ۱۶ صفحه، Axios، Supabase auth |
| Admin Panel | ~۱۰٪ | اسکلت Next.js در `apps/admin_panel/` |
| CMS | آماده | Strapi v5 در `apps/cms/` برای محتوا و مقالات |
| Scientific Models | ~۲۰٪ | در `apps/simulation/` و `scripts/` (AquaCrop, RothC, SWAT+, HECHMS) |
| AI Agents | فعال | `apps/ai_agents/` با LLM Factory (Groq, Gemini, OpenRouter, Ollama) |
| Shared Packages | کامل | `packages/*` برای UI، types، config، hooks، features، api-client |

📋 **کارهای باز:** [`TODO.md`](TODO.md)  
🗺️ **نقشه راه:** [`docs/ROADMAP_FA.md`](docs/ROADMAP_FA.md)  
📊 **تحلیل وابستگی:** [`apps/dependency_report.txt`](apps/dependency_report.txt)

---

## معماری کلی

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ apps/web/    │  │ apps/admin/  │  │ apps/cms/    │      │
│  │ React + Vite │  │ Next.js      │  │ Strapi v5    │      │
│  │ Axios        │  │ Axios        │  │ Content API  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          │   HTTP/REST     │   HTTP/REST     │   HTTP/REST
          │   JWT Auth      │   JWT Auth      │   API Token
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              apps/main.py (FastAPI)                   │   │
│  │  - CORS Middleware                                    │   │
│  │  - Rate Limiting                                      │   │
│  │  - Security Headers                                   │   │
│  │  - Global Error Handlers                              │   │
│  │  - Request Timing                                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
          │
          │ Router Registration
          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Module Routers                            │
│  /api/v1/users      /api/v1/auth       /api/v1/farmers      │
│  /api/v1/calendar   /api/v1/weather    /api/v1/accounting   │
│  /api/v1/gis        /api/v1/education  /api/v1/psychology   │
│  /api/v1/ecomining  /api/v1/store      /api/v1/library      │
│  /api/v1/community  /api/v1/games      /api/v1/simulation   │
│  /api/v1/ai-agents  /api/v1/iot        /api/v1/dashboard    │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Shared Core Services                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ shared_core/ │  │ shared_ai/   │  │ shared_sim/  │      │
│  │ - DB Session │  │ - LLM Factory│  │ - Sim Utils  │      │
│  │ - CRUD Base  │  │ - RAG Tools  │  │ - Models     │      │
│  │ - Utilities  │  │ - Prompts    │  │ - Repository │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────────────────────────────────────────┐       │
│  │           shared_knowledge/                       │       │
│  │  - Knowledge Modeling & Content Store             │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ SQLite/      │  │ File System  │  │ External     │      │
│  │ PostgreSQL   │  │ (data/)      │  │ APIs         │      │
│  │ + PostGIS    │  │ - climate    │  │ - ERA5       │      │
│  │ + Alembic    │  │ - mrv        │  │ - Sentinel-2 │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## ساختار مخزن

```
/workspace/
├── apps/                          # برنامه‌های اصلی
│   ├── main.py                    # نقطه ورود FastAPI
│   ├── api/                       # ماژول API و utilities
│   ├── users/                     # احراز هویت و مدیریت کاربران
│   ├── ai_agents/                 # عوامل هوش مصنوعی و streaming
│   ├── simulation/                # APIهای شبیه‌سازی علمی
│   │   ├── agriculture/           # مدل‌های کشاورزی
│   │   ├── biodiversity/          # تنوع زیستی
│   │   ├── carbon_cycle/          # چرخه کربن
│   │   ├── economics/             # اقتصاد محیط زیست
│   │   ├── energy/                # انرژی‌های تجدیدپذیر
│   │   ├── hydrology/             # هیدرولوژی (SWAT+, HECHMS)
│   │   ├── soil/                  # سلامت خاک
│   │   └── water_quality/         # کیفیت آب
│   ├── shared_core/               # جلسه دیتابیس و utilities
│   ├── shared_ai/                 # ابزارهای AI و RAG
│   ├── shared_knowledge/          # مدل‌سازی دانش
│   ├── shared_sim/                # ابزارهای مشترک شبیه‌سازی
│   ├── admin_panel/               # پنل مدیریت (Next.js)
│   ├── web/                       # فرانت‌اند (React + Vite)
│   └── cms/                       # سیستم مدیریت محتوا (Strapi)
├── packages/                      # بسته‌های TypeScript مشترک
│   ├── api-client/                # کلاینت API
│   ├── ui/                        # کامپوننت‌های UI
│   ├── types/                     # تعاریف نوع
│   ├── hooks/                     # React hooks مشترک
│   ├── features/                  # ویژگی‌های مشترک
│   ├── lib/                       # کتابخانه‌های کمکی
│   ├── config-eslint/             # پیکربندی ESLint
│   └── config-typescript/         # پیکربندی TypeScript
├── data/                          # داده‌ها
│   ├── climate_zones/             # مناطق اقلیمی
│   ├── mrv/                       # پروتکل‌های MRV
│   ├── pilots/                    # داده‌های پایلوت
│   ├── training_content/          # محتوای آموزشی
│   └── offline_content/           # محتوای آفلاین
├── knowledge_hub/                 # مرکز دانش
│   └── exportable_packages/       # بسته‌های دانش قابل صادرات
├── agents/                        # عوامل خودمختار
│   └── memory/                    # حافظه عوامل
├── infrastructure/                # زیرساخت
│   ├── docker/                    # فایل‌های Docker
│   ├── kubernetes/                # маниفست‌های K8s
│   ├── nginx/                     # پیکربندی Nginx
│   ├── security/                  # ابزارهای امنیتی
│   ├── terraform/                 # کدهای Terraform
│   ├── backup/                    # اسکریپت‌های backup
│   ├── coolify/                   # پیکربندی Coolify
│   └── mosquitto/                 # MQTT Broker
├── monitoring/                    # مانیتورینگ
│   ├── prometheus/                # Prometheus config
│   ├── grafana/                   # داشبوردهای Grafana
│   └── alertmanager/              # مدیریت هشدارها
├── database/                      # مهاجرت‌های دیتابیس
│   └── migrations/
├── supabase/                      # مهاجرت‌های Supabase
│   └── migrations/
├── alembic/                       # مهاجرت‌های Alembic
│   └── versions/
├── docker/                        # Dockerfiles
│   └── db/
├── docs/                          # مستندات
│   ├── architecture/              # مستندات معماری
│   ├── global_expansion/          # گسترش جهانی
│   ├── knowledge_base/            # پایگاه دانش
│   ├── launch/                    # راهنمای راه‌اندازی
│   ├── mrv/                       # مستندات MRV
│   ├── operational_training/      # آموزش عملیاتی
│   ├── performance/               # بهینه‌سازی عملکرد
│   ├── policy_briefs/             # خلاصه سیاست‌ها
│   ├── runbooks/                  # Runbooks عملیاتی
│   ├── safeguards/                # پروتکل‌های ایمنی
│   ├── stories/                   # داستان‌های کاربر
│   └── summaries/                 # خلاصه‌ها
├── infra/                         # Kubernetes manifests
│   ├── k8s/
│   └── prometheus/
├── regional_implementation/       # پیاده‌سازی منطقه‌ای
│   ├── afghanistan/
│   ├── iraq/
│   ├── jordan/
│   ├── mena_ilm_network/
│   └── finance/
├── scalability/                   # مقیاس‌پذیری
│   ├── international/
│   ├── national/
│   └── regional/
├── scripts/                       # اسکریپت‌های کمکی
│   └── builders/
├── legal/                         # اسناد حقوقی
│   ├── privacy_policy.md
│   └── service_agreement.ricardian.md
├── reports/                       # گزارش‌های تولید شده
├── output/                        # خروجی‌های تحلیل
├── early_warning_engine/          # موتور هشدار زودهنگام
├── package.json                   # Monorepo scripts
├── pnpm-workspace.yaml            # Workspace config
├── turbo.json                     # Turbo tasks
├── pyproject.toml                 # Python project config
├── docker-compose.yml             # Docker Compose اصلی
├── docker-compose.apps.yml        # Stack محلی
├── docker-compose.db.yml          # سرویس‌های دیتابیس
├── docker-compose.prod.yml        # پیکربندی production
├── .env.example                   # نمونه متغیرهای محیطی بک‌اند
└── apps/web/.env.example          # نمونه متغیرهای محیطی فرانت
```

---

## پیش‌نیازها

### الزامات اصلی
- **Node.js** 20+ ([دانلود](https://nodejs.org/))
- **pnpm** 11+ (`npm install -g pnpm`)
- **Python** 3.11+ ([دانلود](https://python.org/))
- **pip** (همراه Python نصب می‌شود)

### اختیاری
- **Docker** و **Docker Compose** برای اجرای کانتینری
- **PostgreSQL** 14+ برای production (با PostGIS)
- **Git** برای کنترل نسخه

---

## راه‌اندازی محلی

### ۱. نصب وابستگی‌ها

#### Linux/macOS
```bash
cd /workspace
pnpm install

# محیط مجازی Python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Windows (PowerShell)
```powershell
cd d:\econojin.com
pnpm install

# محیط مجازی Python
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### ۲. پیکربندی متغیرهای محیطی

```bash
# بک‌اند
cp .env.example .env
# فایل .env را با مقادیر واقعی پر کنید

# فرانت‌اند
cp apps/web/.env.example apps/web/.env.local
```

### ۳. راه‌اندازی بک‌اند

```bash
# فعال‌سازی محیط مجازی (اگر قبلاً فعال نکرده‌اید)
source .venv/bin/activate  # Linux/macOS
# یا
.\.venv\Scripts\activate   # Windows

# اجرای سرور FastAPI
python apps/main.py
# یا با uvicorn مستقیم
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

**دسترسی:**
- API: `http://127.0.0.1:8000`
- مستندات Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- سلامت: `http://127.0.0.1:8000/health`

### ۴. راه‌اندازی فرانت‌اند

```bash
cd apps/web
pnpm dev
```

**دسترسی:** `http://localhost:5173`

### ۵. راه‌اندازی پنل ادمین (در حال توسعه)

```bash
cd apps/admin_panel
pnpm install
pnpm dev
```

### ۶. راه‌اندازی CMS (اختیاری)

```bash
cd apps/cms
pnpm install
pnpm dev
```

**دسترسی:** `http://localhost:1337`

### ۷. اجرای هم‌زمان با Turbo

```bash
# اجرای تمام سرویس‌ها
pnpm dev

# یا سرویس‌های خاص
pnpm dev:web     # فقط فرانت‌اند
pnpm dev:cms     # فقط CMS
pnpm dev:admin   # فقط پنل ادمین
```

### ۸. اجرای محلی با Docker Compose

```bash
# stack کامل
docker compose -f docker-compose.apps.yml up --build

# فقط سرویس‌های دیتابیس
docker compose -f docker-compose.db.yml up -d

# production-ready
docker compose -f docker-compose.prod.yml up -d
```

---

## متغیرهای محیطی مهم

### Backend (`.env`)

| متغیر | توضیح | مثال |
|-------|-------|------|
| `DATABASE_URL` | رشته اتصال دیتابیس | `sqlite+aiosqlite:///./apps/econojin.db` یا `postgresql+asyncpg://user:pass@localhost:5432/econojin` |
| `SECRET_KEY` | کلید JWT/رمزنگاری | `your-super-secret-key-here` |
| `ALGORITHM` | الگوریتم JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | زمان انقضای توکن | `30` |
| `LLM_PROVIDER` | ارائه‌دهنده LLM | `groq`, `gemini`, `openrouter`, `ollama`, `fake` |
| `GROQ_API_KEY` | کلید API Groq | `gsk_xxx` |
| `GOOGLE_API_KEY` | کلید API Google | `xxx` |
| `OPENROUTER_API_KEY` | کلید API OpenRouter | `sk-or-xxx` |
| `OLLAMA_BASE_URL` | آدرس Ollama | `http://localhost:11434` |
| `APP_URL` | آدرس برنامه | `http://localhost:8000` |
| `ALLOWED_ORIGINS` | منابع CORS مجاز | `http://localhost:5173,http://localhost:3000` |
| `REQUIRE_AUTH_FOR_WRITES` | نیاز به احراز برای عملیات نوشتن | `true`/`false` |

### Strapi CMS (`apps/cms/.env`)

| متغیر | توضیح |
|-------|-------|
| `PUBLIC_URL` | آدرس عمومی Strapi |
| `DATABASE_URL` | پایگاه‌داده Strapi |
| `ADMIN_JWT_SECRET` | کلید امن پنل ادمین |
| `STRAPI_TOKEN` | توکن API برای webhookها |
| `STRAPI_HOST` | میزبان Strapi |
| `STRAPI_PORT` | پورت Strapi |

### Frontend (`apps/web/.env.local`)

| متغیر | توضیح | مقدار پیش‌فرض |
|-------|-------|--------------|
| `VITE_API_BASE_URL` | آدرس بک‌اند | `http://localhost:8000` |
| `VITE_DEFAULT_LANG` | زبان پیش‌فرض | `fa` |
| `VITE_SUPABASE_URL` | آدرس Supabase | (اختیاری) |
| `VITE_SUPABASE_ANON_KEY` | کلید anon Supabase | (اختیاری) |
| `VITE_SENTRY_DSN` | Sentry DSN | (اختیاری) |
| `VITE_GA_MEASUREMENT_ID` | Google Analytics ID | (اختیاری) |

---

## اجرای تست

### تست‌های Python Backend

```bash
# فعال‌سازی محیط مجازی
source .venv/bin/activate

# اجرای همه تست‌ها
pytest tests/ -v

# با coverage
pytest tests/ -v --cov=apps --cov-report=html

# تست‌های خاص
pytest tests/test_api_core.py -v
pytest tests/test_auth.py -v
```

### تست‌های TypeScript/JavaScript

```bash
# بررسی نوع
pnpm type-check

# یا برای پروژه خاص
pnpm --filter @econojin/web type-check

# Lint
pnpm lint

# یا برای پروژه خاص
pnpm --filter @econojin/web lint
```

### تست‌های End-to-End (Playwright)

```bash
# شروع بک‌اند
uvicorn apps.main.py --host 127.0.0.1 --port 8000 &

# اجرای تست‌های E2E
pnpm --filter @econojin/web test:e2e
```

---

## Deployment و CI/CD

### GitHub Actions

این مخزن از workflowهای زیر استفاده می‌کند:

| Workflow | توضیح |
|----------|-------|
| `api-tests` | تست‌های Python backend با pytest |
| `web-typecheck` | بررسی نوع TypeScript فرانت‌اند |
| `playwright` | تست‌های E2E با Playwright |
| `deploy.yml` | ساخت و انتشار Docker image به GHCR |

### استقرار توصیه شده

#### گزینه ۱: Cloud Platform
- **فرانت‌اند:** Vercel، Netlify، یا Cloudflare Pages
- **بک‌اند:** Render، Fly.io، Railway، یا AWS ECS
- **CMS:** کانتینر جداگانه با PostgreSQL
- **دیتابیس:** Neon، Supabase، یا AWS RDS (PostgreSQL + PostGIS)

#### گزینه ۲: Self-hosted با Docker
```bash
# production-ready stack
docker compose -f docker-compose.prod.yml up -d

# مانیتورینگ
docker compose -f docker-compose.prod.yml up prometheus grafana
```

#### گزینه ۳: Kubernetes
```bash
# اعمال manifestها
kubectl apply -f infrastructure/kubernetes/

# یا با Helm (در صورت موجود بودن)
helm install econojin ./infrastructure/helm
```

### Best Practices برای Production

1. **HTTPS اجباری** با گواهی SSL معتبر
2. **چرخش منظم `JWT_SECRET`** هر ۹۰ روز
3. **Backup خودکار دیتابیس** روزانه
4. **WAF / Cloudflare** در لبه شبکه
5. **Rate Limiting** سخت‌گیرانه‌تر
6. **Monitoring** با Prometheus/Grafana
7. **Logging متمرکز** با ELK Stack یا Loki

---

## اسناد مهم

### مستندات فنی
- 📐 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - نمای کلی معماری
- 📊 [`docs/GAP_ANALYSIS.md`](docs/GAP_ANALYSIS.md) - تحلیل شکاف‌ها
- 📝 [`docs/ERRORS_AND_LOGGING.md`](docs/ERRORS_AND_LOGGING.md) - خطاها و لاگ‌گیری
- 🚀 [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) - راهنمای استقرار
- 💰 [`docs/FREE_STACK.md`](docs/FREE_STACK.md) - پشته رایگان

### مستندات عملیاتی
- 📖 [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) - راهنمای مشارکت
- 🗺️ [`docs/ROADMAP_FA.md`](docs/ROADMAP_FA.md) - نقشه راه فارسی
- 🔒 [`docs/SECURITY.md`](docs/SECURITY.md) - امنیت چندلایه
- 📋 [`TODO.md`](TODO.md) - کارهای باز

### مستندات تخصصی
- 🌍 [`docs/global_expansion/`](docs/global_expansion/) - گسترش جهانی
- 🧠 [`docs/knowledge_base/`](docs/knowledge_base/) - پایگاه دانش
- 📈 [`docs/mrv/`](docs/mrv/) - پروتکل‌های MRV
- ⚡ [`docs/performance/`](docs/performance/) - بهینه‌سازی عملکرد
- 🛡️ [`docs/safeguards/`](docs/safeguards/) - پروتکل‌های ایمنی

---

## مشارکت

### نحوه مشارکت

1. **Fork** کردن مخزن
2. ایجاد شاخه feature (`git checkout -b feature/amazing-feature`)
3. **Commit** تغییرات (`git commit -m 'Add amazing feature'`)
4. **Push** به شاخه (`git push origin feature/amazing-feature`)
5. باز کردن **Pull Request**

### استانداردهای کد

#### Python
- رعایت PEP 8
- استفاده از type hints
- پوشش تست حداقل ۸۰٪
- Docstring برای توابع عمومی

```bash
# فرمت کد
black apps/
isort apps/

# بررسی
ruff check apps/
mypy apps/
```

#### TypeScript/JavaScript
- رعایت ESLint config پروژه
- استفاده از TypeScript strict mode
- کامپوننت‌های React با functional approach

```bash
# فرمت و lint
pnpm lint
pnpm format
```

### قبل از Merge

```bash
# اجرای همه تست‌ها
pytest tests/ -v
pnpm test

# بررسی نوع
pnpm type-check

# Build
pnpm build
```

---

## جامعه و پشتیبانی

- 📧 ایمیل: info@econojin.com
- 💬 کانال ارتباطی: [لینک]
- 🐛 گزارش باگ: [GitHub Issues](../../issues)
- 💡 درخواست ویژگی: [GitHub Discussions](../../discussions)

---

## مجوز

این پروژه تحت مجوز **MIT** منتشر می‌شود.

مشاهده متن کامل مجوز در فایل [`License`](License).

```
MIT License

Copyright (c) 2024 Econojin Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
```

---

## قدردانی

با تشکر از تمامی مشارکت‌کنندگان و حامیان پروژه Econojin.

🌱 **ساخته شده با ❤️ برای کشاورزی پایدار و توسعه جامعه**
