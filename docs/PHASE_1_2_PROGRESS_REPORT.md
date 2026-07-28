# گزارش پیشرفت فاز ۱ و ۲ — هم‌تراز با مخزن (SSOT)

نسخهٔ نمایشی قبلی با اعداد Coverage/Performance غیرقابل‌اندازه‌گیری **باطل** است.  
سند مرجع: **`docs/PHASE_1_2_SSOT.md`**

## وضعیت

**MVP فاز ۱–۲ در سطح قابلیت‌های چک‌لیست SSOT تکمیل شده است.**

این به معنی production علمی کامل (SWAT+/FAO AquaCrop/sentinelhub پولی) نیست.

## دستاوردهای قابل‌اثبات

- هسته کشاورزی: farms, crops (+rotation/yield/disease), water (+balance), planting (+season), inventory (+analytics)
- پایش و EO: monitoring, satellite indices (NDVI/NDWI/NDMI/EVI/SMI), weather alerts (+heat)
- شبیه‌سازی: aquacrop/rothc/compare/coupling (محلی)
- داشبورد: `/api/v1/dashboard/overview`
- AI: chat (auth) + providers/feedback عمومی
- استقرار محلی بدون Docker: `scripts/deploy_local.ps1`

## تست

Unit: indices, weather alerts, sentinel fetcher (۱۰ تست).

## فاز بعد

فاز ۳ علمی روی Postgres+PostGIS و کلیدهای EO واقعی، پس از تأیید SSOT.
