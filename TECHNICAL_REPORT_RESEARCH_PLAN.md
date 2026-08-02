# گزارش فنی و برنامه تحقیق و توسعه — Eco Nojin

> **نسخه:** ۲.۰  
> **تاریخ:** ۱۴۰۵-۰۸-۱۱ (۲ اوت ۲۰۲۶)  
> **نویسنده:** تحلیل مبتنی بر شواهد مستقیم مخزن  
> **مخزن:** `https://github.com/mahak1988/eco-nojin.git`  
> **شاخه:** `feature/benchmark-first`  
> **آخرین commit بررسی‌شده:** `8529cfbcfe410200ef5e5c984b8b8471f9975607`  
> **وضعیت دسترسی:** ✅ تأیید شد — `git remote -v` و `git push --dry-run` موفق (دسترسی fetch + push)

---

## ۱. تحلیل مسئله (Problem Analysis)

### ۱.۱ خلاصه

Eco Nojin یک پلتفرم یکپارچه کشاورزی هوشمند، مدیریت آب، محیط‌زیست، اقتصاد سبز و جامعه روستایی است. این پروژه یک monorepo شامل ۱۵+ سرویس back-end (FastAPI)، فرانت‌اند React/Vite، ماژول‌های علمی (AquaCrop، RothC، SCS-CN)، داده‌های ماهواره‌ای (GEE/Sentinel)، اقتصاد توکنی (EcoCoin)، قراردادهای هوشمند Solidity، و زیرساخت Docker است.

### ۱.۲ هدف این سند

ارائه گزارش فنی دقیق مبتنی بر شواهد مستقیم اجراشده در این جلسه، برنامه توسعه فازبندیشده، و برنامه تحقیق بر پلتفرم‌های مشابه — با اصل «هزینه صفر».

---

## ۲. شواهد جمع‌آوری‌شده (مستقیم از مخزن — این جلسه)

### ۲.۱ دسترسی به مخزن

| بررسی | نتیجه | شواهد |
|---|---|---|
| `git remote -v` | ✅ origin = `https://github.com/mahak1988/eco-nojin.git` | خروجی مستقیم git |
| `git push --dry-run origin feature/benchmark-first` | ✅ «Everything up-to-date» — دسترسی push تأیید شد | خروجی مستقیم git |
| `git status --short --branch` | ✅ شاخه `feature/benchmark-first` — کارپوشه تمیز | خروجی مستقیم git |

**نتیجه:** دسترسی کامل (fetch + push) به مخزن تأیید شد. تغییرات و فایل‌های جدید قابل ثبت (commit) و ذخیره (push) در مخزن هستند.

### ۲.۲ فایل‌های تحلیل‌شده در این جلسه

| فایل/منبع | اهمیت و یافته |
|---|---|
| `apps/main.py` (۴۱۵ خط) | نقطه ورود API — الگوی `_include()` با مدیریت مستقل خطای هر ماژول؛ **۵۴ روتر / ۰ خطا** (تأیید اجرایی) |
| `requirements.txt` (۳۴ خط) | FastAPI≥0.115، SQLAlchemy async≥2.0.36، aiosqlite، asyncpg، psycopg[binary]، alembic، pydantic v2، python-jose، argon2، celery[redis]، redis، sentry-sdk |
| `apps/economics/service.py` (۲۵۹ خط) | ماژول اقتصاد سبز: NPV، **IRR با روش Newton-Raphson**، ROI، دوره بازگشت سرمایه، نقطه سربه‌سر |
| `apps/economics/router.py` (۱۳۵ خط) | ۷ endpoint: CRUD تحلیل‌ها، cost-benefit، npv، irr |
| `apps/weather/era5_chirps.py` | **Open-Meteo** (رایگان، بدون API key): forecast، archive ERA5، precipitation — تأیید با جستجو در کد |
| اجرای تست | `pytest apps/api/tests` → **۱۸۹ passed** (Python 3.12.10، pytest 9.1.1) |
| اجرای import | **۵۴ روتر بارگذاری‌شده، ۰ خطا**؛ امنیت Zero Trust فعال؛ ۲۸ شبیه‌ساز بارگذاری (۰ skip) |

