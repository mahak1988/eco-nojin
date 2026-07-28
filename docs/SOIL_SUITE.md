# بسته خاک: آبشویی نیترات، پروفیل، اصلاح، KGE/PBIAS

پایه: `/api/v1/science/soil`

| # | مدل/شاخص | مسیر |
|---|----------|------|
| 1 | آبشویی لایه‌ای NO₃ | `POST .../nitrate-leaching` |
| 2 | FC/WP/AWC از بافت | `POST .../texture-hydrology` |
| 3 | ذخیره SOC | `POST .../soc-stock` |
| 4 | نیاز آهک | `POST .../liming` |
| 5 | CEC | `POST .../cec` |
| 6 | آبشویی شوری (LR) | `POST .../salinity-leaching` |
| 7 | گچ / ESP | `POST .../gypsum` |
| 8 | تراکم | `POST .../compaction` |
| 9 | RUSLE-lite | `POST .../rusle` |
| 10 | کربن اصلاح‌کننده | `POST .../amendment-carbon` |
| 11 | شاخص آبشویی N | `POST .../n-leaching-index` |
| 12 | N پروفیل | `POST .../profile-n` |
| 13 | نفوذ Green-Ampt | `POST .../infiltration` |
| 14 | دمای پروفیل | `POST .../temperature` |
| 15 | سلامت خاک | `POST .../health-score` |
| 16 | KGE/PBIAS/NSE | `POST .../evaluate` |
| — | کاتالوگ | `GET .../catalog` |

## آبشویی نیترات
چند لایه با ظرفیت FC؛ زهکش غلظت NO₃ را به لایه زیرین یا خارج از ریشه می‌برد.

## KGE و PBIAS
- **KGE** = 1 − √[(r−1)²+(α−1)²+(β−1)²]
- **PBIAS** = 100·Σ(S−O)/Σ(O) — مثبت = بیش‌برآورد

```powershell
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/science/soil/catalog
curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" `
  -d "{\"days\":90,\"rain_mm_day\":2,\"irrigation_mm_day\":1,\"no3_kg_ha_layer\":30}" `
  http://localhost:8000/api/v1/science/soil/nitrate-leaching
```
