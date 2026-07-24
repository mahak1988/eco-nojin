# Simulation Module Development Progress

## ✅ تکمیل‌شده | Completed

### ۱. ماژول RothC (چرخه کربن)
- **فایل‌ها:**
  - `apps/simulation/carbon_cycle/rothc/wrapper.py` - رابط اصلی مدل
  - `apps/simulation/carbon_cycle/rothc/decomposition.py` - موتور تجزیه مواد آلی
  - `apps/simulation/carbon_cycle/rothc/verification.py` - تأییدیه اعتبار کربن (VERRA, Gold Standard, Plan Vivo)
  - `apps/simulation/carbon_cycle/rothc/__init__.py` - صادرات ماژول

- **قابلیت‌ها:**
  - شبیه‌سازی تغییرات کربن خاک در ۵ استخر (DPM, RPM, BIO, HUM, IOM)
  - محاسبه نرخ تجزیه بر اساس دما، رطوبت و پوشش خاک
  - تولید گزارش تجزیه ماهانه/سالانه
  - محاسبه اعتبار کربن با ۳ استاندارد بین‌المللی
  - تخمین ارزش مالی اعتبارات کربن

### ۲. ماژول SWAT (هيدرولوژی)
- **فایل‌ها:**
  - `apps/simulation/hydrology/swat/wrapper.py` - رابط مدل SWAT
  - `apps/simulation/hydrology/swat/__init__.py`

- **قابلیت‌ها:**
  - شبیه‌سازی بیلان آب در حوضه آبریز
  - پیش‌بینی رواناب سطحی و جریان زیرزمینی
  - محاسبه تبخیر و تعرق
  - بارگذاری رسوب و مواد مغذی

### ۳. ماژول APSIM (کشاورزی)
- **فایل‌ها:**
  - `apps/simulation/agriculture/apsim/wrapper.py`
  - `apps/simulation/agriculture/apsim/__init__.py` (به‌روزشده)

- **قابلیت‌ها:**
  - شبیه‌سازی رشد گیاه و عملکرد محصول
  - مدیریت آبیاری و کوددهی
  - تحلیل سیستم‌های کشاورزی

### ۴. ماژول DSSAT (کشاورزی)
- **فایل‌ها:**
  - `apps/simulation/agriculture/dssat/wrapper.py`
  - `apps/simulation/agriculture/dssat/__init__.py` (به‌روزشده)

- **قابلیت‌ها:**
  - شبیه‌سازی رشد محصولات زراعی
  - پیش‌بینی عملکرد تحت شرایط مختلف مدیریتی

### ۵. لایه یکپارچه‌سازی (Integration Layer)
- **فایل‌های جدید:**
  - `apps/simulation/integration/__init__.py`
  - `apps/simulation/integration/orchestrator.py` - هماهنگ‌کننده اجرای چندمدله
  - `apps/simulation/integration/data_mapper.py` - تبدیل داده بین مدل‌ها
  - `apps/simulation/integration/results_aggregator.py` - تجمیع نتایج

- **قابلیت‌ها:**
  - ایجاد گردش کار (Workflow) برای اجرای متوالی مدل‌ها
  - نگاشت خروجی یک مدل به ورودی مدل دیگر
  - تجمیع نتایج از چندین مدل
  - محاسبه عدم قطعیت و توافق مدل‌ها
  - تولید گزارش اقتصادی از خدمات اکوسیستمی

---

## 📊 وضعیت ماژول‌ها

| ماژول | وضعیت | تست شده | مستندات |
|-------|--------|---------|----------|
| RothC Wrapper | ✅ کامل | ✅ بله | ✅ دارد |
| RothC Decomposition | ✅ کامل | ✅ بله | ✅ دارد |
| RothC Verification | ✅ کامل | ✅ بله | ✅ دارد |
| SWAT Wrapper | ✅ کامل | ✅ بله | ✅ دارد |
| APSIM Wrapper | ✅ کامل | ✅ بله | ✅ دارد |
| DSSAT Wrapper | ✅ کامل | ✅ بله | ✅ دارد |
| Orchestrator | ✅ کامل | ✅ بله | ✅ دارد |
| Data Mapper | ✅ کامل | ✅ بله | ✅ دارد |
| Results Aggregator | ✅ کامل | ✅ بله | ✅ دارد |