### ۲.۳ تغییرات جدید نسبت به نسخه ۱ سند (گزارش قبلی)

| مورد | گزارش ۱.۰ | واقعیت فعلی (۲.۰) |
|---|---|---|
| آخرین commit | `63c6b571` | `8529cfbc` |
| تعداد روترها | ۵۲ | **۵۴** (+ economics) |
| تست‌ها | ۱۰۵ passed، ۱۲ skipped | **۱۸۹ passed** |
| ماژول economics | ❌ وجود نداشت | ✅ کامل (models، schemas، service، router + ۱۲ تست) |
| پیش‌بینی آب‌وهوا | وابسته به سرویس پولی | ✅ **Open-Meteo رایگان** (بدون API key) + ۴۳ تست weather/risk |
| تست‌های stub در `test_api.py` | عمدتاً `pass` | ✅ ۵ تست واقعی |
| pre-commit | — | ✅ افزوده‌شدن `ruff` + `prettier` (کامیت `312a45f`) |

---

## ۳. ریشه‌یابی وضعیت (Root Cause Analysis)

### ۳.۱ نقاط قوت (شواهدمحور)

1. **معماری ماژولار مقاوم:** ۵۴ روتر با الگوی `_include()` — خطای هر ماژول مستقل مدیریت می‌شود و کل برنامه سقوط نمی‌کند.
2. **امنیت چندلایه:** `SecurityMiddleware` + `SpiderGuardMiddleware` + «۷ best practice امنیتی» + Zero Trust + CORS پیکربندی‌شده + rate limiting + audit log (همگی در سلامت `/health` گزارش می‌شوند).
3. **مدیریت خطای سراسری:** exception handler سراسری با ساختار استاندارد خطا + `request_id` برای ردیابی.
4. **اقتصاد تحلیلی واقعی:** ماژول economics با محاسبات NPV/IRR/ROI/payback/break-even — IRR با روش Newton-Raphson با همگرایی کنترل‌شده (tolerance=1e-6).
5. **هزینه صفر داده هواشناسی:** Open-Meteo بدون کلید API برای forecast، ERA5 historical و precipitation.
6. **تست‌های واقعی و سبز:** ۱۸۹ تست در ۲۰ فایل (ecocoin، economics، risks، weather، community، games، education، accounting، simulation و...) — همه passed.
7. **مستندات غنی:** ۱۰۰+ فایل در `docs/`، README کامل دوزبانه، داکیومنت معماری.
8. **استک رایگان:** `docs/FREE_STACK.md` استک کامل صفر-هزینه را تعریف کرده (تأییدشده با Neon/Supabase، Vercel، Render).

### ۳.۲ نقاط ضعف (شواهدمحور)

1. **شبیه‌سازهای skeleton:** APSIM، MODFLOW، HEC-RAS، CO2FIX، ABM، TEEB، ARIES، LEAP، EPIC، QUAL2K، WASP، MaxEnt، iTree — همگی wrapper موجودند ولی پیاده‌سازی واقعی ندارند (لاگ WARNING در import تأیید شد).
2. **پوشش تست ناقص:** pytest.ini فقط `apps/api/tests` را پوشش می‌دهد؛ ماژول‌های satellite، ml، farms، crops، water (خارج از api/tests) تست اختصاصی ندارند.
3. **مدیریت اسرار:** `SECRET_KEY` نمونه در docker-compose قابل مشاهده است — نیاز به GitHub Secrets/Vault برای production.
4. **هشدارهای deprecation:** `datetime.utcnow()` در SQLAlchemy (۳۷ warning) — نیاز به زمان‌آگاه (timezone-aware).
5. **دوگانگی پیکربندی:** `pytest.ini` و `pyproject.toml` هر دو وجود دارند (pytest هشدار «ignoring pytest config in pyproject.toml» می‌دهد).
6. **PostGIS در محیط فعلی در دسترس نیست** — توسعه با SQLite انجام می‌شود (مسیر مستندشده).

---

## ۴. محدودیت‌های محیط فعلی (Constraints)

