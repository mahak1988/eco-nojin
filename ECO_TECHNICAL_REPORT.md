# گزارش فنی جامع پروژه Econojin (اکو نوژین)

**تاریخ تهیه:** مرداد ۱۴۰۵  
**نسخه:** ۲.۰.۰  
**وضعیت:** در حال توسعه فعال  
**آخرین به‌روزرسانی:** ۲۰۲۶-۰۷-۲۸

---

## فهرست مطالب

1. [خلاصه مدیریتی](#۱-خلاصه-مدیریتی)
2. [معماری سیستم](#۲-معماری-سیستم)
3. [تحلیل بک‌اند (FastAPI / Python)](#۳-تحلیل-بک‌اند-fastapi--python)
4. [تحلیل فرانت‌اند (React / TypeScript)](#۴-تحلیل-فرانت‌اند-react--typescript)
5. [زیرساخت و DevOps](#۵-زیرساخت-و-devops)
6. [امنیت و Spider Security](#۶-امنیت-و-spider-security)
7. [ماژول‌های علمی و شبیه‌سازی](#۷-ماژول‌های-علمی-و-شبیه‌سازی)
8. [قراردادهای هوشمند (بلاکچین)](#۸-قراردادهای-هوشمند-بلاکچین)
9. [توسعه منطقه‌ای](#۹-توسعه-منطقه‌ای)
10. [تحلیل فنی عمیق بدهی فنی](#۱۰-تحلیل-فنی-عمیق-بدهی-فنی)
11. [توصیه‌های فنی استراتژیک](#۱۱-توصیه‌های-فنی-استراتژیک)

---

## ۱. خلاصه مدیریتی

### ۱.۱ نمای کلی پروژه

پروژه **Econojin** یک پلتفرم جامع **Monorepo** برای کشاورزی هوشمند، مدیریت منابع آب، محیط‌زیست، اقتصاد سبز و توسعه جوامع روستایی است. این پلتفرم با پشتیبانی از دو زبان فارسی و انگلیسی، برای ۳ کشور هدف (افغانستان، عراق، اردن) با بودجه کل **۱۹ میلیون دلار** طراحی شده است.

معماری سیستم بر پایه **FastAPI** در بک‌اند و **React 18 + Vite 5** در فرانت‌اند بنا شده و از الگوی **Monorepo** با مدیریت بسته **pnpm** (نسخه ۱۱.۴) و **Turborepo** استفاده می‌کند. بیش از ۴۵ روتر API، ۲۸ شبیه‌ساز علمی ثبت‌شده، و ۳۹+ صفحه فرانت‌اند در این پروژه توسعه یافته‌اند.

### ۱.۲ آمار فنی پروژه

| شاخص | مقدار | توضیحات |
|------|-------|---------|
| **فایل‌های Python** | ۲۲۸ | بک‌اند FastAPI با ماژول‌های متعدد |
| **فایل‌های TypeScript/TSX** | ۳۳۸ | فرانت‌اند React + بسته‌های مشترک |
| **فایل‌های Markdown** | ۹۶ | مستندات فنی و کاربری |
| **روترهای بک‌اند** | ۴۵+ | API endpoints فعال |
| **شبیه‌سازهای علمی** | ۲۸ | مدل‌های ثبت‌شده در رجیستری |
| **صفحات فرانت‌اند** | ۳۹+ | شامل داشبورد، ماژول‌ها و CMS |
| **کشورهای هدف** | ۳ | افغانستان، عراق، اردن |
| **بودجه منطقه‌ای** | $۱۹M | ۳۶ ماه برای هر کشور |
| **خطوط Spider Security** | ۴۷,۷۵۷+ | ۴ فایل امنیتی اصلی |
| **خطوط main.py** | ۲۷۲ | نقطه ورود API |

### ۱.۳ درصد پیشرفت کلی

| لایه | درصد | وضعیت | توضیحات |
|------|------|-------|---------|
| **Backend Core** | ~۷۰٪ | ✅ فعال | ۴۵+ روتر، Auth JWT/OTP، امنیت چندلایه |
| **مدل‌های علمی** | ~۴۰٪ | 🟡 در حال توسعه | RothC کامل، بقیه در transition |
| **فرانت‌اند** | ~۴۰٪ | 🟡 Partial | ۳۹+ صفحه، ۱۶ صفحه متصل به API |
| **زیرساخت** | ~۵۰٪ | 🟡 Partial | Docker + K8s آماده، CI/CD پیکربندی |
| **تست (coverage)** | ~۳۰٪ | ⚠️ نیاز به بهبود | کمتر از هدف ۷۰٪ |
| **مستندات** | ~۶۰٪ | ✅ خوب | ۹۶ فایل Markdown |

---

## ۲. معماری سیستم

### ۲.۱ معماری لایه‌ای

```plaintext
┌────────────────────────────────────────────────────────────────────────┐
│                   لایه کاربری (Presentation Layer)                     │
│  React 18 + Vite 5 + Zustand 5 + TanStack Query 5 + React Router 6    │
│  Tailwind CSS 3 + i18n (fa/en) + PWA Support                          │
└────────────────────────────────────────────────────────────────────────┘
                              │ HTTP/REST + WebSocket + JWT
                              ▼
┌────────────────────────────────────────────────────────────────────────┐
│               لایه API Gateway (FastAPI + Uvicorn)                     │
│  Middleware Stack: Security → RequestID → RateLimit → AuditLog         │
│  → SpiderGuard → CORS → Process Time Header                           │
│  Router Registration: 45+ dynamic routers (resilient loading)          │
└────────────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┬────────────────────┐
         ▼                    ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Core Modules    │  │ Scientific      │  │ Security        │  │ API Routes      │
│ users/          │  │ simulation/     │  │ spider_security/│  │ accounting      │
│ farms/          │  │ carbon_cycle/   │  │ security/       │  │ education       │
│ crops/          │  │ hydrology/      │  │ middleware/     │  │ community       │
│ water/          │  │ agriculture/    │  └─────────────────┘  │ games           │
│ ai_agents/      │  │ biodiversity/   │                       │ ecocoin         │
│ dashboard/      │  │ water_quality/  │                       │ ml              │
│ satellite/      │  │ economics/      │                       │ science         │
│ inventory/      │  │ ecosystem/      │                       │ rothc_full      │
│ planting/       │  │ soil/           │                       │ soil_suite      │
│ weather/        │  │ energy/         │                       │ ... (20+)       │
│ notifications/  │  └─────────────────┘                       └─────────────────┘
│ admin_panel/    │
└─────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   لایه داده و سرویس‌های خارجی                         │
│  PostgreSQL + PostGIS 16 │ Redis 7 │ Celery │ GEE/EO API │ Sentry    │
│  Supabase │ Open-Meteo │ Blockchain (Polygon Amoy) │ Kavenegar/Twilio │
│  SQLite (Dev) ↔ PostgreSQL (Prod) — Alembic Migrations               │
└────────────────────────────────────────────────────────────────────────┘
```

### ۲.۲ ساختار Monorepo

```
d:/econojin.com/
├── apps/                           # برنامه‌های اصلی
│   ├── main.py                     # FastAPI entrypoint (272 خط)
│   ├── shared_core/                # هسته مشترک (config, database, middleware)
│   ├── users/                      # مدیریت کاربران + JWT/OTP Auth
│   ├── ai_agents/                  # LLM Factory (Groq, OpenAI, Gemini, Ollama)
│   ├── simulation/                 # 28 شبیه‌ساز علمی
│   ├── farms/                      # مدیریت مزارع + PostGIS
│   ├── crops/                      # مدیریت محصولات
│   ├── water/                      # مدیریت آب
│   ├── planting/                   # برنامه‌ریزی کشت
│   ├── inventory/                  # انبارداری
│   ├── weather/                    # هواشناسی
│   ├── dashboard/                  # داشبورد تحلیلی
│   ├── satellite/                  # داده‌های ماهواره‌ای
│   ├── risks/                      # ارزیابی ریسک
│   ├── monitoring/                 # پایش
│   ├── notifications/              # اعلان‌ها
│   ├── admin_panel/                # پنل مدیریت
│   ├── spider_security/            # SpiderGuard
│   ├── shared_ai/                  # AI مشترک
│   ├── ml/                         # یادگیری ماشین
│   ├── api/routes/                 # 20+ روتر API
│   └── web/                        # فرانت‌اند React
├── packages/                       # بسته‌های TypeScript مشترک
│   ├── ui/                         # @econojin/ui
│   ├── types/                      # @econojin/types
│   ├── api-client/                 # @econojin/api-client
│   ├── hooks/                      # @econojin/hooks
│   └── features/                   # @econojin/features
├── security/                       # Spider Security (47,757+ خط)
│   └── middleware/
├── contracts/                      # Smart Contracts (Solidity)
│   ├── contracts/EcoCoin.sol
│   └── contracts/VerificationOracle.sol
├── infrastructure/                 # K8s, Terraform
├── data/                           # داده‌ها
├── regional_implementation/        # پیاده‌سازی منطقه‌ای
├── monitoring/                     # Prometheus + Grafana
├── docker/                         # Dockerfileها
├── docs/                           # 96 سند Markdown
├── scripts/                        # اسکریپت‌های کمکی
├── tests/                          # تست‌ها
└── agents/                         # Agent Memory
```

### ۲.۳ تکنولوژی‌های اصلی

| دسته | تکنولوژی | نسخه |
|------|----------|------|
| **Backend Framework** | FastAPI | >=0.115.0 |
| **ORM** | SQLAlchemy (Async) | >=2.0.36 |
| **Validation** | Pydantic v2 | >=2.9.0 |
| **Auth** | python-jose + passlib[bcrypt] + argon2-cffi | >=3.3.0 |
| **Task Queue** | Celery + Redis | >=5.4.0 |
| **Frontend** | React 18 + Vite 5 + Zustand 5 + TanStack Query 5 | - |
| **Styling** | Tailwind CSS 3 | 3.4.19 |
| **Container** | Docker + Docker Compose | - |
| **Orchestration** | Kubernetes (manifests ready) | - |
| **CI/CD** | GitHub Actions | - |
| **Monitoring** | Prometheus + Grafana + Sentry | - |
| **Blockchain** | Solidity + Hardhat + Polygon Amoy | - |

---

## ۳. تحلیل بک‌اند (FastAPI / Python)

### ۳.۱ نقطه ورود اصلی (`apps/main.py`)

فایل `main.py` با ۲۷۲ خط کد از معماری **plugin-based** برای بارگذاری مقاوم روترها استفاده می‌کند. خطا در یک روتر باعث crash کل API نمی‌شود.

**آمار:** ۴۵ روتر موفق / ۰ روتر ناموفق

**Middleware Stack:**
1. SecurityMiddleware (Rate Limit, UA blocking, Security Headers)
2. RequestIDMiddleware (Trace ID)
3. RateLimitMiddleware (بر اساس ENABLE_RATE_LIMIT)
4. AuditLogMiddleware (بر اساس ENABLE_AUDIT_LOG)
5. SpiderGuardMiddleware (Bot Detection - Production)
6. CORSMiddleware (Origins محدود)
7. Process Time Header

### ۳.۲ ماژول Users و احراز هویت

- JWT Token-Based (HS256/RS256)
- OTP Authentication (SMS via Kavenegar/Twilio)
- Password Hashing: bcrypt + Argon2
- Cookie-Based Sessions

### ۳.۳ ماژول AI Agents (LLM Factory)

Providerهای پشتیبانی‌شده: Groq, OpenAI, Gemini, OpenRouter, Ollama, Fake

قابلیت‌ها: Streaming (SSE), RAG Pipeline, Context Management (Redis), Multi-Turn

### ۳.۴ Database Layer

- **Dual-Mode:** SQLite (Dev) / PostgreSQL + PostGIS (Prod)
- **Auto-detection:** تشخیص خودکار asyncpg
- **Alembic:** آماده ولی نیاز به تکمیل
- **13 مدل ORM** ثبت‌شده در model_registry

---

## ۴. تحلیل فرانت‌اند (React / TypeScript)

### ۴.۱ ساختار apps/web/

```
apps/web/src/
├── app/                # Routing (Next.js-like)
├── components/         # 12 دسته کامپوننت
│   ├── layout/        # Header, Footer, Sidebar
│   ├── ui/            # Button, Card, Modal, Table
│   ├── forms/         # Form components
│   ├── charts/        # نمودارهای تعاملی
│   ├── map/           # Leaflet GIS
│   └── chatbot/       # AI Chatbot
├── pages/             # 39+ صفحه
├── api/               # API clients (Axios)
├── services/          # Supabase, Auth
├── hooks/             # useAuth, useTranslation, useTheme
├── i18n/              # fa.json, en.json
├── stores/            # Zustand stores
└── types/             # TypeScript types
```

### ۴.۲ وضعیت اتصال به API

- **متصل:** ۴۱٪ (Dashboard, Weather, Accounting, Calendar, Auth, Farms)
- **Stub/Mock:** ۴۹٪ (GIS, Education, Psychology, Community, Games)
- **در حال توسعه:** ۱۰٪ (Science, Simulation, Admin)

---

## ۵. زیرساخت و DevOps

### ۵.۱ Docker Compose

| سرویس | Image | Port |
|-------|-------|------|
| postgres | postgis/postgis:16-3.4 | 5432 |
| redis | redis:7-alpine | 6379 |
| api | Custom Build | 8000 |
| worker | Custom Build | - |
| beat | Custom Build | - |

### ۵.۲ CI/CD (GitHub Actions)

- ci.yml (Push/PR): pytest → typecheck → build
- deploy.yml (Push to main): Build → Test → Deploy
- quality-gates.yml (PR): Lint → Type Check → Security Scan
- security-scan.yml (Cron): Dependency scan → SAST

---

## ۶. امنیت و Spider Security

### ۶.۱ معماری ۵ لایه

1. **SecurityMiddleware** (14,982 خط): Rate Limiting, UA Blocking, Pattern Detection, Security Headers
2. **Anomaly Detection** (13,364 خط): Behavioral Analysis, Traffic Pattern Recognition
3. **Request Protection** (11,841 خط): SQLi/XSS/Path Traversal Prevention
4. **Fingerprinting** (7,570 خط): Request Fingerprinting, Bot Detection
5. **SpiderGuard** (apps/spider_security/): Bot UA Detection, Per-IP Rate Limiting

### ۶.۲ نقاط قوت و قابل بهبود

**قوت:** امنیت چندلایه، CORS محدود، Rate Limiting، Security Headers، Input Validation

**قابل بهبود:** Secrets Management (Vault توصیه), HTTPS/TLS, RBAC ناقص, JWT Algorithm (RS256 توصیه)

---

## ۷. ماژول‌های علمی و شبیه‌سازی

### ۷.۱ رجیستری ۲۸ شبیه‌ساز

| دسته | شبیه‌سازها | وضعیت |
|------|-----------|--------|
| Climate | ClimateSimulator | 🟡 Stub |
| Urban | UrbanSimulator | 🟡 Stub |
| Agriculture | APSIM, DSSAT, AquaCrop, WOFOST, CropModel | 🟡 Stub |
| Hydrology | SWAT, MODFLOW, WEAP, HECRAS, Bridge | 🟡 Stub |
| Carbon Cycle | RothC, CO2FIX, Century | ✅ RothC کامل |
| Economics | ABM, TEEB, CBA | 🟡 Stub |
| Ecosystem | InVEST, ARIES | 🟡 Stub |
| Energy | HOMER, LEAP | 🟡 Stub |
| Soil | EPIC, RUSLE2 | 🟡 Stub |
| Water Quality | QUAL2K, WASP | 🟡 Stub |
| Biodiversity | MaxEnt, iTree | 🟡 Stub |

### ۷.۲ RothC-26.3 (کامل)

مدل چرخه کربن خاک با ورودی‌های اقلیم، مدیریت خاک و پوشش گیاهی. خروجی: SOC stock, CO2 flux, Decomposition rates.

---

## ۸. قراردادهای هوشمند (بلاکچین)

### ۸.۱ EcoCoin.sol

توکن زیست‌محیطی ERC-20 با قابلیت‌های Minting/Burning, Pausable, Access Control, Carbon Credit Integration. شبکه هدف: Polygon Amoy.

### ۸.۲ VerificationOracle.sol

اوراکل اعتبارسنجی برای تأیید داده‌های MRV خارج از زنجیره، با Multi-Sig Validation و Timestamping.

**ابزارها:** Hardhat ^2.22.0, TypeChain, Solhint

---

## ۹. توسعه منطقه‌ای

| کشور | بودجه | پایلوت‌ها | کاربران |
|------|-------|-----------|---------|
| افغانستان | $۷M | ۳ | ۱,۰۰۰ خانوار |
| عراق | $۶M | ۳ | ۱,۰۰۰ خانوار |
| اردن | $۶M | ۳ | ۱,۰۰۰ خانوار |
| **مجموع** | **$۱۹M** | **۹** | **۳,۰۰۰ خانوار** |

**KPI:** ۳۰,۰۰۰ هکتار زمین، ۱۵,۰۰۰ tCO2e ترسیب کربن، ۲۰٪ کاهش مصرف آب، ۳۰٪ افزایش بهره‌وری

---

## ۱۰. تحلیل فنی عمیق بدهی فنی

### ۱۰.۱ دسته‌بندی بدهی فنی

| دسته | شدت | توضیحات |
|------|------|---------|
| **یکپارچگی علمی** | 🔴 Critical | ۲۳/۲۸ مدل Stub، جدا از API |
| **تست و کیفیت** | 🔴 High | Coverage < ۳۰٪، TypeScript non-strict |
| **Database** | 🔴 High | Alembic ناقص، Schema Patches موقتی |
| **FE/BE Integration** | 🟡 Medium | ۴۱٪ اتصال، Error Handling不一致 |
| **امنیت** | 🟡 Medium | Secrets در .env، RBAC ناقص |
| **مستندات** | 🟢 Low | ۶۰٪ کامل |

### ۱۰.۲ اولویت‌بندی

**فاز ۰ (۲ هفته):** Alembic Migrations (P0), Response Schemas (P0), Test Coverage 70% (P0), Security Issues (P0)

**فاز ۱ (۴ هفته):** Scientific Models Migration, Celery Integration, PostGIS, RBAC

**فاز ۲ (۴ هفته):** API Integration (10 pages), TypeScript Strict, Error Handling

### ۱۰.۳ Quality Gates

| شاخص | حداقل | هدف |
|------|-------|-----|
| Test Coverage (Backend) | ۵۰٪ | ۷۰٪ |
| Ruff Score | ۸/۱۰ | ۹/۱۰ |
| API Response Time (p95) | < ۵۰۰ms | < ۲۰۰ms |
| Pages Connected | ۵۰٪ | ۸۰٪ |

---

## ۱۱. توصیه‌های فنی استراتژیک

### ۱۱.۱ کوتاه‌مدت (۲ هفته)

1. **Alembic Migrations:** `alembic revision --autogenerate -m "initial_schema"`
2. **API Standardization:** الگوی یکسان Response
3. **Test Coverage:** تمرکز بر ماژول‌های حیاتی

### ۱۱.۲ میان‌مدت (۴ هفته)

4. **Scientific Migration:** انتقال ۲۳ مدل Stub به API، پیاده‌سازی ۵ مدل کلیدی
5. **Celery Integration:** Redis broker, Flower monitoring
6. **PostGIS Activation:** Spatial indexes

### ۱۱.۳ بلندمدت (۸+ هفته)

7. **Production Deployment:** TLS, Monitoring, Disaster Recovery
8. **Regional Pilots:** شروع در افغانستان
9. **Blockchain:** استقرار EcoCoin.sol, ممیزی امنیتی
10. **PWA:** Service Workers, Offline Mode

### ۱۱.۴ نتیجه‌گیری نهایی

**Econojin** یک پلتفرم جامع با معماری فنی قوی و پتانسیل بالا برای تأثیرگذاری در کشاورزی پایدار خاورمیانه است.

**نقاط قوت:** معماری ماژولار، امنیت چندلایه، i18n کامل، مستندات غنی، Docker/K8s آماده

**چالش‌ها:** یکپارچگی علمی ناقص، Test Coverage پایین، Migrations ناقص، اتصال FE/BE ۴۱٪

**توصیه:** تمرکز بر فاز ۰ (تثبیت پایه) و فاز ۱ (تکمیل بک‌اند) پیش از گسترش قابلیت‌ها. دستیابی به Production-Ready در ۶ ماه.

---

## پیوست‌ها

### دستورات مفید

```bash
pnpm dev                          # توسعه محلی
pytest apps/ -v --cov=apps        # تست
alembic upgrade head              # Migration
docker compose -f docker-compose.prod.yml up -d  # استقرار
cd contracts && npx hardhat test  # تست قراردادها
ruff check apps/ --fix            # Linting
```

### مستندات مرتبط

| سند | مسیر |
|-----|------|
| README | `README.md` |
| برنامه توسعه | `DEVELOPMENT_PLAN.md` |
| TODO | `TODO.md` |
| معماری | `docs/ARCHITECTURE.md` |
| API | `docs/API.md` |

---

**تهیه‌شده توسط:** دستیار هوشمند تحلیل کد  
**بر اساس بررسی:** ۵۶۶ فایل کد (Python + TypeScript) و ۹۶ سند مستندات  
**تاریخ:** مرداد ۱۴۰۵ | **نسخه:** ۲.۰.۰
