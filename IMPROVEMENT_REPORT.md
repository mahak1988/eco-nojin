# گزارش جامع تحلیل، یافته‌های جدید و برنامه اجرایی ۱۰ فازی — Econojin

**تاریخ به‌روزرسانی:** ۱۴۰۵/۰۵/۰۷ (2026-07-29)  
**مخزن:** [mahak1988/eco-nojin](https://github.com/mahak1988/eco-nojin)  
**وضعیت پایه:** Phase 0–3 Wave 2 در مخزن؛ Science API فعال؛ JWT hardcoded رفع شده

---

## ۱. خلاصه اجرایی (Executive Summary)

پروژه **Econojin** (اکو نوژین) یک پلتفرم یکپارچه کشاورزی هوشمند، آب، محیط‌زیست، اقتصاد سبز و جامعه روستایی است. معماری ماژولار Model→Schema→Repository→Service→Router، FastAPI async، React/Vite، Alembic، SpiderGuard، rate-limit و audit middleware، Science API (AquaCrop conceptual + RothC-26.3 + SCS-CN)، و قراردادهای Solidity (EcoCoin + VerificationOracle) در مخزن وجود دارند.

### یافته‌های جدید نسبت به گزارش قبلی

| مورد | وضعیت قبلی (گزارش قدیم) | وضعیت فعلی (2026-07-29) | تأثیر |
|------|-------------------------|--------------------------|-------|
| کلید JWT دیکدود در `apps/users/service.py` | **بحرانی** | ✅ **رفع شده** — استفاده از `shared_core.security` + `settings` | امنیت production ممکن شد |
| Rate limiting | غایب / پیشنهادی | ✅ `apps/shared_core/middleware/rate_limit.py` + SpiderGuard | محافظت Brute-force |
| Audit log middleware | پیشنهادی | ✅ `apps/shared_core/middleware/audit_log.py` | ردیابی امنیتی |
| Science API Phase 3 | در حال توسعه | ✅ `/api/v1/science/*` mount شده + تست‌های unit/contract | هسته علمی آماده |
| FE Science UI | ناقص | ✅ صفحه `/science` متصل | نمایش زنده |
| Alembic | ناقص / create_all | ✅ زنجیره تا `20260728_0004` | آمادگی Postgres |
| ماژول‌های Accounting / Education / Library / Community / Games | ناقص | ✅ CRUD کامل + تست | بدهی ماژولی کاهش یافته |
| Docker / PostGIS روی host | مسدود | ⚠️ هنوز نیاز به نصب Docker Desktop توسط کاربر | بلوکه استقرار محلی کامل |
| Live GEE NDVI | مسدود | ⚠️ نیاز به service account | داده ماهواره‌ای واقعی |
| RS256 production | پیشنهادی | ⚠️ کلیدها اختیاری؛ پیش‌فرض HS256 | امنیت بالاتر در prod |
| پوشش تست اندازه‌گیری‌شده | ادعاهای قدیمی | ❌ `pytest --cov` پروژه-wide اجرا نشده | عدد واقعی نامعلوم |
| اتصال کامل FE به API | جزئی | ⚠️ بسیاری صفحات هنوز mock یا نیمه‌متصل | UX ناقص |
| پنل Admin | اسکلت | ⚠️ پیشرفت کم | مدیریت کاربران محدود |
| i18n متمرکز | پراکنده | ⚠️ در حال تحکیم (TODO.md) | چندزبانه ناقص |

**نتیجه:** نقص امنیتی بحرانی JWT رفع شده و هسته علمی + middlewareهای امنیتی اضافه شده‌اند. بدهی فنی باقی‌مانده عمدتاً در استقرار (Docker/PostGIS/GEE)، اتصال کامل فرانت، اندازه‌گیری پوشش تست، RBAC سراسری روی writeها، و polish production است.

---

## ۲. وضعیت صادقانه فعلی (SSOT هم‌راستا با docs/PHASE_1_2_SSOT.md و docs/REMAINING.md)

### انجام‌شده در مخزن
- FastAPI entry `apps/main.py`، CORS محدود، rate-limit و SpiderGuard
- Alembic تا revision اخیر
- RBAC models + `require_permission`
- Auth cookies path؛ JWT HS256 پیش‌فرض، RS256 اختیاری
- Celery + Redis config
- Docker compose: postgres(postgis) + redis + api + worker + beat
- Science: AquaCrop advanced، RothC، SCS-CN، NDVI→canopy، simulation_runs
- ماژول‌های accounting، education، library، community، games با الگوی کامل
- PWA skeleton (manifest + SW)
- Solidity EcoCoin + VerificationOracle

### مسدود / نیازمند اقدام کاربر یا credential
| آیتم | دلیل |
|------|------|
| Docker + PostGIS روی host | Docker Desktop نصب نشده |
| Real GEE NDVI | Google Earth Engine service account |
| RS256 در production | تولید جفت کلید openssl + env |
| measured coverage % | اجرای `pytest --cov` محلی |
| Locust p95 | load test روی API deployشده |
| Official FAO/SWAT binaries | نصب خارجی + مجوز (طراحی عمدی: proxy)

---

## ۳. جدول KPI به‌روز (Gap Analysis)

| حوزه | شاخص | وضعیت فعلی | هدف Best-in-Class | فاصله | اولویت |
|------|-------|------------|-------------------|-------|--------|
| امنیت | JWT secret management | centralized settings | Vault / KMS | کم | متوسط |
| امنیت | Rate limit + anti-bot | in-memory + SpiderGuard | Redis shared + WAF | متوسط | بالا |
| امنیت | RS256 | اختیاری | اجباری در prod | متوسط | بالا |
| داده | PostGIS live | compose آماده | همیشه-on در prod | متوسط | بالا |
| داده | GEE live | synthetic/fallback | service account | بالا | بالا |
| FE | اتصال API واقعی | جزئی (~۴۰–۶۰٪) | ۱۰۰٪ صفحات اصلی | متوسط | بالا |
| تست | coverage اندازه‌گیری‌شده | نامعلوم | ≥۸۰٪ با gate CI | بالا | بالا |
| Observability | Sentry + metrics | پایه | OpenTelemetry + alerts | متوسط | متوسط |
| Admin | پنل مدیریت | اسکلت | CRUD کاربران/نقش‌ها/لاگ | بالا | متوسط |
| i18n | fa/en کامل | در حال تحکیم | next-intl یا dict متمرکز | متوسط | متوسط |
| Deploy | multi-stage + secrets | Dockerfile موجود | multi-stage + non-root + vault | متوسط | بالا |

---

## ۴. برنامه اجرایی ۱۰ فاز برای تکمیل کامل پروژه

هر فاز شامل **هدف**، **تحویل‌پذیرها**، **معیار پذیرش**، **ابزار/کتابخانه**، و **تخمین** است. فازها قابل موازی‌سازی جزئی هستند اما ترتیب پیشنهادی وابستگی‌ها را رعایت می‌کند.

### فاز ۱ — تثبیت امنیت و Hardening نهایی (۳–۵ روز)
**هدف:** حذف هرگونه secret در کد، فعال‌سازی rate-limit/audit در entrypoint، آماده‌سازی RS256.

**تحویل‌پذیرها:**
1. تأیید عدم وجود hardcoded secret (`git grep -n SECRET_KEY apps/` فقط در config/settings).
2. ثبت `RateLimitMiddleware` + `SpiderGuardMiddleware` + `AuditLogMiddleware` در `apps/main.py` با config از env.
3. اسکریپت `scripts/gen_jwt_keys.sh` + مستند KEY_ROTATION به‌روز.
4. `REQUIRE_AUTH_FOR_WRITES=true` به‌عنوان پیش‌فرض در `.env.docker` و production compose.
5. bandit + pip-audit در CI gate.

**معیار پذیرش:** `bandit -r apps/ -ll` بدون critical؛ login با >۵ تلاش → ۴۲۹؛ write بدون token → ۴۰۱.

**ابزار:** slowapi یا middleware موجود، bandit، pip-audit، openssl.

---

### فاز ۲ — دیتابیس و Migrations production-ready (۴–۶ روز)
**هدف:** Alembic کامل، PostGIS فعال، seed داده‌های پایه.

**تحویل‌پذیرها:**
1. همه مدل‌های فعال در `alembic/env.py` و revisionهای متوالی بدون `create_all` در prod.
2. `docker compose up postgres redis` با healthcheck و volume.
3. migration برای `farms.geom` (GIST) و جداول science/simulation_runs.
4. اسکریپت seed (کاربر admin اولیه، نقش‌های RBAC، داده نمونه مزارع).
5. مستند `docs/POSTGRES_MIGRATE.md` و `docs/DB_VERSIONING.md` به‌روز.

**معیار پذیرش:** `alembic upgrade head` روی Postgres خالی موفق؛ PostGIS extension فعال؛ تست CRUD روی Postgres.

**ابزار:** Alembic، asyncpg، geoalchemy2، docker compose.

---

### فاز ۳ — تکمیل و یکپارچه‌سازی API (۵–۸ روز)
**هدف:** همه روترهای موجود از الگوی یکسان پیروی کنند؛ endpointهای تجمیعی؛ OpenAPI تمیز.

**تحویل‌پذیرها:**
1. Audit هر روتر برای استفاده از `shared_core` security/deps.
2. `/api/v1/dashboard/stats` با داده زنده (health + modules + counts).
3. Pagination استاندارد + error schema یکنواخت (trace_id).
4. Swagger tags و نسخه‌گذاری ثابت `/api/v1`.
5. تست‌های contract برای science + auth + accounting + education.

**معیار پذیرش:** `curl /api/v1/debug/routers` بدون 404؛ OpenAPI بدون schema ناقص؛ تست‌های contract سبز.

**ابزار:** pytest، httpx، pydantic v2.

---

### فاز ۴ — اتصال کامل فرانت‌اند به API (۷–۱۰ روز)
**هدف:** حذف mockهای استاتیک از صفحات اصلی؛ React Query؛ login JWT.

**تحویل‌پذیرها:**
1. اتصال صفحات: dashboard، weather، accounting، calendar، farmers، science، education، library، community، games، settings.
2. `/login` و `/register` با JWT (cookie HttpOnly + interceptor axios).
3. React Query برای cache/invalidation.
4. مدیریت خطای ۴۰۱ → redirect login.
5. TypeScript types از OpenAPI (اختیاری: openapi-typescript).

**معیار پذیرش:** همه صفحات اصلی داده زنده از API می‌گیرند؛ refresh token کار می‌کند؛ بدون console error بحرانی.

**ابزار:** @tanstack/react-query، axios، zustand (در صورت نیاز).

---

### فاز ۵ — داده علمی و EO زنده (۵–۸ روز)
**هدف:** GEE service account + providerهای واقعی؛ Celery jobهای دوره‌ای.

**تحویل‌پذیرها:**
1. پیروی از `docs/GEE_SETUP.md`؛ env `GEE_SERVICE_ACCOUNT_JSON`.
2. endpointهای NDVI واقعی با fallback synthetic.
3. Celery beat: weekly vegetation check + climate ETL.
4. ذخیره simulation_runs و export PDF/CSV.
5. مستند محدودیت‌ها (بدون binary رسمی FAO/SWAT).

**معیار پذیرش:** `science/status` → `gee_live: true` وقتی credential موجود؛ jobهای Celery بدون error در log.

**ابزار:** earthengine-api، Celery، Redis، rasterio (در صورت نیاز).

---

### فاز ۶ — تست، پوشش و Observability (۵–۷ روز)
**هدف:** پوشش اندازه‌گیری‌شده ≥۷۰٪ (هدف ۸۰٪)؛ Sentry + metrics پایه.

**تحویل‌پذیرها:**
1. `pytest --cov=apps --cov-report=xml` در CI؛ gate روی threshold.
2. تست‌های integration با Postgres testcontainer یا sqlite.
3. init Sentry در `apps/main.py` + capture در exception handlers.
4. Prometheus metrics endpoint (اختیاری: prometheus-fastapi-instrumentator).
5. تست‌های E2E پایه Playwright برای login + science page.

**معیار پذیرش:** coverage report در CI؛ Sentry event در صورت exception مصنوعی؛ Playwright سبز.

**ابزار:** pytest-cov، sentry-sdk، playwright، testcontainers (اختیاری).

---

### فاز ۷ — CI/CD و DevOps (۴–۶ روز)
**هدف:** pipeline قابل اعتماد؛ multi-stage image؛ deploy خودکار.

**تحویل‌پذیرها:**
1. GitHub Actions: lint (ruff) → test → security (bandit/pip-audit) → build image.
2. Dockerfile multi-stage (builder + runtime non-root).
3. `docker-compose.prod.yml` با secrets mount.
4. مستند deploy: Vercel (FE) + Render/Liara/Neon (API/DB) یا pure Docker.
5. pre-commit hooks فعال.

**معیار پذیرش:** PR بدون سبز شدن CI merge نمی‌شود؛ image بدون secret؛ healthcheck پس از deploy موفق.

**ابزار:** GitHub Actions، Docker، ruff، pre-commit.

---

### فاز ۸ — پنل Admin و RBAC سراسری (۵–۷ روز)
**هدف:** مدیریت کاربران/نقش‌ها/لاگ؛ enforce permission روی همه writeها.

**تحویل‌پذیرها:**
1. صفحات admin: users، roles، modules، system health، audit logs.
2. `require_permission` روی تمام POST/PUT/DELETE حساس.
3. UI برای تخصیص نقش و مشاهده audit trail.
4. تست‌های RBAC (forbidden vs allowed).

**معیار پذیرش:** کاربر بدون نقش نمی‌تواند write کند؛ admin می‌تواند نقش تغییر دهد؛ audit log قابل مشاهده.

**ابزار:** FastAPI Depends، React admin UI (یا گسترش apps/web).

---

### فاز ۹ — PWA، i18n و polish UX (۴–۶ روز)
**هدف:** نصب‌پذیر، چندزبانه کامل fa/en، دسترسی‌پذیری پایه.

**تحویل‌پذیرها:**
1. تکمیل dict متمرکز i18n (طبق TODO.md) و حذف پراکندگی.
2. Service worker cache استراتژی برای offline science/dashboard.
3. RTL کامل برای fa؛ LTR برای en.
4. Lighthouse پایه (performance/accessibility) و رفع critical.
5. manifest + icons نهایی.

**معیار پذیرش:** `tsc --noEmit` سبز؛ نصب PWA روی Android/Chrome؛ تغییر زبان بدون reload سخت.

**ابزار:** i18next یا dict موجود، workbox (اختیاری)، lighthouse CI.

---

### فاز ۱۰ — استقرار production، بارگذاری و مستندات نهایی (۵–۸ روز)
**هدف:** محیط production پایدار؛ load test؛ SSOT مستندات.

**تحویل‌پذیرها:**
1. Deploy API + DB + Redis + worker روی هدف انتخابی (Render/Liara/VPS).
2. FE روی Vercel با `VITE_API_BASE_URL` production.
3. Locust یا k6 برای p95 latency و throughput.
4. به‌روزرسانی README، REMAINING، PHASE_SSOT، DEPLOYMENT، ARCHITECTURE.
5. Runbook عملیات (restart، backup، key rotation).
6. چک‌لیست نهایی OPS_CHECKLIST + DEPLOY_CHECKLIST تیک‌خورده.

**معیار پذیرش:** health و science/status در production سبز؛ p95 قابل قبول (<۵۰۰ms برای endpointهای سبک)؛ مستندات بدون ادعای اندازه‌گیری‌نشده.

**ابزار:** Locust/k6، platform CLI (vercel/render)، Sentry production DSN.

---

## ۵. اولویت‌بندی فوری (هفته جاری)

1. **فاز ۱** — تأیید نهایی امنیت و فعال‌سازی middlewareها در entrypoint.
2. **فاز ۲** — بالا آوردن Postgres/PostGIS با Docker (در صورت نصب Docker).
3. **فاز ۴ شروع** — اتصال ۳–۴ صفحه پرترافیک (dashboard, science, accounting, login).
4. اجرای `pytest --cov` و ثبت عدد واقعی در REMAINING.
5. آماده‌سازی GEE service account (مستندات موجود).

---

## ۶. دستورات اجرایی سریع (مرجع)

```bash
# امنیت
git grep -n "SECRET_KEY.*=.*[\"']" apps/ || true
bandit -r apps/ -ll --skip B101
pip-audit -r requirements.txt

# تست
pytest tests/unit/test_real_science.py tests/contract/test_science_endpoints.py -q
pytest --cov=apps --cov-report=term-missing -q

# محلی
pip install -r requirements.txt
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
# در ترمینال دیگر:
cd apps/web && pnpm install && pnpm dev

# Docker (پس از نصب Docker Desktop)
docker compose up --build -d
alembic upgrade head
```

---

## ۷. نقشه‌راه زمانی پیشنهادی (تقریبی)

| فاز | مدت | وابستگی |
|-----|------|----------|
| ۱ امنیت | ۳–۵ روز | — |
| ۲ دیتابیس | ۴–۶ روز | ۱ |
| ۳ API | ۵–۸ روز | ۲ |
| ۴ FE | ۷–۱۰ روز | ۳ |
| ۵ Science/EO | ۵–۸ روز | ۲، credential |
| ۶ تست/Obs | ۵–۷ روز | ۳، ۴ |
| ۷ CI/CD | ۴–۶ روز | ۱، ۶ |
| ۸ Admin/RBAC | ۵–۷ روز | ۳ |
| ۹ PWA/i18n | ۴–۶ روز | ۴ |
| ۱۰ Deploy | ۵–۸ روز | همه |

**جمع تخمینی:** ۸–۱۲ هفته کار متمرکز (با موازی‌سازی قابل کاهش به ۶–۹ هفته).

---

## ۸. توصیه‌های نهایی

- هیچ ادعای «درصد تکمیل» بدون اندازه‌گیری (coverage، Lighthouse، Locust) در مستندات باقی نماند.
- تمام secrets فقط از env / secret manager؛ هرگز در image یا repo.
- برای GEE و Docker اقدام کاربر لازم است؛ کد آماده fallback است.
- پس از هر فاز، `docs/REMAINING.md` و `docs/PHASE_*_SSOT.md` را به‌روز کنید.

---

*این گزارش بر اساس اسکن مخزن در 2026-07-29، فایل‌های IMPROVEMENT_REPORT قبلی، PLAN.md، REMAINING.md، PHASE_1_2_SSOT.md، GAP_ANALYSIS.md، ROADMAP_FA.md و وضعیت واقعی کد (شامل رفع JWT و وجود middlewareها) تهیه شده است.*