| محدودیت | وضعیت |
|---|---|
| Docker | ❌ نصب نیست |
| PostgreSQL (psql) | ❌ نصب نیست |
| Python | ✅ 3.12.10 (venv پروژه: `.venv`) |
| pytest | ✅ 9.1.1 |
| Node.js | ✅ v22.16.0 |
| pnpm | ✅ 11.4.0 |
| git + remote + push | ✅ تأیید شد |

**نتیجه:** توسعه لوکال باید از مسیر SQLite (`docs/LOCAL_NO_DOCKER.md`) انجام شود.

---

## ۵. راهکارهای کاندید (Candidate Solutions)

### راهکار A: توسعه لوکال با SQLite
- **مزایا:** بدون Docker/Postgres؛ مستندشده؛ اجرای تست‌ها تأییدشده (۱۸۹ passed)؛ سریع
- **معایب:** بدون PostGIS؛ تفاوت رفتاری جزئی با production
- **مناسب:** فازهای ۰-۲ (وضعیت فعلی)

### راهکار B: نصب Docker Desktop
- **مزایا:** PostGIS کامل؛ تطابق با production
- **معایب:** نیاز به نصب؛ مصرف منابع؛ نیازمندی WSL2
- **مناسب:** فاز استقرار نهایی

### راهکار C: PostgreSQL ابری رایگان (Neon/Supabase)
- **مزایا:** رایگان؛ PostGIS؛ بدون نصب لوکال
- **معایب:** نیاز به اینترنت؛ تأخیر شبکه
- **مناسب:** توسعه پیشرفته و production

### راهکار D: ترکیبی (توصیه‌شده — وضعیت فعلی)
**فاز ۰-۲:** SQLite لوکال (فعال) → **فاز ۳-۴:** Neon/Supabase ابری → **فاز ۵:** استقرار Liara/Docker

---

## ۶. راهکار منتخب (Selected Solution)

**راهکار D — ترکیبی فازبندیشده (در حال اجرا):**

```bash
# توسعه لوکال (فعال — تأییدشده با ۱۸۹ تست سبز)
set DATABASE_URL=sqlite+aiosqlite:///./apps/econojin.db
set ENVIRONMENT=local
set REQUIRE_AUTH_FOR_WRITES=false
.venv\Scripts\python.exe -m uvicorn apps.main:app --reload --port 8000

# اجرای تست‌ها
.venv\Scripts\python.exe -m pytest apps/api/tests -q
```

---

## ۷. برنامه توسعه (Implementation Plan)

### ✅ فاز ۰ — راه‌اندازی و راستی‌آزمایی (کامل شد)

| # | اقدام | وضعیت |
|---|---|---|
| ۰.۱ | تحلیل پیکربندی‌ها و ساختار | ✅ کامل — README، main.py، requirements، pytest.ini |
| ۰.۲ | تحلیل معماری و وابستگی‌ها | ✅ کامل — ۵۴ روتر، ۳۷۷+ route |
| ۰.۳ | اجرای تست‌های baseline | ✅ کامل — **۱۸۹ passed** |
| ۰.۴ | تأیید دسترسی مخزن | ✅ کامل — fetch + push تأیید شد |
| ۰.۵ | Commit و Push تغییرات | ✅ کامل — `8529cfbc` روی `feature/benchmark-first` |

### ✅ فاز ۱ — تکمیل ماژول‌های اقتصاد و تست‌های واقعی (کامل شد)

| اقدام | شواهد |
|---|---|
| ماژول `apps/economics` (models، schemas، service، router) | کامیت `312a45f` — ۱۲ تست economics |
| جایگزینی ۱۲ تست stub با ۲۸ تست واقعی | کامیت `ae099db` |
| تست‌های واقعی education/games/community | ۵+۷+۴ تست — همه سبز |
| اصلاح باگ dead code در service.py | کامیت `ae099db` |

### ✅ فاز ۲ — پیش‌بینی آب‌وهوا با هزینه صفر (کامل شد)

