# برنامه جامع توسعه، رفع بدهی فنی و تکمیل پروژه Econojin

**تاریخ تهیه:** مرداد ۱۴۰۵
**نسخه:** ۱.۰.۰
**وضعیت:** پیشنهادی

---

## فهرست مطالب

1. [خلاصه وضعیت فعلی](#۱-خلاصه-وضعیت-فعلی)
2. [بدهی فنی شناسایی‌شده](#۲-بدهی-فنی-شناسایی‌شده)
3. [فازهای توسعه](#۳-فازهای-توسعه)
4. [جزئیات فاز ۰ — تثبیت پایه](#۴-جزئیات-فاز-۰)
5. [جزئیات فاز ۱ — تکمیل بک‌اند](#۵-جزئیات-فاز-۱)
6. [جزئیات فاز ۲ — تکمیل فرانت‌اند](#۶-جزئیات-فاز-۲)
7. [جزئیات فاز ۳ — یکپارچگی علمی و داده](#۷-جزئیات-فاز-۳)
8. [جزئیات فاز ۴ — زیرساخت و استقرار نهایی](#۸-جزئیات-فاز-۴)
9. [جزئیات فاز ۵ — بلاکچین و اقتصاد توکن](#۹-جزئیات-فاز-۵)
10. [جزئیات فاز ۶ — منطقه‌ای و MRV](#۱۰-جزئیات-فاز-۶)
11. [زمان‌بندی و وابستگی‌ها](#۱۱-زمان‌بندی-و-وابستگی‌ها)
12. [شاخص‌های موفقیت (KPI)](#۱۲-شاخص‌های-موفقیت)
13. [پیوست‌ها](#۱۳-پیوست‌ها)

---

## ۱. خلاصه وضعیت فعلی

### ۱.۱ پیشرفت کلی

| لایه | درصد | وضعیت |
|------|------|--------|
| **Backend Core** (FastAPI) | ~۷۰٪ | روترها فعال، Auth JWT/OTP آماده، Security چندلایه |
| **مدل‌های علمی** (RothC, AquaCrop, SWAT+) | ~۴۰٪ | RothC کامل، بقیه در حال انتقال از scripts |
| **Frontend** (React/Vite) | ~۴۰٪ | ۳۹+ صفحه، ۱۶ صفحه متصل به API، بقیه Mock |
| **CMS** (Strapi v5) | ~۳۰٪ | اسکلت اولیه |
| **زیرساخت** (Docker, K8s, CI/CD) | ~۵۰٪ | Dockerfiles آماده، CI/CD پیکربندی شده |
| **تست** (pytest, Playwright) | ~۳۰٪ | تست‌های پایه موجود، coverage < 70% |
| **مستندات** | ~۶۰٪ | ۹۶ فایل Markdown، برخی ناقص |

### ۱.۲ اجزای تکمیل‌شده

| ماژول | وضعیت | جزئیات |
|-------|--------|--------|
| Accounting System | ✅ کامل | Model → Schema → Repository → Service → Router |
| Agriculture Schools | ✅ کامل | CRUD کامل + DB |
| Education System | ✅ کامل | Course, Lesson, Enrollment CRUD + stats |
| Library System | ✅ کامل | LibraryResource CRUD + file upload |
| Community System | ✅ کامل | Posts, Comments, Likes |
| Games System | ✅ کامل | Vocabulary + Quiz + Attempts |
| Simulation (RothC) | ✅ کامل | مدل چرخه کربن پیاده‌سازی شده |
| Smart Contracts | ✅ کامل | EcoCoin.sol + VerificationOracle.sol |
| PWA Support | ✅ کامل | manifest.webmanifest + sw.js |
| Alembic Migrations | ✅ تنظیم شده | مدل‌ها ثبت شدند |
| Database Tests | ✅ اضافه شد | تست‌های CRUD |

### ۱.۳ اجزای ناقص

| ماژول | وضعیت | مشکل |
|-------|--------|------|
| AI Agents | ⚠️ ناقص | LLM Factory آماده، عملیات در انتظار |
| Weather Module | 🟡 Partial | API متصل، برخی ویژگی‌ها ناقص |
| GIS Module | 🟡 Stub/Mock | نقشه تعاملی Leaflet، داده واقعی ندارد |
| Satellite Module | 🟡 Partial | Catalog و roles آماده، fetcherها ناقص |
| Hydrological Models | 🟡 Stub | AquaCrop stub، SWAT+ در scripts |
| Frontend Integration | 🟡 Partial | ۴۰٪ صفحات mock هستند |
| Tests Coverage | ⚠️ متوسط | نیاز به افزایش به ۷۰٪+ |

---

## ۲. بدهی فنی شناسایی‌شده

### ۲.۱ بدهی‌های بحرانی (باید بلافاصله رفع شوند)

| # | بدهی فنی | اولویت | فایل‌های مرتبط | راهکار |
|---|---------|--------|---------------|--------|
| T-01 | عدم وجود Alembic migrations کامل برای production | 🔴 بحرانی | `alembic/`, `apps/shared_core/database/` | تکمیل migration scripts |
| T-02 | استفاده از `create_all()` به جای migrations | 🔴 بحرانی | `apps/shared_core/database/session.py` | جایگزینی با Alembic |
| T-03 | Wildcard CORS `*` در برخی پیکربندی‌ها | 🔴 بحرانی | `apps/main.py`, `settings` | محدود کردن origins |
| T-04 | نبود rate limiting برای production | 🔴 بحرانی | `apps/shared_core/middleware/rate_limit.py` | فعال‌سازی و تنظیم thresholds |
| T-05 | مدیریت secrets به صورت hardcoded | 🔴 بحرانی | `.env`, `settings` | استفاده از Vault/Secrets Manager |

### ۲.۲ بدهی‌های بالا

| # | بدهی فنی | اولویت | فایل‌های مرتبط | راهکار |
|---|---------|--------|---------------|--------|
| T-06 | مدل‌های علمی جدا از API اصلی | 🟠 بالا | `scripts/`, `apps/simulation/` | مهاجرت به ماژول simulation |
| T-07 | ۴۰٪ صفحات frontend به API متصل نیستند | 🟠 بالا | `apps/web/src/pages/` | اتصال به API واقعی |
| T-08 | Response schemas غیراستاندارد | 🟠 بالا | `apps/*/routers.py` | یکسان‌سازی error handling |
| T-09 | Coverage تست زیر ۷۰٪ | 🟠 بالا | `tests/`, `apps/*/tests/` | افزودن تست‌های جامع |
| T-10 | Legacy code در `scripts/` و `backend/` | 🟠 بالا | `scripts/main.py`, `backend/` | پاکسازی یا مهاجرت |

### ۲.۳ بدهی‌های متوسط

| # | بدهی فنی | اولویت | فایل‌های مرتبط | راهکار |
|---|---------|--------|---------------|--------|
| T-11 | مقادیر hardcoded در کد | 🟡 متوسط | متفرقه | انتقال به environment variables |
| T-12 | Type safety ناقص در TypeScript | 🟡 متوسط | `apps/web/src/` | افزودن types دقیق‌تر |
| T-13 | مستندات API ناقص | 🟡 متوسط | `docs/API.md` | تکمیل با exampleها |
| T-14 | نبود centralized logging dashboard | 🟡 متوسط | `monitoring/` | راه‌اندازی Grafana dashboards |
| T-15 | Cache strategy پیاده‌سازی نشده | 🟡 متوسط | `apps/shared_core/` | افزودن Redis caching |

### ۲.۴ بدهی‌های پایین

| # | بدهی فنی | اولویت | فایل‌های مرتبط | راهکار |
|---|---------|--------|---------------|--------|
| T-16 | نبود CI/CD برای frontend | 🟢 پایین | `.github/workflows/` | افزودن workflow frontend |
| T-17 | نبود container health checks | 🟢 پایین | `docker-compose*.yml` | افزودن healthcheck |
| T-18 | Dependency های unused | 🟢 پایین | `requirements.txt`, `package.json` | پاکسازی |
| T-19 | نبود codeowners | 🟢 پایین | `CODEOWNERS` | ایجاد فایل |
| T-20 | ESLint/Prettier ناقص | 🟢 پایین | `.eslintrc`, `ruff.toml` | تکمیل پیکربندی |

---

## ۳. فازهای توسعه

### ۳.۱ نمای کلی فازها

| فاز | نام | مدت | وابستگی | نتیجه |
|-----|-----|------|---------|--------|
| **فاز ۰** | تثبیت پایه | ۳ هفته | - | رفع بدهی‌های بحرانی و بالا |
| **فاز ۱** | تکمیل بک‌اند | ۴ هفته | فاز ۰ | همه روترها آماده production |
| **فاز ۲** | تکمیل فرانت‌اند | ۴ هفته | فاز ۱ | همه صفحات به API متصل |
| **فاز ۳** | یکپارچگی علمی | ۴ هفته | فاز ۱ | مدل‌های علمی در API |
| **فاز ۴** | زیرساخت و استقرار | ۳ هفته | فاز ۰-۳ | محیط staging + production |
| **فاز ۵** | بلاکچین و اقتصاد توکن | ۳ هفته | فاز ۱ | EcoCoin + Oracle عملیاتی |
| **فاز ۶** | منطقه‌ای و MRV | ۴ هفته | فاز ۳ | پایلوت‌های منطقه‌ای |

**جمع کل:** ~۲۵ هفته (~۶ ماه)

### ۳.۲ اولویت‌بندی بر اساس تأثیر

```
بالا
 ↑
 |  T-01 T-02 T-03 T-04 T-05    فاز ۰
 |  T-06 T-07 T-08 T-09 T-10    فاز ۱-۲
 |  مدل‌های علمی                  فاز ۳
 |  زیرساخت production            فاز ۴
 |  بلاکچین                       فاز ۵
 |  منطقه‌ای                      فاز ۶
 ↓
پایین
     ←──────────  زمان  ──────────→
```

---

## ۴. جزئیات فاز ۰ — تثبیت پایه (۳ هفته)

### هدف: رفع بدهی‌های فنی بحرانی و بالا

### هفته ۱: رفع بدهی‌های بحرانی (T-01 تا T-05)

#### روز ۱-۲: تکمیل Alembic Migrations

```
مسئول: Backend
فایل‌های هدف: alembic/, apps/shared_core/database/
```

**اقدامات:**
- [ ] بازبینی تمام models ثبت‌شده در `alembic/env.py`
- [ ] ایجاد migration اولیه برای تمام مدل‌ها
- [ ] تست migration در SQLite و PostgreSQL
- [ ] افزودن script خودکار `alembic upgrade head` در startup
- [ ] جایگزینی `create_all()` با `alembic upgrade`

**تست:**
- اجرای `alembic upgrade head` در محیط local
- اجرای migration در PostgreSQL container
- تأیید جدول‌های ایجاد شده

#### روز ۳: امنیت CORS و Rate Limiting

```
فایل‌های هدف: apps/main.py, apps/shared_core/middleware/rate_limit.py, settings
```

**اقدامات:**
- [ ] حذف `*` از ALLOWED_ORIGINS
- [ ] افزودن لیست سفید origins از environment
- [ ] فعال‌سازی RateLimitMiddleware برای production
- [ ] تنظیم rate limits: 100 req/min برای عمومی، 1000 req/min برای API
- [ ] افزودن Redis backend برای rate limiting

**تست:**
- تست CORS با origin غیرمجاز (باید 403 دریافت کند)
- تست rate limiting با 101 درخواست در یک دقیقه

#### روز ۴-۵: Secret Management

```
فایل‌های هدف: .env.example, apps/shared_core/config.py, infra/
```

**اقدامات:**
- [ ] ایجاد `.env.example` کامل با توضیحات
- [ ] انتقال secrets به environment variables
- [ ] افزودن پشتیبانی از Docker secrets
- [ ] ایجاد script تولید `SECRET_KEY` خودکار
- [ ] مستندسازی مدیریت secrets در `docs/SECURITY.md`

**تست:**
- تست بارگذاری config بدون فایل .env (فقط environment)
- تست Docker secrets injection

### هفته ۲: رفع بدهی‌های بالا (T-06 تا T-10)

#### روز ۶-۷: مهاجرت مدل‌های علمی (T-06)

```
فایل‌های هدف: scripts/*, apps/simulation/
```

**اقدامات:**
- [ ] آنالیز کامل فایل‌های `scripts/` و شناسایی مدل‌های فعال
- [ ] انتقال RothC (در صورت وجود کپی در scripts) به `apps/simulation/carbon_cycle/`
- [ ] انتقال SWAT+ به `apps/simulation/hydrology/swat_plus/`
- [ ] ایجاد endpoints API برای هر مدل
- [ ] افزودن job queue با Celery برای مدل‌های سنگین
- [ ] پاکسازی فایل‌های قدیمی `scripts/`

**تست:**
- اجرای هر مدل با داده test
- مقایسه خروجی با نسخه قبلی
- تست REST API جدید

#### روز ۸-۹: استانداردسازی API Responses (T-08)

```
فایل‌های هدف: apps/*/routers.py, apps/shared_core/
```

**اقدامات:**
- [ ] ایجاد base response schema در `apps/shared_core/schemas/`
  
```python
  class APIResponse(BaseModel):
      success: bool
      data: Any | None = None
      error: APIError | None = None
      meta: ResponseMeta | None = None
  
  class APIError(BaseModel):
      code: str
      message: str
      details: list[str] = []
  
  class ResponseMeta(BaseModel):
      page: int = 1
      per_page: int = 20
      total: int = 0
      request_id: str | None = None
  
```
- [ ] ایجاد helper functions برای پاسخ‌های یکسان
- [ ] به‌روزرسانی تمام routerها برای استفاده از standard responses
- [ ] افزودن pagination به همه endpoints لیست

**تست:**
- تست تمام endpoints برای بررسی فرمت پاسخ
- تست pagination با پارامترهای مختلف

#### روز ۱۰: Legacy Code Cleanup (T-10)

```
فایل‌های هدف: scripts/, backend/, src/ (قدیمی)
```

**اقدامات:**
- [ ] شناسایی فایل‌های بدون استفاده
- [ ] انتقال کد مفید به `apps/simulation/` یا `apps/shared_core/`
- [ ] حذف فایل‌های قدیمی با git rm
- [ ] به‌روزرسانی imports در کل پروژه

### هفته ۳: تست و تثبیت

#### روز ۱۱-۱۳: افزایش تست Coverage (T-09)

```
فایل‌های هدف: tests/, apps/*/tests/, pytest.ini
```

**اقدامات:**
- [ ] تعیین coverage هدف: حداقل ۷۰٪ برای backend، ۵۰٪ برای frontend
- [ ] نوشتن تست‌های واحد برای:
  - تمام repositories (CRUD operations)
  - تمام services (business logic)
  - تمام routers (endpoints)
- [ ] نوشتن تست‌های integration برای:
  - Authentication flow (register → login → refresh)
  - Simulation workflows
  - Error scenarios
- [ ] افزودن pytest-cov به CI pipeline
- [ ] ایجاد report coverage خودکار

**تست:**
```bash
pytest apps/ -v --cov=apps --cov-report=html --cov-fail-under=70
```

#### روز ۱۴-۱۵: تکمیل TypeScript Types (T-12)

```
فایل‌های هدف: apps/web/src/, packages/types/
```

**اقدامات:**
- [ ] بازبینی و تکمیل types در `packages/types/src/`
- [ ] افزودن types برای:
  - همه API responses
  - همه component props
  - State management
- [ ] حذف هرگونه `any`
- [ ] تنظیم strict mode در tsconfig

---

## ۵. جزئیات فاز ۱ — تکمیل بک‌اند (۴ هفته)

### هدف: تکمیل تمام ماژول‌های بک‌اند برای production

### هفته ۴: تکمیل AI Agents

```
فایل‌های هدف: apps/ai_agents/
```

#### اقدامات:
- [ ] تکمیل LLM Factory با همه providers
  - [ ] OpenAI integration
  - [ ] Groq integration
  - [ ] Gemini integration
  - [ ] Ollama (local) integration
- [ ] پیاده‌سازی RAG pipeline کامل
- [ ] افزودن context management با Redis
- [ ] ایجاد endpoints:
  - `POST /api/v1/ai-agents/chat` - Streaming chat
  - `POST /api/v1/ai-agents/query` - Single query
  - `GET /api/v1/ai-agents/history` - Chat history
  - `POST /api/v1/ai-agents/rag/search` - RAG search
- [ ] تست با mock LLM provider

### هفته ۵: تکمیل Simulation Module

```
فایل‌های هدف: apps/simulation/
```

#### اقدامات:
- [ ] تکمیل AquaCrop integration
  - [ ] اتصال به FAO AquaCrop package
  - [ ] پیاده‌سازی محاسبات water-yield
  - [ ] ایجاد REST endpoints
- [ ] تکمیل SWAT+ integration
  - [ ] انتقال از scripts به API
  - [ ] پیاده‌سازی basin-scale modeling
  - [ ] افزودن nutrient modeling
- [ ] تکمیل Coupling Engine
  - [ ] ادغام RothC + AquaCrop + SWAT+
  - [ ] ایجاد pipeline processing
- [ ] افزودن job management:
  - `POST /api/v1/simulation/jobs` - Create job
  - `GET /api/v1/simulation/jobs/{id}` - Job status
  - `GET /api/v1/simulation/jobs/{id}/results` - Get results
  - `DELETE /api/v1/simulation/jobs/{id}` - Cancel job

### هفته ۶: تکمیل Satellite و Weather

```
فایل‌های هدف: apps/satellite/, apps/weather/
```

#### اقدامات:
- [ ] تکمیل Sentinel-2 fetcher
  - [ ] ادغام با sentinelhub py
  - [ ] NDVI/NDWI/SMI indices
  - [ ] کش نتایج در Redis/PostGIS
- [ ] تکمیل ERA5-Land fetcher
  - [ ] Climate variables: temp, precip, radiation
  - [ ] تاریخ‌های تاریخی و پیش‌بینی
- [ ] تکمیل CHIRPS fetcher
  - [ ] داده‌های بارش روزانه
- [ ] تکمیل Weather alerts:
  - [ ] Drought index
  - [ ] Flood risk
  - [ ] Frost warning
- [ ] افزودن PostGIS spatial queries

### هفته ۷: تکمیل ماژول‌های باقی‌مانده

```
فایل‌های هدف: apps/crops/, apps/farms/, apps/water/, apps/planting/, apps/inventory/
```

#### اقدامات:
- [ ] تکمیل Crop Management:
  - Crop rotation planner
  - Yield prediction
  - Disease detection rules
- [ ] تکمیل Water Management:
  - Irrigation scheduling
  - Water balance
  - Quality monitoring
- [ ] تکمیل Planting:
  - Season planner
  - Seed selection
  - Growth tracking
- [ ] تکمیل Inventory:
  - Resource tracking
  - Usage analytics
  - Reorder alerts

---

## ۶. جزئیات فاز ۲ — تکمیل فرانت‌اند (۴ هفته)

### هدف: اتصال همه صفحات به API واقعی

### هفته ۸: اتصال ماژول‌های اصلی

```
فایل‌های هدف: apps/web/src/pages/
```

#### اقدامات:
- [ ] Dashboard اصلی با داده زنده:
  - Stats از `/api/v1/dashboard/stats`
  - Weather widget
  - Recent activities
  - Alerts
- [ ] GIS Map با داده واقعی:
  - Satellite imagery
  - Farm boundaries
  - Soil moisture overlay
- [ ] Education Module:
  - Course listings
  - Lesson viewer
  - Progress tracking

### هفته ۹: اتصال ماژول‌های ثانویه

```
فایل‌های هدف: apps/web/src/pages/
```

#### اقدامات:
- [ ] Psychology Module:
  - Test interface
  - Session booking
  - Results dashboard
- [ ] EcoMining Module:
  - Mining simulator
  - Token balance
  - Transaction history
- [ ] Store Module:
  - Product catalog
  - Shopping cart
  - Order management
- [ ] Desktop Module:
  - Widget system
  - Shortcut management
  - Theme customization

### هفته ۱۰: Admin Panel

```
فایل‌های هدف: apps/admin_panel/
```

#### اقدامات:
- [ ] User management:
  - CRUD users
  - Role assignment
  - Activity log
- [ ] Module management:
  - Enable/disable modules
  - Configuration
- [ ] System health:
  - API status
  - Database health
  - Cache stats
  - Queue monitoring (Celery)
- [ ] Reports:
  - Usage statistics
  - Error logs
  - Performance metrics

### هفته ۱۱: بهبود UX و PWA

```
فایل‌های هدف: apps/web/src/
```

#### اقدامات:
- [ ] State management با Zustand:
  - User store
  - Settings store
  - Cache store
- [ ] بهبود React Query:
  - Cache invalidation strategies
  - Optimistic updates
  - Error boundaries
- [ ] PWA improvements:
  - Offline mode
  - Background sync
  - Push notifications
- [ ] Performance:
  - Code splitting
  - Lazy loading
  - Image optimization

---

## ۷. جزئیات فاز ۳ — یکپارچگی علمی و داده (۴ هفته)

### هدف: اتصال تمام مدل‌های علمی به API

### هفته ۱۲-۱۳: مدل‌های هواشناسی و اقلیم

```
فایل‌های هدف: apps/simulation/, data/
```

#### اقدامات:
- [ ] تکمیل ERA5-Land fetcher:
  - Historical data download
  - Climate variables extraction
  - Data validation
- [ ] تکمیل Sentinel-2 integration:
  - NDVI computation
  - Soil moisture estimation
  - Crop health monitoring
- [ ] تکمیل CHIRPS fetcher:
  - Daily precipitation
  - Drought indices
  - Seasonal forecasting

### هفته ۱۴-۱۵: مدل‌های هیدرولوژی و خاک

```
فایل‌های هدف: apps/simulation/hydrology/, apps/simulation/soil/
```

#### اقدامات:
- [ ] تکمیل SWAT+:
  - Basin-scale modeling
  - Nutrient transport
  - Sediment yield
- [ ] تکمیل Coupling Engine:
  - Multi-model integration
  - Scenario analysis
  - Optimization
- [ ] PostGIS activation:
  - Spatial indexes
  - Geometry columns
  - Geospatial queries
- [ ] Data pipeline:
  - ETL processes
  - Data validation
  - Result storage

---

## ۸. جزئیات فاز ۴ — زیرساخت و استقرار نهایی (۳ هفته)

### هدف: محیط production کامل

### هفته ۱۶: Docker و Containerization

```
فایل‌های هدف: docker-compose*.yml, Dockerfile*
```

#### اقدامات:
- [ ] تکمیل Docker Compose production:
  
```yaml
  services:
    api:
      build: .
      ports: ["8000:8000"]
      depends_on: [postgres, redis]
      healthcheck: ...
    postgres:
      image: postgis/postgis:15-3.3
      volumes: [pgdata:/var/lib/postgresql/data]
    redis:
      image: redis:7-alpine
    celery:
      build: .
      command: celery -A apps.shared_core.celery_app worker
    nginx:
      image: nginx:alpine
      volumes: [./infra/nginx/:/etc/nginx/]
  
```
- [ ] افزودن health checks
- [ ] Resource limits
- [ ] Network isolation

### هفته ۱۷: Kubernetes

```
فایل‌های هدف: infrastructure/kubernetes/
```

#### اقدامات:
- [ ] تکمیل Deployment manifests
- [ ] Service definitions:
  - ClusterIP for internal
  - LoadBalancer for external
- [ ] ConfigMaps و Secrets
- [ ] Ingress rules:
  - API routing
  - Web routing
  - WebSocket support
- [ ] Horizontal Pod Autoscaler
- [ ] Network Policies

### هفته ۱۸: Monitoring و CI/CD

```
فایل‌های هدف: monitoring/, .github/workflows/
```

#### اقدامات:
- [ ] Prometheus exporters:
  - FastAPI metrics
  - PostgreSQL metrics
  - Redis metrics
  - Celery metrics
- [ ] Grafana dashboards:
  - API performance
  - Database health
  - Queue status
  - Error rates
- [ ] Alert rules:
  - High error rate
  - Slow responses
  - Down services
- [ ] تکمیل CI/CD:
  - Build and test
  - Docker build
  - Deploy to staging
  - Integration tests
  - Deploy to production

---

## ۹. جزئیات فاز ۵ — بلاکچین و اقتصاد توکن (۳ هفته)

### هدف: عملیاتی‌سازی EcoCoin و Verification Oracle

### هفته ۱۹-۲۰: Smart Contracts

```
فایل‌های هدف: contracts/
```

#### اقدامات:
- [ ] تست و deploy EcoCoin.sol:
  - Token distribution
  - Staking mechanism
  - Reward calculation
- [ ] تست و deploy VerificationOracle.sol:
  - Project registration
  - Verification workflow
  - Compliance reporting
- [ ] Hardhat tests:
  
```javascript
  describe("EcoCoin", () => {
    it("should mint tokens", async () => { ... })
    it("should handle staking", async () => { ... })
  })
  
```
- [ ] Deploy به testnet (Sepolia/Mumbai)
- [ ] Create deployment scripts

### هفته ۲۱: Backend Integration

```
فایل‌های هدف: apps/api/routes/ecocoin.py, contracts/
```

#### اقدامات:
- [ ] Web3 provider setup
- [ ] Contract interaction layer
- [ ] REST endpoints:
  - Token balance
  - Staking
  - Rewards
  - Verification
- [ ] Event listeners
- [ ] Gas optimization

---

## ۱۰. جزئیات فاز ۶ — منطقه‌ای و MRV (۴ هفته)

### هدف: آماده‌سازی برای پایلوت‌های منطقه‌ای

### هفته ۲۲-۲۳: Localization

```
فایل‌های هدف: regional_implementation/, apps/web/src/i18n/
```

#### اقدامات:
- [ ] تکمیل i18n برای کشورهای هدف:
  - فارسی (افغانستان)
  - عربی (عراق)
  - عربی (اردن)
- [ ] Culture-specific adaptations:
  - Calendar systems
  - Number formats
  - Legal frameworks
- [ ] Localization strategy implementation:
  - Language detection
  - Content translation
  - Regional settings

### هفته ۲۴-۲۵: MRV System

```
فایل‌های هدف: data/mrv/, apps/simulation/, regional_implementation/mrv_protocols/
```

#### اقدامات:
- [ ] پیاده‌سازی Measurement protocols:
  - Soil carbon sampling
  - Biomass estimation
  - Water quality metrics
- [ ] Reporting system:
  - Automated report generation
  - Data validation
  - Third-party verification
- [ ] Verification workflow:
  - Field data collection
  - Satellite validation
  - Audit trail
- [ ] Integration با regional partners

---

## ۱۱. زمان‌بندی و وابستگی‌ها

### ۱۱.۱ گانت چارت

```
هفته    0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25
فاز 0   █████████████████
فاز 1                    ████████████████████████████████
فاز 2                                         ████████████████████████████████
فاز 3                                                    ████████████████████
فاز 4                                                                  ██████████████
فاز 5                                                                     ██████████████
فاز 6                                                                                    ████████████████████
```

### ۱۱.۲ وابستگی‌های بحرانی

| فاز | وابسته به | دلیل |
|-----|-----------|------|
| فاز ۱ | فاز ۰ | نیاز به پایه پایدار |
| فاز ۲ | فاز ۱ | نیاز به APIهای کامل |
| فاز ۳ | فاز ۱ | نیاز به infrastructure simulation |
| فاز ۴ | فاز ۰-۳ | نیاز به همه اجزا |
| فاز ۵ | فاز ۱ | نیاز به APIهای کاربر |
| فاز ۶ | فاز ۳ | نیاز به مدل‌های علمی کامل |

### ۱۱.۳ تیم پیشنهادی

| نقش | تعداد | فازهای مرتبط |
|-----|-------|-------------|
| Backend Developer | ۲ نفر | فاز ۰, ۱, ۳, ۵ |
| Frontend Developer | ۲ نفر | فاز ۲ |
| DevOps Engineer | ۱ نفر | فاز ۴ |
| Data Scientist | ۱ نفر | فاز ۳ |
| Smart Contract Developer | ۱ نفر | فاز ۵ |
| Project Manager | ۱ نفر | همه فازها |

---

## ۱۲. شاخص‌های موفقیت (KPI)

### ۱۲.۱ شاخص‌های فنی

| KPI | هدف فعلی | هدف نهایی | مهلت |
|-----|---------|-----------|------|
| Test Coverage (Backend) | ~۴۰٪ | ≥ ۸۰٪ | پایان فاز ۰ |
| Test Coverage (Frontend) | ~۲۰٪ | ≥ ۶۰٪ | پایان فاز ۲ |
| API Response Time (p95) | > ۵۰۰ms | < ۲۰۰ms | پایان فاز ۴ |
| Uptime | - | ≥ ۹۹.۹٪ | پایان فاز ۴ |
| Pages Connected to API | ۱۶/۳۹ (۴۱٪) | ۳۹/۳۹ (۱۰۰٪) | پایان فاز ۲ |
| Alembic Migrations | Partial | کامل | پایان فاز ۰ |
| Docker Compose Production | Partial | کامل | پایان فاز ۴ |
| Kubernetes Ready | Partial | کامل | پایان فاز ۴ |

### ۱۲.۲ شاخص‌های کیفی

| شاخص | اندازه‌گیری |
|------|------------|
| Code Quality | Ruff score ≥ ۹.۵/۱۰ |
| TypeScript Strictness | noUnusedLocals, noUnusedParameters |
| Security Score | OWASP Top 10 coverage |
| Documentation Completion | ≥ ۸۰٪ فایل‌های docs کامل |
| Accessibility Score | Lighthouse ≥ ۹۰ |

### ۱۲.۳ شاخص‌های منطقه‌ای

| شاخص | هدف |
|------|-----|
| کشورهای فعال | ۳ (افغانستان، عراق، اردن) |
| پایلوت‌های منطقه‌ای | ۹ پایلوت |
| کاربران فعال | ۳,۰۰۰ خانوار |
| زمین تحت مدیریت | ۳۰,۰۰۰ هکتار |
| ترسیب کربن | ۱۵,۰۰۰ tCO2e |

---

## ۱۳. پیوست‌ها

### ۱۳.۱ دستورات مفید

```bash
# رفع بدهی فنی phase 0
python -m scripts.fix_technical_debt --phase=0

# اجرای تست‌ها
pytest apps/ -v --cov=apps --cov-report=html --cov-fail-under=70

# بررسی نوع TypeScript
pnpm --filter @econojin/web type-check

# linting
ruff check apps/ --fix
ruff format apps/

# Docker
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Migration
alembic upgrade head
alembic revision --autogenerate -m "description"

# Deploy contracts
cd contracts && npx hardhat run scripts/deploy.ts --network sepolia
```

### ۱۳.۲ Checklist روزانه

- [ ] بررسی لاگ‌های Sentry
- [ ] بررسی health endpoint
- [ ] اجرای تست‌های critical
- [ ] بررسی queue length (Celery)
- [ ] بررسی metrics (Grafana)

### ۱۳.۳ Checklist هفتگی

- [ ] بازبینی technical debt backlog
- [ ] بررسی coverage report
- [ ] بررسی performance metrics
- [ ] به‌روزرسانی TODO.md
- [ ] مستندسازی تغییرات

### ۱۳.۴ مستندات مرتبط

- گزارش فنی: `TECHNICAL_ANALYTICAL_REPORT.md`
- برنامه فازی قبلی: `PLAN.md`
- نقشه راه: `docs/ROADMAP_FA.md`
- تحلیل شکاف: `docs/GAP_ANALYSIS.md`
- TODO: `TODO.md`

---

**تهیه‌شده توسط:** تیم فنی Econojin
**وضعیت:** پیشنهادی - منتظر تأیید

**نویسنده:** دستیار هوشمند تحلیل کد
**بر اساس:** بررسی ۵۶۶ فایل کد، ۹۶ سند مستندات، و تحلیل ۲۰ آیتم بدهی فنی
