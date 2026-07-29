# گزارش ارزیابی شبیه‌سازهای ثبت‌شده (Registry)

**تاریخ:** ۲۰۲۶-۰۷-۲۸  
**منبع:** `apps/simulation/registry.py` — ۲۸ ماژول اعلام‌شده

## ۱. خلاصه اجرایی

| وضعیت | تعداد | توضیح |
|--------|------:|--------|
| اعلام در Registry | ۲۸ | catalogue کامل دامنه‌ها |
| بارگذاری واقعی در runtime | متغیر (اغلب ۱۴ load / ۱۴ skip در لاگ محلی) | بسیاری abstract یا وابستگی سنگین |
| موتور علمی فاز ۳ (process-based) | ۴ هسته | AquaCrop conceptual، RothC-26.3، SCS-CN، NDVI→canopy |
| باینری رسمی FAO/SWAT+/DSSAT | ۰ | عمداً proxy / conceptual |

**حکم صادقانه:** کاتالوگ وسیع است؛ عمق اجرایی روی چند مدل فرایندی و ML متمرکز است. ادعای «۲۸ شبیه‌ساز production» نادرست است.

## ۲. جدول ارزیابی بر اساس دامنه

### کشاورزی (۵)
| شناسه | کلاس | ارزیابی | اولویت توسعه |
|--------|------|---------|---------------|
| aquacrop | AquaCropSimulator | اسکلت + موتور فاز۳ `aquacrop_advanced` قوی‌تر است | **P0** یکپارچه کردن registry با science API |
| wofost | WOFOSTSimulator | اسکلت / skip محتمل | P2 — wrapper سبک LINTUL-like |
| apsim | APSIMSimulator | بدون باینری APSIM | P3 — فقط metadata + لینک خارجی |
| dssat | DSSATSimulator | بدون باینری | P3 |
| crop_model | CropModelSimulator | generic | P2 ادغام با crops catalog |

### هیدرولوژی (۵)
| شناسه | ارزیابی | اولویت |
|--------|---------|--------|
| swat | اسکلت؛ موتور SCS-CN در science جایگزین جزئی | **P0** نام‌گذاری صادقانه `scs_cn` vs SWAT+ |
| modflow | بدون MODFLOW | P3 |
| weap | اسکلت | P2 بیلان آب ساده |
| hecras | اسکلت | P3 |
| bridge | utility | P2 |

### کربن (۳)
| شناسه | ارزیابی | اولویت |
|--------|---------|--------|
| rothc | موتور `rothc_model` فاز۳ قابل اتکا | **P0** اتصال UI simulators ↔ science |
| co2fix | اسکلت | P2 |
| century | اسکلت | P2 نسخه کاهش‌یافته |

### اقتصاد / خدمات اکوسیستم / انرژی / خاک / کیفیت آب / تنوع‌زیستی (۱۵)
عمده: **اسکلت registry + دانش advisory** — نه مدل عددی کامل.  
اولویت: مستندسازی صادقانه + ۱–۲ proxy کم‌هزینه (CBA ساده، RUSLE2 بار رسوب پروکسی، MaxEnt stub).

## ۳. شکاف‌ها

1. **دو مسیر موازی:** `apps/simulation/agriculture/*` vs `apps/simulation/aquacrop_advanced.py` / science router  
2. **Celery:** فقط بخشی از مدل‌های فاز۳؛ کاتالوگ قدیمی همگام نیست  
3. **تست contract** برای `/api/v1/simulation/list` و run  
4. **FE:** صفحات aquacrop/rothc جدا از `/science`

## ۴. برنامه توسعه پیشنهادی (۱۲ هفته)

| موج | هفته | اقدام |
|-----|------|--------|
| A | ۱–۲ | SSOT: هر simulator.id → engine واقعی یا `status: stub` در OpenAPI |
| B | ۳–۴ | ادغام AquaCrop/RothC/SCS registry با `/api/v1/science/*` + persist |
| C | ۵–۶ | Celery task یکپارچه + PDF export برای ۳ موتور |
| D | ۷–۸ | RUSLE2-proxy + WEAP-balance ساده + تست |
| E | ۹–۱۰ | حذف/آرشیو stubهای بدون roadmap (APSIM/DSSAT/HEC-RAS باینری) |
| F | ۱۱–۱۲ | UI واحد Simulators Lab + SA (Sobol) روی پارامترهای AquaCrop |

## ۵. معیار پذیرش توسعه

- `GET /api/v1/simulation/list` فقط موتورهای `ready` را runnable نشان دهد  
- هر runnable: schema ورودی، citation، محدودیت  
- بدون ادعای باینری رسمی در README  

## ۶. ارتباط با Global SA

- SRC / Morris / Sobol روی **مدل ML yield** پیاده شد (`/api/v1/ml/sensitivity/global`)  
- مرحله بعد: همان pipeline روی پارامترهای AquaCrop (Ky, TAW, rain) و RothC (clay, C input)
