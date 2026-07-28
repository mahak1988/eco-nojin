# راستی‌آزمایی — هم‌تراز با مخزن فعلی (۲۰۲۶-۰۷-۲۸)

## حکم

گزارش «۱۰۰٪ فاز ۱ و ۲ با Coverage ۷۸٪» **رد** می‌شود.  
وضعیت عملی: **MVP قابل‌اجرا + فاز ۳ Wave 2 در کد**؛ نه production علمی کامل.

## موجود در مخزن (نمونه)

| حوزه | مسیر |
|------|------|
| Farms/Crops/Water/Planting/Inventory | `apps/farms` … `apps/inventory` |
| Satellite | `apps/satellite/` |
| Weather | `apps/weather/` |
| Science API | `apps/simulation/phase3_router.py` |
| Simulation runs | `apps/simulation/models_runs.py` |
| PostGIS helpers | `apps/shared_core/geo/postgis.py` |

## 404 روی `/api/v1/science/*`

معمولاً: uvicorn بدون restart کامل، یا خطای import در لود router.  
پس از این commit، import Celery از مسیر hot-load حذف شد. لاگ باید `science: router loaded` باشد.

## PowerShell curl

بدنه JSON را با **تک‌کوتیشن** بدهید تا escape خراب نشود:

```powershell
curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" -d '{"days":20}' http://localhost:8000/api/v1/science/aquacrop-advanced
```
