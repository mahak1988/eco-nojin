# Econojin (اکو نوژین)

**Integrated platform for smart agriculture, water, environment, green economy, and rural community.**

پلتفرم یکپارچه کشاورزی هوشمند، آب، محیط‌زیست، اقتصاد سبز و جامعه روستایی.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](License)
[![Status](https://img.shields.io/badge/status-active-success.svg)](.)
[![Phase](https://img.shields.io/badge/phase-0--2-blue.svg)](docs/PHASE_1_2_SSOT.md)

---

## 📋 فهرست مطالب / Table of Contents

- [معرفی پروژه](#-معرفی-پروژه)
- [ویژگی‌های کلیدی](#-ویژگی‌های-کلیدی)
- [معماری سیستم](#-معماری-سیستم)
- [ساختار ماژول‌ها](#-ساختار-ماژول‌ها)
- [وضعیت فعلی](#-وضعیت-فعلی)
- [نصب و راه‌اندازی سریع](#-نصب-و-راه‌اندازی-سریع)
- [مستندات API](#-مستندات-api)
- [توسعه و مشارکت](#-توسعه-و-مشارکت)
- [امنیت](#-امنیت)
- [مجوز](#-مجوز)
- [تماس](#-تماس)

---

## 🌱 معرفی پروژه

**Econojin** یک پلتفرم جامع و یکپارچه برای مدیریت هوشمند کشاورزی، منابع آب، محیط‌زیست، اقتصاد سبز و توسعه جوامع روستایی است. این پلتفرم با بهره‌گیری از مدل‌های علمی پیشرفته، هوش مصنوعی و داده‌های ماهواره‌ای، به کشاورزان، پژوهشگران و سیاست‌گذاران کمک می‌کند تا تصمیمات بهینه‌تری در زمینه‌های مختلف کشاورزی و زیست‌محیطی اتخاذ کنند.

### اهداف اصلی

- 🌾 **کشاورزی هوشمند**: ارائه مدل‌های شبیه‌سازی رشد گیاهان (AquaCrop، RothC) و مدیریت بهینه آبیاری
- 💧 **مدیریت آب**: پایش مصرف آب، پیش‌بینی نیازهای آبی و بهینه‌سازی توزیع منابع
- 🌍 **محیط‌زیست**: پایش کربن خاک، ارزیابی اثرات زیست‌محیطی و پشتیبانی از پروژه‌های اعتبار کربن
- 📊 **اقتصاد سبز**: تحلیل هزینه-فایده، پشتیبانی از توکن‌های اکوسیستم (EcoCoin) و شفافیت زنجیره تأمین
- 👥 **جامعه روستایی**: آموزش، اشتراک دانش و تقویت همکاری‌های محلی

### زبان‌های پشتیبانی‌شده

رابط کاربری به دو زبان **فارسی (fa)** و **انگلیسی (en)** در دسترس است. تمام شناسه‌های کد و API به زبان انگلیسی هستند.

---

## ✨ ویژگی‌های کلیدی

- 🤖 **عامل‌های هوشمند (AI Agents)**: سیستم چندعاملی برای تحلیل داده‌ها، پیش‌بینی و توصیه‌های هوشمند
- 🛰️ **ادغام داده‌های ماهواره‌ای**: اتصال به Google Earth Engine برای دریافت داده‌های EO (NDVI، LAI، رطوبت خاک)
- 🧪 **مدل‌های علمی**: پیاده‌سازی مدل‌های FAO AquaCrop، RothC-26.3، SCS-CN و SWAT (مفهومی)
- 📈 **داشبورد تحلیلی**: نمایش بصری داده‌ها، نمودارهای تعاملی و گزارش‌های سفارشی
- 🔐 **امنیت پیشرفته**: ماژول SpiderGuard برای تشخیص و مقابله با ترافیک خودکار/ربات‌ها
- 🌐 **مقیاس‌پذیری جهانی**: پشتیبانی از پیاده‌سازی منطقه‌ای (خاورمیانه، افغانستان، عراق، اردن)
- 📱 **CMS یکپارچه**: مدیریت محتوا، کتابخانه آموزشی و اعلان‌ها
- 🎯 **سیستم هشدار sớm**: پایش شرایط بحرانی و اطلاع‌رسانی به موقع

---

## 🏗️ معماری سیستم

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React/Next.js)               │
│                    apps/web + packages/ui                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway (FastAPI)                  │
│                        apps/main.py                         │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐ │
│  │   Science    │   Farms      │   Crops      │  Water   │ │
│  │   Module     │   Module     │   Module     │  Module  │ │
│  └──────────────┴──────────────┴──────────────┴──────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data & Knowledge Layer                  │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐ │
│  │  PostgreSQL  │   Redis      │  GEE/EO API  │  Agents  │ │
│  │  + PostGIS   │   (Cache)    │  (Satellite) │  Memory  │ │
│  └──────────────┴──────────────┴──────────────┴──────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### لایه‌های اصلی

1. **Frontend**: React/Next.js با پشتیبانی از i18n و طراحی واکنش‌گرا
2. **API Layer**: FastAPI با مستندات Swagger/OpenAPI خودکار
3. **Business Logic**: ماژول‌های تخصصی (کشاورزی، آب، ریسک، ماهواره)
4. **Data Layer**: PostgreSQL + PostGIS برای داده‌های مکانی، Redis برای کش
5. **External Services**: Google Earth Engine، سرویس‌های هواشناسی

---

## 📦 ساختار ماژول‌ها

```
eco-nojin/
├── apps/                      # ماژول‌های اصلی برنامه
│   ├── ai_agents/            # عامل‌های هوشمند و حافظه
│   ├── farms/                # مدیریت مزارع و زمین‌ها
│   ├── crops/                # مدیریت محصولات و چرخه رشد
│   ├── water/                # مدیریت منابع آب و آبیاری
│   ├── risks/                # ارزیابی ریسک و بیمه
│   ├── satellite/            # ادغام داده‌های ماهواره‌ای
│   ├── monitoring/           # پایش و هشدارها
│   ├── dashboard/            # داشبورد تحلیلی
│   ├── cms/                  # مدیریت محتوا
│   ├── library/              # کتابخانه آموزشی
│   ├── notifications/        # سیستم اعلان
│   ├── users/                # مدیریت کاربران و احراز هویت
│   ├── admin_panel/          # پنل مدیریت
│   ├── spider_security/      # ماژول امنیت SpiderGuard
│   ├── ml/                   # مدل‌های یادگیری ماشین
│   ├── simulation/           # شبیه‌سازها
│   └── web/                  # فرانت‌اند React
├── packages/                  # بسته‌های مشترک
│   ├── ui/                   # کامپوننت‌های UI
│   ├── hooks/                # هوک‌های React
│   ├── api-client/           # کلاینت API
│   └── types/                # تعاریف TypeScript
├── docs/                      # مستندات کامل
├── contracts/                 # قراردادهای هوشمند (Solidity)
├── infrastructure/            # زیرساخت Docker/K8s
├── scripts/                   # اسکریپت‌های کمکی
└── tests/                     # تست‌های واحد و یکپارچگی
```

---

## 📊 وضعیت فعلی

**آخرین به‌روزرسانی:** 2026-07-28

| حوزه | وضعیت | توضیحات |
|------|-------|---------|
| Phase 0–2 Core | ✅ تکمیل‌شده | هسته اصلی در مخزن موجود است (SQLite محلی) |
| Phase 3 Science API | ✅ فعال | `/api/v1/science/*` در دسترس |
| مدل‌های فرآیندی | ✅ مفهومی | FAO AquaCrop، RothC-26.3، SCS-CN |
| رابط کاربری Science | ✅ تکمیل‌شده | `/science` در فرانت‌اند |
| Docker / PostGIS | ⚠️ اختیاری | نیاز به نصب Docker دارد |
| اتصال Live GEE | ⚠️ نیازمند تنظیمات | نیاز به حساب سرویس Google Earth Engine |
| باینری‌های FAO/SWAT | ❌ بسته‌نشده | طبق طراحی (نیاز به مجوز) |

برای اطلاعات دقیق‌تر درباره وضعیت پروژه، به [Single Source of Truth](docs/PHASE_1_2_SSOT.md) مراجعه کنید.

---

## 🚀 نصب و راه‌اندازی سریع

### پیش‌نیازها

- Python 3.9+ 
- Node.js 18+ و pnpm
- PostgreSQL 14+ (اختیاری برای توسعه - SQLite پیش‌فرض است)
- Docker (اختیاری برای استقرار)

### راه‌اندازی سریع (Development)

```bash
# کلون کردن مخزن
git clone https://github.com/mahak1988/eco-nojin.git
cd eco-nojin

# نصب وابستگی‌های Python
pip install -r requirements.txt

# اجرای سرور API
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000

# در ترمینال دیگر - نصب و اجرای فرانت‌اند
cd apps/web && pnpm install && pnpm dev
```

### استفاده از Docker (Production)

```bash
# اجرای کامل با Docker Compose
docker-compose up -d

# یا برای توسعه
docker-compose -f docker-compose.dev.yml up --build
```

### دسترسی به سرویس‌ها

| سرویس | URL | توضیحات |
|-------|-----|---------|
| مستندات API | http://localhost:8000/docs | Swagger UI |
| سلامت سیستم | http://localhost:8000/health | بررسی وضعیت |
| وضعیت Science | http://localhost:8000/api/v1/science/status | وضعیت ماژول‌های علمی |
| دیباگ Routerها | http://localhost:8000/api/v1/debug/routers | لیست endpointها |
| وب‌سایت | http://localhost:5173 | فرانت‌اند اصلی |
| رابط Science | http://localhost:5173/science | داشبورد علمی |

---

## 📡 مستندات API

### نمونه درخواست‌ها

#### بررسی وضعیت Science

```bash
curl -H "User-Agent: Mozilla/5.0" \
  http://localhost:8000/api/v1/science/status
```

#### اجرای مدل AquaCrop پیشرفته

```bash
curl -X POST \
  -H "User-Agent: Mozilla/5.0" \
  -H "Content-Type: application/json" \
  -d '{"days":40,"rain_mm_day":0.4,"crop":"wheat"}' \
  http://localhost:8000/api/v1/science/aquacrop-advanced
```

### Endpointهای اصلی

- `GET /api/v1/science/status` - وضعیت کلی ماژول‌های علمی
- `POST /api/v1/science/aquacrop-advanced` - شبیه‌سازی AquaCrop
- `POST /api/v1/science/rothc` - مدل کربن خاک RothC
- `GET /api/v1/farms/` - لیست مزارع
- `GET /api/v1/satellite/ndvi` - داده‌های NDVI

برای مستندات کامل API به [docs/API.md](docs/API.md) و Swagger UI مراجعه کنید.

---

## 🧪 اجرای تست‌ها

```bash
# تست‌های علمی
pytest tests/unit/test_real_science.py tests/contract/test_science_endpoints.py -q

# همه تست‌ها
pytest tests/ -v

# تست با پوشش کد
pytest --cov=apps tests/
```

---

## 🛡️ امنیت

ماژول **SpiderGuard** برای تشخیص و مقابله با ترافیک خودکار/ربات‌ها اضافه شده است:

- **موقعیت**: `apps/spider_security/`
- **ویژگی‌ها**:
  - تشخیص ربات بر اساس User-Agent
  - محدودکننده نرخ درخواست بر اساس IP
  - Middleware سبک برای FastAPI
  - تست‌های واحد

### نحوه استفاده

```python
from fastapi import FastAPI
from apps.spider_security.middleware import SpiderGuardMiddleware

app = FastAPI()
app.add_middleware(SpiderGuardMiddleware,
    max_requests=60, window_seconds=60, block_after=True)
```

### نکات امنیتی

- برای محیط Production از Redis برای Rate Limiting استفاده کنید
- امکان ادغام با WAF و سیستم‌های احراز هویت وجود دارد
- لاگ‌ها را به ELK/Datadog ارسال کنید
- برای اطلاعات بیشتر: [security/SECURITY_POLICY.md](security/SECURITY_POLICY.md)

---

## 🤝 توسعه و مشارکت

ما از مشارکت جامعه متن‌باز استقبال می‌کنیم! برای راهنمای کامل مشارکت به موارد زیر مراجعه کنید:

- **راهنمای مشارکت**: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- **استانداردهای مهندسی**: [docs/ENGINEERING_STANDARDS.md](docs/ENGINEERING_STANDARDS.md)
- **قانون اساسی پروژه**: [docs/CONSTITUTION.md](docs/CONSTITUTION.md)
- **نقشه راه**: [docs/ROADMAP_FA.md](docs/ROADMAP_FA.md)

### گردش کار توسعه

1. Fork کردن مخزن
2. ایجاد شاخه جدید (`git checkout -b feature/amazing-feature`)
3. Commit تغییرات (`git commit -m 'Add amazing feature'`)
4. Push به شاخه (`git push origin feature/amazing-feature`)
5. ایجاد Pull Request

---

## 📄 مجوز

این پروژه تحت مجوز **MIT** منتشر شده است. برای اطلاعات بیشتر به فایل [License](License) مراجعه کنید.

---

## 📞 تماس

- **مخزن GitHub**: [github.com/mahak1988/eco-nojin](https://github.com/mahak1988/eco-nojin)
- **مستندات کامل**: پوشه `docs/`
- **گزارش‌ها**: پوشه `reports/`

---

## 🙏 قدردانی

از تمامcontributors، پژوهشگران و سازمان‌هایی که در توسعه این پلتفرم مشارکت کرده‌اند، سپاسگزاریم.

---

<div align="center">

**ساخته شده با ❤️ برای کشاورزی پایدار و آینده‌ای سبزتر**

[بالا ↑](#-فهرست-مطالب--table-of-contents)

</div>