| اقدام | شواهد |
|---|---|
| یکپارچه‌سازی Open-Meteo (forecast/ERA5/precip) | کامیت `8529cfb` — بدون API key، رایگان |
| ۴۳ تست weather + risk | `test_weather.py` (۱۲) + `test_risks.py` (۲۱) + سایر — همه سبز |
| تقویت pre-commit (ruff + prettier) | کامیت `312a45f` و `8529cfb` |

### ⬜ فاز ۳ — ارتقای ماژول‌های تخصصی به سطح رقبا (برنامه تحقیق — بخش ۹)

### ⬜ فاز ۴ — امنیت و بهینه‌سازی

- [ ] اسکن با `bandit` و `pip-audit` (فایل `.bandit` موجود است)
- [ ] انتقال اسرار هاردکد به GitHub Secrets / محیط
- [ ] حذف هشدارهای `utcnow()` (۳۷ warning) → `datetime.now(timezone.utc)`
- [ ] یکسان‌سازی پیکربندی pytest (حذف تداخل `pyproject.toml`/`pytest.ini`)
- [ ] پروفایلینگ performance endpoints کلیدی

### ⬜ فاز ۵ — استقرار و آپلود

- [ ] تست کامل لوکال + push به GitHub
- [ ] راه‌اندازی GitHub Actions (قالب موجود: `ci-admin-panel.yml`)
- [ ] استقرار روی Neon/Supabase + Liara/Render (رایگان)

---

## ۸. تحلیل هزینه صفر (Zero-Cost Analysis — تأییدشده)

| نیازمندی | راهکار رایگان | وضعیت شواهد |
|---|---|---|
| پایگاه داده لوکال | SQLite + aiosqlite | ✅ فعال (`econojin.db` موجود) |
| پایگاه داده ابری | Neon / Supabase | ✅ مستندشده (`docs/FREE_STACK.md`) |
| فرانت‌اند | Vercel | ✅ مستندشده |
| API | Render / Fly.io | ✅ مستندشده |
| پیش‌بینی آب‌وهوا | **Open-Meteo (رایگان، بدون API key)** | ✅ **پیاده‌سازی‌شده** (`apps/weather/era5_chirps.py`) |
| تصاویر ماهواره‌ای | Sentinel-2 (ESA) / Landsat (USGS) | ✅ رایگان؛ GEE نیازمند سرویس‌اکانت |
| CI/CD | GitHub Actions (public رایگان) | ✅ `ci-admin-panel.yml` موجود |
| نظارت | Prometheus + Grafana | ✅ `monitoring/` موجود |
| هوش مصنوعی | llama/mistral + LangChain | ✅ در `requirements.txt` |

---

## ۹. برنامه تحقیق بر پلتفرم‌های مشابه (Research & Parity)

### ۹.۱ جدول پلتفرم‌های مرجع و ماژول متناظر

| ماژول Eco Nojin | پلتفرم مرجع | قابلیت کلیدی | اقدام parity (پیشنهادی) |
|---|---|---|---|
| `satellite` | Google Earth Engine / Sentinel Hub | NDVI، NDWI، LAI، رطوبت خاک | Sentinel-2 رایگان + محاسبه NDVI محلی |
| `ml` | IBM Watson Agriculture / FBN | پیش‌بینی بازده، تشخیص آفات | مدل‌های open-source + داده‌های FAO |
| `economics/ecocoin` | Regen Network / Toucan Protocol | اعتبار کربن، توکنومیک | ✅ ماژول economics پیاده‌سازی شد — کوپل با استاندارد Verra/GS |
| `weather` | Climate FieldView / aWhere | پیش‌بینی محلی | ✅ **Open-Meteo پیاده‌سازی شد** — ادغام با `water` و `risks` |
| `water` | Netafim / CropX | آبیاری هوشمند | مدل FAO AquaCrop (مفهومی موجود) |
| `risks` | Descartes Labs | هشدار زودهنگام | ترکیب داده EO + مدل‌های آماری (آغاز با ۲۱ تست) |
| `simulation` | APSIM / DSSAT | شبیه‌سازی رشد محصول | skeleton موجود — نیاز به جایگزین open-source |

### ۹.۲ روش تحقیق (طبق پرامپت)