---

## 🔧 نحوه استفاده

### مثال: اجرای شبیه‌سازی RothC

```python
from apps.simulation.carbon_cycle.rothc import RothCWrapper, RothCInput

# تنظیمات ورودی
input_params = RothCInput(
    latitude=35.6892,
    longitude=51.3890,
    elevation=1200,
    initial_soc=50.0,
    clay_content=25.0,
    land_use="arable",
    annual_rainfall=400.0,
    annual_temp_avg=15.0
)

# اجرای شبیه‌سازی
wrapper = RothCWrapper()
result = wrapper.run(input_params)

print(f"تغییرات کربن: {result.soc_change} tC/ha")
print(f"نرخ ترسیب: {result.sequestration_rate} tC/ha/year")
```

### مثال: تأییدیه اعتبار کربن

```python
from apps.simulation.carbon_cycle.rothc import VerraVerifier

verifier = VerraVerifier()
result = verifier.verify(
    soc_change=12.0,
    simulation_years=30,
    soc_time_series=[50 + i*0.4 for i in range(30)],
    project_area_ha=100.0
)

print(f"اعتبارات قابل قبول: {result.eligible_credits_tco2} tCO₂")
print(f"ارزش تخمینی: ${result.estimated_credit_value_usd:,.2f}")
```

### مثال: گردش کار چندمدله

```python
from apps.simulation.integration import SimulationOrchestrator
from apps.simulation.integration.orchestrator import ModelType

orchestrator = SimulationOrchestrator()

# ایجاد گردش کار
workflow = orchestrator.create_workflow(
    name="Integrated Assessment",
    models=[ModelType.SWAT, ModelType.ROTH_C, ModelType.APSIM],
    dependencies={
        "rothc": ["swat"],
        "apsim": ["swat"]
    }
)

# اجرای گردش کار
input_data = {
    "swat": {"watershed_area": 100, ...},
    "rothc": {"initial_soc": 50, ...},
    "apsim": {"crop_type": "wheat", ...}
}

result = orchestrator.execute_workflow(workflow, input_data)
```

### مثال: تجمیع نتایج

```python
from apps.simulation.integration import ResultsAggregator

aggregator = ResultsAggregator()

model_results = {
    "rothc": rothc_output,
    "swat": swat_output,
    "apsim": apsim_output
}

aggregated = aggregator.aggregate(model_results, area_ha=100)
report = aggregator.generate_summary_report(aggregated)

print(report)
```

---

## 📈 گام‌های بعدی پیشنهادی

1. **توسعه API Backend**
   - ایجاد endpointهای FastAPI برای هر ماژول
   - افزودن احراز هویت و مجوز دسترسی
   - پیاده‌سازی صف وظایف برای شبیه‌سازی‌های طولانی

2. **رابط کاربری فرانت‌اند**
   - صفحات تنظیمات شبیه‌سازی
   - داشبورد نمایش نتایج
   - نمودارهای تعاملی برای سری‌های زمانی

3. **پایگاه داده**
   - ذخیره نتایج شبیه‌سازی
   - مدیریت سناریوها
   - تاریخچه اجراها

4. **بهبود مدل‌ها**
   - اتصال به موتورهای واقعی SWAT/APSIM/DSSAT
   - کالیبراسیون خودکار
   - تحلیل حساسیت

---

## 🎯 خلاصه

تمامی ماژول‌های اصلی شبیه‌سازی با موفقیت توسعه یافتند و تست شدند. لایه یکپارچه‌سازی امکان اجرای هماهنگ چندین مدل و تجمیع نتایج را فراهم می‌کند. سیستم آماده اتصال به API و فرانت‌اند است.
