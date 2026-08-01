# برنامه ورود محتوای سند هیدروما نوژین به اکو نوژین

منبع: طرح توجیهی فنی کسب‌وکار هیدروما نوژین (۲۰۵ صفحه).

## فاز C1 — داده و کاتالوگ (انجام‌شده در کد)

- [x] `apps/simulation/climate_zones.py` — اقلیم‌های جهانی قابل انتخاب
- [x] `apps/simulation/satellite_catalog.py` — Copernicus, Landsat, NASA POWER, JAXA, GEE, …
- [x] `apps/simulation/fao_indices.py` — FAO-56, SPI, SPEI, SSI, VHI, …
- [x] `apps/content/hydroma_eco_bridge.md` — پل محتوایی دو برند

## فاز C2 — API عمومی Science

- `GET /api/v1/science/climate-zones`
- `GET /api/v1/science/satellite-catalog`
- `GET /api/v1/science/indices-catalog`

## فاز C3 — صفحات وب (مسیرهای موجود)

| محتوا | مسیر پیشنهادی موجود |
|--------|---------------------|
| پل هیدروما/اکو | Education / Library / About blocks |
| انتخاب اقلیم | Science / Farm wizard |
| کاتالوگ ماهواره | Satellite dashboard |
| شاخص خشکسالی | Monitoring / Science |
| ۸ ماژول | Home + Science hub |
| اصول ۴گانه مهندسی | Library articles |
| مدل تقسیم سود / حکمرانی | Policies / Mrv (متنی، بدون ادعای حقوقی) |
| FFS / آموزش | Education |

## فاز C4 — وبلاگ / کتابخانه (متن)

مقالات پیشنهادی از پیشگفتار و بیانیه مأموریت (بازنویسی کوتاه، بدون نام مکان پایلوت):

1. بازآفرینی منظر و بازگشت به تعادل
2. چهار ضعف ساختاری برنامه‌های گذشته و پاسخ دیجیتال
3. MRV سه‌سطحی و شفافیت
4. خدمات اکوسیستمی و ارزش‌گذاری
5. مدارس مزرعه‌ای و دانش بومی

## فاز C5 — مدل‌ها و تریگر

- اتصال SPI/VHI به monitors
- coupled-run + climate zone defaults
- NDVI از Sentinel مسیر (GEE اختیاری)

## قواعد محصول

1. **نام پایلوت محلی در UI عمومی نیاید** — فقط تیپ اقلیمی.
2. اکو نوژین = بازوی دیجیتال حمایتی؛ درآمد اصلی از فروش پلتفرم ادعا نشود.
3. اعداد مالی سند به‌عنوان «هدف طرح» برچسب بخورند نه KPI تولید نرم‌افزار.
4. باینری رسمی FAO/SWAT ادعا نشود؛ مدل مفهومی + citation.
