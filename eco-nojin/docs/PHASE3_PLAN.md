# فاز ۳ — یکپارچگی علمی (Postgres · GEE · مدل‌های سنگین)

**شروع:** ۲۰۲۶-۰۷-۲۸  
**وضعیت:** Wave 1 پیاده‌سازی‌شده در مخزن

## اهداف Wave 1 (این commit)

| آیتم | وضعیت |
|------|--------|
| مسیر Postgres با `FORCE_POSTGRES=1` | ✅ |
| Migration `20260728_0003` (PostGIS + simulation_runs) | ✅ |
| GEE probe `/api/v1/satellite/gee/status` | ✅ (نیاز به کلید واقعی) |
| SWAT+ proxy علمی | ✅ `/api/v1/science/swat` |
| AquaCrop پیشرفته + NDVI canopy | ✅ `/api/v1/science/aquacrop-advanced` |
| Climate ETL (Open-Meteo) | ✅ `/api/v1/science/climate-drivers` |
| Scenario ranking | ✅ `/api/v1/science/scenarios` |
| Farm pipeline climate→models | ✅ `/api/v1/science/pipeline/farm-run` |

## صریحاً هنوز انجام نشده

- باینری رسمی SWAT+ / FAO AquaCrop plugin
- اجرای واقعی GEE بدون Service Account
- Docker روی ویندوز کاربر (اگر Docker نصب نباشد)

## راه‌اندازی Postgres

```powershell
.\scripts\phase3_postgres.ps1
# یا دستی:
$env:FORCE_POSTGRES="1"
$env:DATABASE_URL="postgresql+asyncpg://econojin:econojin@127.0.0.1:5432/econojin"
alembic upgrade head
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

## GEE

رجوع به `docs/GEE_SETUP.md` سپس:

```powershell
pip install -r requirements-scientific.txt
# secrets/gee-sa.json + env GEE_*
curl.exe http://localhost:8000/api/v1/satellite/gee/status
```

## تست مدل‌ها (بدون Docker)

```powershell
curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" -d "{}" http://localhost:8000/api/v1/science/swat
curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" -d "{\"days\":30}" http://localhost:8000/api/v1/science/aquacrop-advanced
curl.exe -H "User-Agent: Mozilla/5.0" "http://localhost:8000/api/v1/science/climate-drivers?lat=32.65&lon=51.67"
curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" -d "{}" http://localhost:8000/api/v1/science/scenarios
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/science/status
```

## Wave 2 (بعدی)

1. ذخیره simulation_runs در DB
2. Celery task برای SWAT/AquaCrop advanced
3. کالیبراسیون NDVI→AquaCrop از `/satellite/timeseries`
4. نصب Docker + PostGIS spatial indexes روی farms
