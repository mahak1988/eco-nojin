# مدل‌های شبیه‌سازی کربن خاک (Econojin)

## فهرست

| مدل | استخرها | فایل / API |
|-----|---------|-----------|
| **RothC-26.3** | DPM, RPM, BIO, HUM, IOM | `rothc_model.py` · `POST /api/v1/science/rothc/run` |
| **ICBM** | Young, Old | `soil_carbon.py` · `POST .../soil-carbon/icbm` |
| **CENTURY-3** | Active, Slow, Passive | `POST .../soil-carbon/century3` |
| **Yasso07-lite** | A, W, E, N, H | `POST .../soil-carbon/yasso` |
| **Ensemble** | مقایسه هر چهار | `POST .../soil-carbon/ensemble` |
| کاتالوگ | — | `GET .../soil-carbon/catalog` |

## معادلات خلاصه

### RothC
تجزیه با عوامل `a(T)·b(θ)·c(cover)`؛ ثابت‌های k استاندارد؛ IOM اختیاری Falloon.

### ICBM
```
dY/dt = i − k_Y · r_e · Y
dO/dt = h · k_Y · r_e · Y − k_O · r_e · O
```
`k_Y≈0.8 y⁻¹`, `k_O≈0.006 y⁻¹`, `h≈0.125`

### CENTURY-3
سه استخر با نرخ وابسته به دما/رطوبت/رس؛ ورودی متابولیک → Active.

### Yasso-lite
پنج استخر لاشبرگ/SOM با پاسخ دمایی نمایی و عامل بارش؛ **نه** باینری رسمی SYKE.

## ورودی مشترک پیشنهادی
```json
{
  "years": 20,
  "soc_t_ha": 40,
  "c_input_t_ha_y": 1.5,
  "temp_c": 15,
  "rain_mm_year": 650,
  "et_mm_year": 700,
  "clay_pct": 25
}
```

## مثال ensemble
```powershell
curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" `
  -d "{\"years\":20,\"soc_t_ha\":18,\"c_input_t_ha_y\":0.9,\"temp_c\":17.5,\"rain_mm_year\":280,\"et_mm_year\":1400,\"clay_pct\":28}" `
  http://localhost:8000/api/v1/science/soil-carbon/ensemble
```

## محدودیت
همه مدل‌ها **تقریب فرآیندی** هستند؛ برای MRV رسمی باید با داده میدانی کالیبره و با پروتکل ملی/بین‌المللی هم‌راستا شوند.
