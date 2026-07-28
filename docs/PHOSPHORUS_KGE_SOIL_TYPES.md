# فسفر خاک، KGE عمیق، انواع خاک و اصلاح

## ۱. دینامیک فسفر
`POST /api/v1/science/phosphorus/run`

استخرها (kg P/ha): labile · active · stable · organic  
فرآیندها: کود، معدنی‌سازی، جذب، واجذب، انسداد، جذب گیاه، فرسایش، آبشویی کم  
ضریب دسترسی با **pH** و رس تنظیم می‌شود.

## ۲. خانواده KGE
`POST /api/v1/science/metrics/kge-deep`

### Gupta 2009
\(KGE = 1 - \sqrt{(r-1)^2 + (\alpha-1)^2 + (\beta-1)^2}\)  
\(\alpha=\sigma_s/\sigma_o\)، \(\beta=\mu_s/\mu_o\)

### Kling 2012 (KGE′)
\(\alpha' = CV_s/CV_o\)، \(\beta=\mu_s/\mu_o\)

### غیرپارامتری
به جای Pearson از Spearman استفاده می‌شود.

خروجی شامل **error_share** (سهم همبستگی / نوسان / بایاس) برای تشخیص است.

## ۳. انواع خاک و اصلاح
- `GET /api/v1/science/soil/types`
- `POST /api/v1/science/soil/classify`
- `POST /api/v1/science/soil/amendment-plan`

انواع: acidic, alkaline, calcareous, saline, sodic, saline_sodic, sandy, clayey, compacted, organic_poor, organic_rich, gypsiferous, normal  
برنامه: primary / secondary / avoid + تخمین آهک/گچ/LR در صورت نیاز.
