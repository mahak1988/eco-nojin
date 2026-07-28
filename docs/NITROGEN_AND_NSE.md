# چرخه نیتروژن خاک و معیار NSE

## چرخه N

`POST /api/v1/science/nitrogen/run`

### استخرها (t N/ha)
| استخر | نقش |
|--------|-----|
| N_org | نیتروژن آلی |
| NH4 | آمونیوم |
| NO3 | نیترات |

### فرآیندها
معدنی‌سازی، تثبیت میکروبی، نیتریفیکاسیون، دنیتریفیکاسیون، آبشویی، جذب گیاه، کود، رسوب جوی.

### مثال
```json
{
  "years": 10,
  "fertilizer_n_t_ha_y": 0.12,
  "temp_c": 16,
  "moisture_frac": 0.6,
  "soc_t_ha": 40,
  "cn_ratio": 12
}
```

`POST /api/v1/science/nitrogen/evaluate` — اجرا + NSE/RMSE روی سری مشاهده‌شده.

---

## معیارهای ارزیابی

`GET /api/v1/science/metrics/catalog`  
`POST /api/v1/science/metrics/evaluate`

### NSE (Nash–Sutcliffe)
\[
\mathrm{NSE} = 1 - \frac{\sum (O_i - S_i)^2}{\sum (O_i - \bar O)^2}
\]

| مقدار | تفسیر (Moriasi 2007، تقریبی) |
|------|------------------------------|
| > 0.75 | خیلی خوب |
| 0.65–0.75 | خوب |
| 0.50–0.65 | قابل قبول |
| < 0.50 | نامطلوب |
| < 0 | بدتر از میانگین مشاهدات |

**نکته:** NSE به خطا در مقادیر بالا حساس است؛ برای سری‌های هموار SOC گاهی KGE و PBIAS مکمل بهتری‌اند.

### سایر شاخص‌ها
- **RMSE / MAE** — خطا با واحد متغیر
- **PBIAS** — درصد بایاس (مثبت = بیش‌برآورد)
- **R²** — همبستگی مربعی (بایاس را نمی‌بیند)
- **KGE** — ترکیب همبستگی، انحراف معیار، بایاس

```powershell
curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" `
  -d "{\"observed\":[1,2,3,4],\"simulated\":[1.1,1.9,3.2,3.8],\"variable\":\"demo\"}" `
  http://localhost:8000/api/v1/science/metrics/evaluate
```
