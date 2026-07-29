# کالیبراسیون کربن خاک و پویایی مواد آلی

## ۱. کالیبراسیون SOC

`POST /api/v1/science/soil-carbon/calibrate`

```json
{
  "model": "rothc",
  "observed_soc": [40, 39.2, 38.8, 38.5, 38.3],
  "base_params": { "temp_c": 15, "rain_mm_year": 650, "et_mm_year": 700, "clay_pct": 25 },
  "free_params": ["c_input_t_ha_y", "dpm_rpm_ratio"],
  "n_samples": 100,
  "metric": "rmse"
}
```

مدل‌ها: `rothc` | `icbm` | `century3` | `yasso07_lite`  
خروجی: `best.free_params`, `rmse`, `nse`, `simulated_soc`, `top_trials`

روش: جستجوی تصادفی + پالایش محلی (نه MCMC کامل).

## ۲. پویایی مواد آلی

| مدل | مسیر | محتوا |
|-----|------|--------|
| دو استخری | `POST .../organic-matter/two-pool` | Labile / Stable |
| C–N | `POST .../organic-matter/cn` | معدنی‌سازی و تثبیت N |
| لاشبرگ | `POST .../organic-matter/litter` | Litter → OM → Passive |
| کاتالوگ | `GET .../organic-matter/catalog` | فهرست |

### دو استخری
\(dL = I f_L - k_L f L\)، \(dS = I(1-f_L) + \alpha k_L f L - k_S f S\)

### C–N
تقاضای میکروبی نسبت به C:N بحرانی؛ کمبود N معدنی → immobilization.

## مثال
```powershell
curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" `
  -d "{\"model\":\"icbm\",\"observed_soc\":[30,29.5,29.1,28.8,28.6],\"n_samples\":60}" `
  http://localhost:8000/api/v1/science/soil-carbon/calibrate

curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" `
  -d "{\"years\":20,\"om_t_ha\":80,\"om_input_t_ha_y\":3,\"temp_c\":16,\"moisture_frac\":0.5}" `
  http://localhost:8000/api/v1/science/organic-matter/two-pool
```
