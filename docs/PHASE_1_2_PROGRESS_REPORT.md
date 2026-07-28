# گزارش راستی‌آزمایی فاز ۱ و ۲ — Econojin

**تاریخ:** ۲۰۲۶-۰۷-۲۸  
**وضعیت واقعی:** MVP عملیاتی (نه Production 100٪ ادعاشده در پیش‌نویس)

---

## ۱. حکم کلی

پیش‌نویس گزارش «فاز ۱ و ۲ ۱۰۰٪ تکمیل» با مخزن **مغایرت جدی** دارد.  
آنچه در مخزن هست یک **پلتفرم MVP قوی** با auth، مزرعه/محصول/آب، ماهواره/هواشناسی، شبیه‌ساز stub، و ده‌ها صفحه FE است — اما:

| ادعای پیش‌نویس | واقعیت مخزن |
|----------------|-------------|
| ~۸۵ endpoint production-ready | ده‌ها endpoint فعال؛ بخشی demo/stub |
| Coverage بک‌اند ~۷۸٪ | تست واحد محدود (indices/weather/contract)؛ **۷۸٪ تأیید نشده** |
| Coverage فرانت ~۶۵٪ | تست FE گسترده **وجود ندارد** |
| p95 API ~۱۸۰ms | **اندازه‌گیری load test در CI نیست** |
| AquaCrop FAO package واقعی | مدل شفاف / stub محلی |
| SWAT+ کامل + genetic coupling | اسکلت hydrology؛ coupling ساده |
| sentinelhub-py + دانلود تصویر | synthetic + STAC اختیاری + Open-Meteo |
| ERA5 از ۱۹۵۰ ساعتی | Open-Meteo archive (روزانه، بدون کلید) |
| CHIRPS ۵km رسمی | proxy Open-Meteo precip |
| PostGIS production | کد آماده؛ روی ماشین شما SQLite (بدون Docker) |
| ۱۰۰٪ صفحات به API واقعی | بسیاری از صفحات API دارند؛ بخشی هنوز mock/نیمه‌کامل |
| PWA کامل + Zustand + React Query بهینه | جزئی؛ ادعای bundle ۱.۱MB تأیید نشده |
| Admin panel کامل جدا | اسکلت admin در web |

**نتیجه:** گزارش پیش‌نویس برای مخاطب بیرونی **غیرقابل اتکا** است. این فایل جایگزین راستی‌آزمایی است.

---

## ۲. آنچه واقعاً آماده است (تأییدشده)

### بک‌اند
- Auth: register/login/refresh/logout + HttpOnly cookie + revoke jti
- RBAC seed + `require_permission` روی writeهای مهم
- Farms CRUD + GeoJSON + spatial nearby (Haversine / PostGIS)
- Crops catalog (≥۱۰۰) + agronomy fields + irrigation calc + **rotation-plan / yield-prediction** (جدید)
- Water dashboard/sources/quality/schedules + **balance** (جدید)
- Inventory items + seed
- Monitoring sensors/readings/alerts + WS broadcast
- Satellite NDVI/NDWI/NDMI/SMI/**EVI** + cache table + timeseries
- Weather forecast + ERA5/CHIRPS-like + drought/flood/frost alerts
- Simulation jobs aquacrop/rothc/compare (محلی/Celery)
- Alembic chain خطی تا `20260728_0002`

### فرانت
- ده‌ها صفحه: Auth, Farms, Crops, Water, Monitoring, Satellite, Education, Accounting, Simulators, …
- اتصال نسبی به API؛ کیفیت ناهمگون

### تست
```text
pytest tests/unit/test_indices.py tests/unit/test_weather_alerts.py tests/unit/test_sentinel_fetcher.py
# انتظار: ۱۰ passed
```

---

## ۳. شکاف‌های باقی‌مانده برای «نزدیک به ادعای فاز ۱–۲»

### اولویت P0
1. Docker + Postgres+PostGIS روی محیط هدف
2. Coverage واقعی pytest با گزارش coverage
3. Contract tests برای همه writeها
4. حذف any و codegen OpenAPI در FE

### اولویت P1
5. AquaCrop/SWAT واقعی یا وابستگی اختیاری مستند
6. GEE credentials برای EO زنده
7. FE: Dashboard stats از `/api/v1/dashboard/overview`
8. Admin health واقعی

### اولویت P2
9. Psychology/Store/Desktop به‌صورت ماژول‌های محصول جدا (فعلاً در گزارش بیش‌ادعا شده)
10. Locust/k6 در CI

---

## ۴. Endpointهای تکمیل‌شده در این commit (شکاف گزارش)

| Endpoint | نقش |
|----------|-----|
| `POST /api/v1/crops/rotation-plan` | برنامه تناوب |
| `GET /api/v1/crops/yield-prediction` | پیش‌بینی عملکرد ساده |
| `GET /api/v1/crops/disease-rules` | قوانین بیماری |
| `GET /api/v1/water/balance` | تراز آب |
| `GET /api/v1/dashboard/overview` | آمار داشبورد |
| `GET /api/v1/weather/current` | آب‌وهوای فعلی |
| `GET /api/v1/weather/historical` | تاریخی ERA5 |
| `POST /api/v1/simulation/coupling/run` | coupling سبک AquaCrop+RothC |
| EVI در indices | شاخص پوشش بهبودیافته |

---

## ۵. آمار صادقانه (تقریبی)

| شاخص | مقدار واقعی تقریبی |
|------|---------------------|
| صفحات FE (tsx) | ~۶۰ فایل صفحه |
| ماژول‌های بک‌اند دامنه | ~۱۵ پوشه (عمق متفاوت) |
| تست واحد EO/Weather | ۱۰ |
| Docker روی dev شما | نصب نشده |
| DB پیش‌فرض local | SQLite |

---

## ۶. آمادگی فاز ۳

فاز ۳ علمی فقط پس از:
- Postgres+PostGIS
- کلیدهای GEE/Copernicus در صورت نیاز به EO واقعی
- Job queue پایدار (Redis+Celery)
- پذیرش گزارش **صادقانه** به‌جای اعداد نمایشی

---

**تهیه:** راستی‌آزمایی خودکار در برابر مخزن `mahak1988/eco-nojin`
