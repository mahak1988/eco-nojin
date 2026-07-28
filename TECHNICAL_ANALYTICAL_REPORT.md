# گزارش فنی و تحلیلی پروژه Econojin (اکو نوژین)

**تاریخ تهیه:** تیر ۱۴۰۵  
**نسخه پلتفرم:** 2.0.0  
**وضعیت پروژه:** در حال توسعه فعال  

---

## فهرست مطالب

1. [خلاصه اجرایی](#۱-خلاصه-اجرایی)
2. [معماری سیستم](#۲-معماری-سیستم)
3. [تحلیل فنی بک‌اند](#۳-تحلیل-فنی-بک‌اند)
4. [تحلیل فنی فرانت‌اند](#۴-تحلیل-فنی-فرانت‌اند)
5. [زیرساخت و DevOps](#۵-زیرساخت-و-devops)
6. [امنیت](#۶-امنیت)
7. [ماژول‌های علمی و شبیه‌سازی](#۷-ماژول‌های-علمی-و-شبیه‌سازی)
8. [توسعه منطقه‌ای](#۸-توسعه-منطقه‌ای)
9. [تحلیل شکاف‌ها و ریسک‌ها](#۹-تحلیل-شکاف‌ها-و-ریسک‌ها)
10. [نتایج و پیشنهادات](#۱۰-نتایج-و-پیشنهادات)

---

## ۱. خلاصه اجرایی

### معرفی پروژه
Econojin یک پلتفرم جامع monorepo برای کشاورزی پایدار، آموزش، محیط زیست و اقتصاد است که با معماری ماژولار و چندزبانه طراحی شده است. این پلتفرم از FastAPI برای بک‌اند و React/Vite برای فرانت‌اند استفاده می‌کند.

### آمار کلیدی پروژه
| شاخص | مقدار |
|------|-------|
| فایل‌های Python | ۲۲۸ فایل |
| فایل‌های TypeScript/TSX | ۳۳۸ فایل |
| اسناد Markdown | ۹۶ فایل |
| ماژول‌های بک‌اند | ۱۵+ روتر |
| صفحات فرانت‌اند | ۳۹+ صفحه |
| کشورهای هدف | ۳ کشور (افغانستان، عراق، اردن) |
| بودجه منطقه‌ای | ۱۹,۰۰۰,۰۰۰ دلار |

### وضعیت کلی توسعه
| لایه | درصد پیشرفت | وضعیت |
|------|-------------|--------|
| Backend | ~۶۰٪ | فعال - ۱۵+ روتر ماژول |
| Frontend | ~۴۰٪ | فعال - React + Vite |
| CMS | ~۳۰٪ | Strapi v5 |
| Scientific Models | ~۲۰٪ | در حال انتقال از scripts به API |
| Infrastructure | ~۵۰٪ | Docker + Kubernetes آماده |

---

## ۲. معماری سیستم

### ۲.۱ ساختار Monorepo

```
/workspace/
├── apps/                      # برنامه‌های اصلی
│   ├── main.py               # نقطه ورود FastAPI
│   ├── users/                # مدیریت کاربران و احراز هویت
│   ├── ai_agents/            # عامل‌های هوش مصنوعی
│   ├── simulation/           # APIs شبیه‌سازی
│   ├── shared_core/          # هسته مشترک (DB، امنیت)
│   ├── shared_ai/            # ماژول‌های AI مشترک
│   ├── web/                  # فرانت‌اند React
│   └── cms/                  # Strapi CMS
├── packages/                  # بسته‌های TypeScript مشترک
│   ├── api-client/           # کلاینت API
│   ├── ui/                   # کامپوننت‌های UI
│   ├── types/                # تعاریف نوع
│   └── hooks/                # Hooks سفارشی
├── infrastructure/            # زیرساخت استقرار
│   ├── docker/               # پیکربندی Docker
│   ├── kubernetes/           # مانفیست‌های K8s
│   ├── terraform/            # کدهای IaC
│   └── security/             # پیکربندی امنیت
├── data/                      # داده‌های آموزشی و پردازش
├── docs/                      # مستندات فنی
└── regional_implementation/   # پیاده‌سازی منطقه‌ای
```

### ۲.۲ جریان داده

```
┌───────────────────┐          ┌───────────────────┐
│ apps/web/         │          │ apps/cms/         │
│ - Vite + React    │          │ - Strapi v5       │
│ - Axios/Supabase  │          │ - محتوای CMS      │
└────────┬──────────┘          └────────┬──────────┘
         │                              │
         │ HTTP/REST/JWT                │
         ▼                              │
┌───────────────────────────────────────────────────┐
│ apps/main.py (FastAPI)                            │
│ - CORS، Logging، Error Handlers                   │
│ - Security Middleware (Spider Security)           │
│ - Routerهای: Users، Auth، AI Agents، Simulation   │
└────────┬──────────────────────────────────────────┘
         │
         ▼
┌───────────────────────────────────┐
│ apps/shared_core/                 │
│ - Async SQLAlchemy Session        │
│ - Database Utilities              │
│ - Security & Protection           │
└───────────────────────────────────┘
```

### ۲.۳ تکنولوژی‌های اصلی

#### Backend (Python)
| دسته | تکنولوژی | نسخه |
|------|----------|------|
| Framework | FastAPI | >=0.115.0 |
| ORM | SQLAlchemy (Async) | >=2.0.30 |
| Database | PostgreSQL/SQLite | Asyncpg/Aiosqlite |
| Validation | Pydantic v2 | >=2.7.0 |
| Auth | python-jose، passlib | - |
| Cache | Redis | >=5.0.0 |
| Tasks | Celery + Flower | >=5.4.0 |
| Geo | Shapely، GeoJSON | - |

#### Frontend (TypeScript)
| دسته | تکنولوژی | نسخه |
|------|----------|------|
| Framework | React | 18.3.1 |
| Build Tool | Vite | 5.4.21 |
| State | Zustand | 5.0.14 |
| Data Fetching | TanStack Query | 5.101.2 |
| Routing | React Router | 6.30.4 |
| Styling | Tailwind CSS | 3.4.19 |
| HTTP | Axios | 1.17.0 |
| Auth | Supabase JS | 2.10.8 |

---

## ۳. تحلیل فنی بک‌اند

### ۳.۱ نقطه ورود اصلی (`apps/main.py`)

فایل `main.py` با ۲۷۲ خط کد، هسته مرکزی بک‌اند است:

**ویژگی‌های کلیدی:**
- ✅ پیکربندی Logging ساختاریافته
- ✅ مدیریت رویدادهای lifespan (startup/shutdown)
- ✅ Middlewareهای امنیتی چندلایه
- ✅ ثبت خودکار routerها با error handling
- ✅ Health check و root endpoints

**Middlewareهای امنیتی:**
1. **CORS Middleware** - کنترل دسترسی با اعتبارسنجی origins
2. **Security Headers Middleware** - هدرهای امنیتی HTTP
3. **Spider Security Middleware** - سیستم امنیت اختصاصی
4. **Process Time Header** - مانیتورینگ عملکرد

**Routerهای ثبت‌شده:**
| مسیر | پیشوند | توضیح |
|------|--------|-------|
| Users | `/api/v1/users` | مدیریت کاربران |
| Auth | `/api/v1` | احراز هویت JWT/OTP |
| AI Agents | `/api/v1/ai-agents` | چت‌بات و RAG |
| Admin | `/api/v1` | پنل مدیریت |
| Simulation | `/api/v1/simulation` | APIs شبیه‌سازی |

### ۳.۲ ماژول‌های اصلی

#### الف) ماژول Users (`apps/users/`)
- **تعداد خطوط:** ۱۲۰+ خط در router
- **قابلیت‌ها:**
  - CRUD کامل کاربران
  - پروفایل کاربری
  - OTP (request/verify)
  - ادغام با Supabase (اختیاری)

#### ب) ماژول AI Agents (`apps/ai_agents/`)
- **تعداد خطوط:** ۲۸۷ خط در router
- **قابلیت‌ها:**
  - Streaming responses
  - LLM Factory (Groq، Gemini، OpenRouter، Ollama)
  - RAG tools
  - Context management

#### ج) ماژول Simulation (`apps/simulation/`)
- **ساختار:**
```
simulation/
├── agriculture/      # مدل‌های کشاورزی
├── biodiversity/     # تنوع زیستی
├── carbon_cycle/     # چرخه کربن (RothC)
├── economics/        # اقتصاد کشاورزی
├── hydrology/        # هیدرولوژی (AquaCrop)
├── soil/             # علوم خاک
└── water_quality/    # کیفیت آب
```
- **مدل‌های پیاده‌سازی‌شده:**
  - RothC-full (کربن خاک)
  - AquaCrop (عملکرد محصول)
  - Coupling Engine (ادغام مدل‌ها)

### ۳.۳ لایه امنیت عنکبوتی (`apps/shared_core/security/`)

این ماژول یک سیستم امنیتی چندلایه اختصاصی است:

| فایل | اندازه | مسئولیت |
|------|--------|---------|
| `middleware.py` | ۱۴,۹۸۲ خط | Middlewareهای امنیتی |
| `anomaly.py` | ۱۳,۳۶۴ خط | تشخیص ناهنجاری |
| `protection.py` | ۱۱,۸۴۱ خط | محافظت در برابر حملات |
| `fingerprint.py` | ۷,۵۷۰ خط | اثرانگشت درخواست |

**قابلیت‌های امنیتی:**
- ✅ Security Headers (CSP، X-Frame-Options، etc.)
- ✅ Rate Limiting
- ✅ SQL Injection Protection
- ✅ XSS Protection
- ✅ Input Sanitization
- ✅ Request Fingerprinting
- ✅ Anomaly Detection

### ۳.۴ پایگاه داده و ORM

**پیکربندی:**
- **Development:** SQLite + Aiosqlite
- **Production:** PostgreSQL + Asyncpg (+ PostGIS)
- **Migrations:** Alembic

**چالش شناسایی‌شده:**
- ⚠️ نیاز به تکمیل Alembic migrations برای production
- ⚠️ فعلیاً از `create_all()` استفاده می‌شود (برای production مناسب نیست)

---

## ۴. تحلیل فنی فرانت‌اند

### ۴.۱ ساختار `apps/web/`

```
apps/web/src/
├── app/                  # مسیرهای برنامه
├── components/           # کامپوننت‌های React (۱۲ پوشه)
├── pages/                # صفحات (۳۹ صفحه)
├── api/                  # کلاینت‌های API
├── services/             # سرویس‌ها (Supabase، etc.)
├── hooks/                # Custom hooks
├── i18n/                 # بین‌المللی‌سازی (fa/en)
├── simulators/           # شبیه‌سازهای کلاینت
└── lib/                  # توابع کمکی
```

### ۴.۲ صفحات پیاده‌سازی‌شده

| دسته | صفحات | وضعیت |
|------|-------|--------|
| اصلی | Dashboard، Home | ✅ کامل |
| ماژول‌ها | Weather، Accounting، Calendar | ✅ متصل به API |
| ماژول‌ها | GIS، Education، Psychology | 🟡 Stub/Mock |
| ماژول‌ها | EcoMining، Store، Library | 🟡 Stub/Mock |
| ماژول‌ها | Desktop، Community، Games | 🟡 Stub/Mock |
| احراز هویت | Login، Register | ✅ JWT Ready |
| کشاورزان | Farmers CRUD | ✅ کامل |

### ۴.۳ ویژگی‌های کلیدی فرانت‌اند

- ✅ **i18n کامل:** پشتیبانی همزمان فارسی و انگلیسی با `next-intl`
- ✅ **React Query:** Cache و invalidation خودکار
- ✅ **Zustand:** State management سبک
- ✅ **Axios:** کلاینت HTTP با interceptorها
- ✅ **Supabase Integration:** Auth و session handling
- ✅ **Leaflet GIS:** نقشه تعاملی با لایه‌ها
- ✅ **Chatbot شناور:** AI chat در همه صفحات

### ۴.۴ کامپوننت‌های مشترک (`packages/`)

| بسته | مسئولیت |
|------|---------|
| `@econojin/ui` | کامپوننت‌های UI مشترک |
| `@econojin/types` | تعاریف TypeScript |
| `@econojin/api-client` | کلاینت API typed |
| `@econojin/hooks` | Custom React hooks |
| `@econojin/features` | Feature modules |

---

## ۵. زیرساخت و DevOps

### ۵.۱ Docker و Containerization

**فایل‌های Docker Compose:**
| فایل | کاربرد |
|------|--------|
| `docker-compose.yml` | Production stack |
| `docker-compose.apps.yml` | Development (apps فقط) |
| `docker-compose.db.yml` | Database services |
| `docker-compose.prod.yml` | Production configuration |

**Dockerfileها:**
- `Dockerfile` - Root Dockerfile
- `docker/Dockerfile.api` - API container
- `apps/web/Dockerfile` - Frontend container
- `apps/cms/Dockerfile` - CMS container

### ۵.۲ Kubernetes

```
infrastructure/kubernetes/
├── deployments/          # Deployment manifests
├── services/             # Service definitions
├── configmaps/           # Configuration
├── secrets/              # Secrets templates
└── ingress/              # Ingress rules
```

### ۵.۳ CI/CD Pipeline

**Workflowهای GitHub Actions:**
| Workflow | Trigger | وظیفه |
|----------|---------|-------|
| `ci.yml` | Push/PR | تست‌های اصلی |
| `deploy.yml` | Main branch | Build & Deploy |
| `quality-gates.yml` | PR | بررسی کیفیت کد |
| `security-scan.yml` | Scheduled | اسکن امنیتی |
| `scheduled-tasks.yml` | Cron | تسک‌های زمان‌بندی‌شده |

**مراحل CI:**
1. **api-tests:** اجرای pytest با coverage >= 70%
2. **web-typecheck:** بررسی نوع TypeScript
3. **playwright:** تست E2E
4. **build:** ساخت Docker image
5. **deploy:** انتشار به registry

### ۵.۴ Monitoring Stack

```
monitoring/
├── prometheus/           # Metrics collection
├── grafana/              # Visualization
├── alertmanager/         # Alert routing
└── prometheus.yml        # Configuration
```

**متریک‌های کلیدی:**
- Request rate و latency
- Error rates
- Database connections
- Cache hit/miss
- Queue lengths (Celery)

---

## ۶. امنیت

### ۶.۱ لایه‌های امنیتی

| لایه | مکانیزم | پیاده‌سازی |
|------|---------|-----------|
| Network | CORS، Origin Validation | ✅ Middleware |
| Transport | HTTPS (production) | ⏳ نیاز به پیکربندی |
| Application | Security Headers | ✅ Spider Security |
| Authentication | JWT + OTP | ✅ کامل |
| Authorization | Role-based access | 🟡 در حال توسعه |
| Data | Input Sanitization | ✅ Protection module |
| Monitoring | Anomaly Detection | ✅ Fingerprinting |

### ۶.۲ احراز هویت

**روش‌های پشتیبانی‌شده:**
1. **JWT Token:** استاندارد با python-jose
2. **OTP:** SMS via Kavenegar/Twilio
3. **Supabase Auth:** اختیاری

**Endpoints احراز هویت:**
```
POST /api/v1/auth/otp/request
POST /api/v1/auth/otp/verify
POST /api/v1/users/login
POST /api/v1/users/register
```

### ۶.۳ چالش‌های امنیتی شناسایی‌شده

| ریسک | سطح | راهکار پیشنهادی |
|------|-----|-----------------|
| Wildcard CORS | متوسط | حذف `*` از ALLOWED_ORIGINS |
| Missing Rate Limits | پایین | تنظیم دقیق‌تر thresholds |
| Secret Management | متوسط | استفاده از Vault/Secrets Manager |
| SQL Injection | پایین | استفاده از ORM + Parameterized queries |
| XSS | پایین | Input sanitization + CSP headers |

---

## ۷. ماژول‌های علمی و شبیه‌سازی

### ۷.۱ مدل‌های پیاده‌سازی‌شده

#### الف) چرخه کربن (`carbon_cycle/`)
- **مدل RothC-full:** شبیه‌سازی کربن آلی خاک
- **ورودی‌ها:** اقلیم، مدیریت خاک، پوشش گیاهی
- **خروجی‌ها:** SOC stock، CO2 flux

#### ب) هیدرولوژی (`hydrology/`)
- **مدل AquaCrop:** عملکرد محصول بر اساس آب
- **مدل SWAT+:** هیدرولوژی حوضه آبریز
- **Coupling Engine:** ادغام مدل‌های چندگانه

#### ج) کشاورزی (`agriculture/`)
- مدیریت مزرعه
- برنامه‌ریزی کشت
- پیش‌بینی عملکرد

### ۷.۲ وضعیت یکپارچگی علمی

| مؤلفه | وضعیت | محل |
|-------|-------|-----|
| RothC | ✅ کامل | `apps/simulation/carbon_cycle/` |
| AquaCrop | 🟡 Stub | نیاز به اتصال FAO package |
| SWAT+ | 🟡 در scripts | نیاز به مهاجرت به API |
| ERA5-Land | 🟡 Partial | نیاز به fetcher کامل |
| Sentinel-2 | 🟡 Partial | نیاز به sentinelhub integration |
| CHIRPS | 🔴 Not started | - |

### ۷.۳ چالش‌های علمی

1. **جداسازی کد علمی:** مدل‌ها در `scripts/` باید به `apps/simulation/` مهاجرت کنند
2. **پردازش ناهمزمان:** نیاز به Celery workers برای jobهای سنگین
3. **ذخیره‌سازی نتایج:** نیاز به schemaهای تخصصی برای lineage داده
4. **PostGIS:** نیاز به فعال‌سازی برای تحلیل‌های مکانی

---

## ۸. توسعه منطقه‌ای

### ۸.۱ کشورهای هدف

| کشور | اولویت | بودجه | مدت | مناطق هدف |
|------|--------|-------|-----|-----------|
| افغانستان | HIGH | $5M | 36 ماه | بامیان، دایکندی، غور |
| عراق | HIGH | $8M | 36 ماه | الانبار، صلاح‌الدین، نینوا |
| اردن | MEDIUM | $6M | 36 ماه | معان، الکَرک، الطفیله |

**بودجه کل:** $19,000,000

### ۸.۲ نتایج مورد انتظار

| شاخص | هدف |
|------|-----|
| پایلوت‌های منطقه‌ای | ۹ پایلوت |
| زمین تحت مدیریت | ۳۰,۰۰۰ هکتار |
| کارشناسان آموزش‌دیده | ۹۰۰ نفر |
| ترسیب کربن | ۱۵,۰۰۰ tCO2e |
| خانوارهای بهره‌مند | ۳,۰۰۰ خانوار |

### ۸.۳ اسناد منطقه‌ای

```
regional_implementation/
├── REGIONAL_SUMMARY.md
├── afghanistan/
│   ├── COUNTRY_PROFILE.md
│   ├── LOCALIZATION_STRATEGY.md
│   └── BILATERAL_FRAMEWORK.md
├── iraq/
│   ├── COUNTRY_PROFILE.md
│   ├── LOCALIZATION_STRATEGY.md
│   └── BILATERAL_FRAMEWORK.md
├── jordan/
│   ├── COUNTRY_PROFILE.md
│   ├── LOCALIZATION_STRATEGY.md
│   └── BILATERAL_FRAMEWORK.md
├── finance/
│   └── REGIONAL_FINANCING_MODEL.md
├── mena_ilm_network/
│   └── NETWORK_CHARTER.md
└── mrv_protocols/
    └── REGIONAL_MRV_PROTOCOLS.md
```

### ۸.۴ چارچوب MRV (Measurement, Reporting, Verification)

سیستم MRV برای ردیابی:
- ترسیب کربن
- بهبود حاصلخیزی خاک
- صرفه‌جویی آب
- افزایش تنوع زیستی

---

## ۹. تحلیل شکاف‌ها و ریسک‌ها

### ۹.۱ شکاف‌های فنی

| حوزه | شکاف | اولویت | تلاش تخمینی |
|------|------|--------|-------------|
| Database Migrations | عدم وجود Alembic کامل | بالا | ۳ روز |
| API Coverage | ۶۰٪ ماژول‌ها stub هستند | بالا | ۲ هفته |
| Frontend Integration | ۴۰٪ صفحات mock هستند | متوسط | ۲ هفته |
| Scientific Models | جدایی از API اصلی | بالا | ۳ هفته |
| Testing | Coverage < 70% | متوسط | ۱ هفته |
| Documentation | مستندات ناقص | پایین | ۱ هفته |

### ۹.۲ ریسک‌های پروژه

| ریسک | احتمال | تأثیر | راهکار کاهش |
|------|--------|-------|-------------|
| تأخیر در یکپارچگی علمی | متوسط | بالا | تخصیص تیم متخصص |
| مشکلات مقیاس‌پذیری | پایین | متوسط | Load testing زودهنگام |
| وابستگی به APIهای خارجی | متوسط | متوسط | Implement fallbacks |
| چالش‌های استقرار منطقه‌ای | بالا | بالا | مشارکت ذینفعان محلی |
| محدودیت بودجه | متوسط | بالا | فازبندی هوشمند |

### ۹.۳ بدهی فنی

1. **Legacy Code:** فایل‌های `scripts/main.py` و `backend/` باید حذف یا مهاجرت کنند
2. **Hardcoded Values:** برخی مقادیر environment باید externalize شوند
3. **Error Handling:** نیاز به استانداردسازی response schemas
4. **Type Safety:** برخی بخش‌های TypeScript نیاز به typing دقیق‌تر دارند

---

## ۱۰. نتایج و پیشنهادات

### ۱۰.۱ نقاط قوت

✅ **معماری ماژولار:** ساختار monorepo با separation of concerns واضح  
✅ **امنیت چندلایه:** سیستم Spider Security اختصاصی  
✅ **پشتیبانی چندزبانه:** i18n کامل فارسی/انگلیسی  
✅ **مستندات غنی:** ۹۶ فایل Markdown  
✅ **زیرساخت آماده:** Docker، K8s، CI/CD  
✅ **تعهد منطقه‌ای:** برنامه‌ریزی برای ۳ کشور با بودجه $19M  

### ۱۰.۲ نقاط ضعف

⚠️ **یکپارچگی ناقص:** ماژول‌های علمی جدا از API اصلی  
⚠️ **تست ناکافی:** Coverage زیر ۷۰٪  
⚠️ **Database Migrations:** عدم وجود Alembic کامل برای production  
⚠️ **Frontend Mock:** بسیاری از صفحات هنوز به API متصل نیستند  

### ۱۰.۳ پیشنهادات اولویت‌بندی‌شده

#### کوتاه‌مدت (۲ هفته)
1. **تکمیل Alembic Migrations:** برای پشتیبانی PostgreSQL production
2. **استانداردسازی API:** Response schemas یکنواخت
3. **اتصال Frontend:** حداقل ۵ ماژول پرکاربرد به API
4. **بهبود تست:** رسیدن به ۷۰٪ coverage

#### میان‌مدت (۴ هفته)
1. **مهاجرت مدل‌های علمی:** انتقال از `scripts/` به `apps/simulation/`
2. **Celery Integration:** برای پردازش ناهمزمان
3. **PostGIS Activation:** برای تحلیل‌های مکانی
4. **Staging Deployment:** استقرار محیط آزمایشی

#### بلندمدت (۸+ هفته)
1. **Production Deployment:** استقرار کامل با monitoring
2. **Regional Pilots:** شروع پایلوت‌های منطقه‌ای
3. **Blockchain Integration:** قرارداد ECO.sol و oracle
4. **PWA Implementation:** حالت آفلاین

### ۱۰.۴ نتیجه‌گیری نهایی

پروژه Econojin یک پلتفرم بلندپروازانه با معماری فنی قوی است که پتانسیل بالایی برای تأثیرگذاری در حوزه کشاورزی پایدار منطقه خاورمیانه دارد. با وجود پیشرفت قابل توجه (~۵۰٪ کلی)، چالش‌های کلیدی در یکپارچگی مدل‌های علمی و تکمیل تست‌ها وجود دارد.

**توصیه استراتژیک:** تمرکز بر تکمیل فاز ۱ (یکپارچگی و زیرساخت) قبل از گسترش قابلیت‌های جدید، موفقیت پروژه را تضمین خواهد کرد.

---

## پیوست‌ها

### الف) منابع کلیدی
- README اصلی: `/workspace/README.md`
- مستندات معماری: `/workspace/docs/ARCHITECTURE.md`
- نقشه راه: `/workspace/docs/ROADMAP_FA.md`
- تحلیل شکاف: `/workspace/docs/GAP_ANALYSIS.md`
- TODO پروژه: `/workspace/TODO.md`

### ب) دستورات مفید

```bash
# اجرای تست‌ها
pytest apps/ -v --cov=apps

# بررسی نوع TypeScript
pnpm --filter @econojin/web type-check

# اجرای لوکال با Docker
docker compose -f docker-compose.apps.yml up --build

# Build کامل
pnpm build
```

### ج) تماس و مشارکت
- مخزن: Git repository
- مستندات: `/workspace/docs/`
- راهنمای مشارکت: `/workspace/docs/CONTRIBUTING.md`

---

**تهیه‌شده توسط:** دستیار هوشمند تحلیل کد  
**بر اساس بررسی:** ۵۶۶ فایل کد (Python + TypeScript) و ۹۶ سند مستندات
