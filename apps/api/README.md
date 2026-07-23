# api | ماژول APIهای تخصصی Econojin

> **نکته:** این ماژول **روترها و سرویس‌های API تخصصی** پلتفرم Econojin را شامل می‌شود.
> هر زیرماژول مسئول یک حوزه‌ی خاص مانند حسابداری، EcoCoin، پایش، شبیه‌ساز، آموزش و ... است.

## مسئولیت‌ها

این ماژول شامل ۸ زیرماژول تخصصی است که در `apps/main.py` به صورت داینامیک بارگذاری می‌شوند:

| زیرماژول | مسیر API | توضیح |
|----------|----------|--------|
| **accounting** | `/api/v1/accounting` | حسابداری و امور مالی |
| **ecocoin** | `/api/v1/ecocoin` | ارز دیجیتال بومی و پاداش‌های زیست‌محیطی |
| **monitoring** | `/api/v1/monitoring` | پایش و مانیتورینگ سیستم |
| **simulator** | `/api/v1/simulator` | شبیه‌سازهای اختصاصی |
| **agriculture_schools** | `/api/v1/agriculture-schools` | مدیریت مدارس کشاورزی |
| **alerts** | `/api/v1/alerts` | اعلان‌ها و هشدارها |
| **education** | `/api/v1/education` | محتوای آموزشی و دوره‌ها |
| **community** | `/api/v1/community` | شبکه اجتماعی و انجمن‌ها |
| **library** | `/api/v1/library` | کتابخانه دیجیتال |
| **games** | `/api/v1/games` | بازی‌ها و سرگرمی |

## ساختار

```
api/
├── __init__.py                # Package init
├── router.py                  # ★ روتر عمومی API
├── schemas.py                 # Pydantic schemas عمومی
├── service.py                 # Business logic عمومی
├── repository.py              # Database access عمومی
├── models.py                  # ORM models عمومی
├── dependencies.py            # FastAPI dependencies عمومی
├── routes/                    # ★ زیرماژول‌های تخصصی
│   ├── accounting.py          #   حسابدارى
│   ├── ecocoin.py             #   EcoCoin
│   ├── monitoring.py          #   پایش
│   ├── simulator.py           #   شبیه‌ساز
│   ├── agriculture_schools.py #   مدارس کشاورزی
│   ├── alerts.py              #   اعلان‌ها
│   ├── education.py           #   آموزش
│   ├── community.py           #   جامعه
│   └── games.py               #   بازی‌ها
├── services/                  # ★ سرویس‌های تخصصی
├── repositories/              # ★ Repositoryهای اختصاصی
├── models/                    # ★ مدل‌های اختصاصی
├── schemas/                   # ★ Schemaهای اختصاصی
└── tests/                     # Pytest tests
```

## بارگذاری خودکار در main.py

روترها به صورت داینامیک در `apps/main.py` بارگذاری می‌شوند:

```python
# نمونه کد بارگذاری خودکار از main.py
try:
    from apps.api.routes.accounting import router as accounting_router
    app.include_router(accounting_router, prefix=settings.API_V1_STR)
    logger.info("✅ accounting: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  accounting: {e}")

try:
    from apps.api.routes.ecocoin import router as ecocoin_router
    app.include_router(ecocoin_router)
    logger.info("✅ ecocoin: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  ecocoin: {e}")
```

## زیرماژول‌ها

### 1. حسابداری (Accounting)
مدیریت امور مالی، تراکنش‌ها و گزارش‌های مالی.

### 2. EcoCoin
ارز دیجیتال بومی برای پاداش‌های زیست‌محیطی و فعالیت‌های پایدار.

### 3. پایش (Monitoring)
مانیتورینگ سلامت سیستم، لاگ‌ها و گزارش‌های عملکرد.

### 4. شبیه‌ساز (Simulator)
شبیه‌سازهای اختصاصی برای مدل‌سازی سناریوهای مختلف.

### 5. مدارس کشاورزی (Agriculture Schools)
مدیریت مدارس کشاورزی، دانش‌آموزان و برنامه‌های آموزشی.

### 6. اعلان‌ها (Alerts)
سیستم هشدار و اعلان برای رویدادهای مهم.

### 7. آموزش (Education)
دوره‌های آموزشی، محتوا و پیشرفت یادگیری.

### 8. جامعه (Community)
شبکه اجتماعی، گروه‌ها و تعامل کاربران.

### 9. کتابخانه (Library)
مدیریت منابع دیجیتال، کتاب‌ها و دانلودها.

### 10. بازی‌ها (Games)
بازی‌های تعاملی، امتیازها و چالش‌ها.

## توسعه و تست

```bash
# از ریشه‌ی پروژه
cd d:\econojin.com

# اجرای تست‌ها
pytest apps/api/tests/ -v

# اجرای سرور توسعه
python apps/main.py
# یا
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

## تغییرات مهم

- **فاز ۲:** افزودن ۱۰ زیرماژول تخصصی با بارگذاری داینامیک
- **فاز ۲:** معماری routes/services/repositories/models/schemas مجزا
- **فاز ۲:** مدیریت خطا و لاگینگ برای هر زیرماژول