1. **اسناد رسمی:** ESA Sentinel، FAO، USGS، Verra، Gold Standard، IPCC.
2. **مخازن open-source:** پیاده‌سازی‌های مرجع روی GitHub.
3. **علم:** مقالات معتبر درباره AquaCrop، RothC، SCS-CN، و روش‌های IRR/NPV.
4. **تفکیک واقعیت/فرض:** هر ادعا باید با منبع رسمی پشتیبانی شود؛ موارد ناتأیید صریحاً «unknown» اعلام شوند.

### ۹.۳ اولویت‌های تحقیق پیشنهادی (فاز ۳)

1. **Parity آب‌وهوا → آب:** اتصال خروجی Open-Meteo به محاسبات نیاز آبیاری (ET₀ با FAO Penman-Monteith — رایگان و مستند FAO).
2. **Parity ماهواره:** پیاده‌سازی محاسبه NDVI محلی از باندهای Sentinel-2 (بدون نیاز به GEE).
3. **Parity اقتصاد:** اتصال ماژول economics به سناریوهای اعتبار کربن (استاندارد Verra VM0042 — سند رایگان).
4. **Parity ریسک:** مدل هشدار زودهنگام ترکیبی (پیش‌بینی Open-Meteo + شاخص‌های EO).

---

## ۱۰. ریسک‌ها و راهکارها

| ریسک | شدت | راهکار |
|---|---|---|
| باینری‌های FAO/SWAT تحت مجوز | زیاد | مستندسازی؛ استفاده از پیاده‌سازی‌های جایگزین open-source |
| PostGIS در محیط فعلی در دسترس نیست | متوسط | توسعه SQLite؛ PostGIS ابری در فاز ۵ |
| شبیه‌سازهای skeleton (۱۳ ماژول) | متوسط | جایگزینی تدریجی با پیاده‌سازی open-source |
| اسرار هاردکد در docker-compose | زیاد | انتقال به GitHub Secrets / Vault |
| هشدارهای deprecation (utcnow) | کم | اصلاح به timezone-aware در فاز ۴ |
| تداخل پیکربندی pytest | کم | یکسان‌سازی فایل‌های پیکربندی |

---

## ۱۱. معیارهای موفقیت نهایی (Acceptance Criteria)

- [x] `pytest` تمام سبز — **۱۸۹ passed** (فعلی)
- [ ] پوشش تست > ۶۰٪ برای ماژول‌های اصلی (افزودن تست به satellite/ml/farms/water)
- [ ] اسکن امنیتی (bandit + pip-audit) بدون یافته critical
- [ ] parity با حداقل ۳ پلتفرم مرجع (مستندشده) — ✓ weather (Open-Meteo)، ✓ economics، ⬜ satellite، ⬜ خطر
- [ ] استقرار موفق لوکال + push به GitHub
- [ ] هزینه کل اجرا: صفر تومان

---

## ۱۲. خلاصه و نتیجه

این گزارش بر اساس شواهد مستقیم اجراشده در این جلسه تهیه شده است:

- ✅ **دسترسی مخزن تأیید شد** (fetch + push)
- ✅ **۱۸۹ تست سبز** (Python 3.12.10)
- ✅ **۵۴ روتر با ۰ خطا** بارگذاری شد
- ✅ ماژول **economics** (NPV/IRR/ROI) پیاده‌سازی و تست‌شده
- ✅ پیش‌بینی آب‌وهوا با **Open-Meteo رایگان** یکپارچه شد
- ⬜ فاز ۳: تحقیق و parity پلتفرم‌های مشابه (اولویت: satellite، water، risks)
- ⬜ فاز ۴: امنیت و بهینه‌سازی
- ⬜ فاز ۵: استقرار رایگان

**وضعیت:** فازهای ۰-۲ کامل‌شده و push شده‌اند. آماده شروع فاز ۳ (تحقیق و parity) طبق برنامه بخش ۹ هستیم.

---

*سند بر اساس شواهد مستقیم مخزن تهیه شده و با پیشرفت فازها به‌روزرسانی خواهد شد.*