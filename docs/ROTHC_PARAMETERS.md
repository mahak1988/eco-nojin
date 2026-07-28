# پارامترهای دقیق RothC-26.3

## API
| مسیر | نقش |
|------|-----|
| `GET /api/v1/science/rothc/schema` | کاتالوگ کامل (min/max/unit/گروه/راهنما) |
| `GET /api/v1/science/rothc/presets` | پیش‌تنظیم‌ها |
| `GET /api/v1/science/rothc/defaults?preset=iran_arid_rainfed` | پیش‌فرض + استخرهای resolveشده |
| `POST /api/v1/science/rothc/run` | اجرا با body کامل |

## گروه‌ها
1. **simulation** — `years`
2. **initial_pools** — `soc_t_ha`, `iom`, `dpm`, `rpm`, `bio`, `hum`, `use_falloon_iom`
3. **management** — `c_input_t_ha_y`, `dpm_rpm_ratio`, `plant_cover`
4. **soil** — `clay_pct`
5. **climate** — `temp_c`, `rain_mm_year`, `et_mm_year`
6. **advanced** — `k_dpm/rpm/bio/hum`

## نسبت ورودی DPM/RPM
| منبع | نسبت |
|------|------:|
| محصولات زراعی | 1.44 |
| کود حیوانی (FYM) | 1.0 |
| مرتع | ~0.67 |
| چوبی | ~0.25 |

## IOM
اگر `iom_t_ha` نباشد و `use_falloon_iom=true`:  
`IOM = 0.049 × SOC^1.139` (Falloon).

## Preset نمونه ایران
`iran_arid_rainfed`: SOC=18، ورودی=0.9، بارش=280، ET=1400، رس=28٪، دما=17.5°C

## مثال curl
```powershell
curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" `
  -d "{\"preset\":\"iran_arid_rainfed\",\"years\":20,\"persist\":false}" `
  http://localhost:8000/api/v1/science/rothc/run
```
