# فاز ۲ — پایش علمی و ماهواره (بدون Docker)

**پیش‌نیاز:** فاز ۱ تأیید شده (auth / farms / crops 200).

## دامنه فاز ۲

| بخش | API اصلی |
|------|----------|
| Monitoring | `/api/v1/monitoring/overview`, `/sensors`, `/alerts`, `/alert-rules`, seed-demo |
| Satellite | `/api/v1/satellite/ndvi`, `/timeseries`, `/indices`, `/change-detection`, `/availability` |
| Science / sim | `/api/v1/science/status`, aquacrop, satellite bridge |
| Weather alerts | `/api/v1/weather/...` در صورت وجود |

## محدودیت صادقانه (local)

- GEE بدون Service Account → synthetic / Open-Meteo fallback
- Celery بدون Redis → اجرای sync
- PostGIS بدون Postgres → spatial اختیاری

## تست PowerShell (بعد از `git pull` و restart API)

```powershell
# login
'{"email":"farmer1@example.com","password":"SecurePass123!"}' | Set-Content -Encoding utf8 login.json
$login = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST -ContentType "application/json" -InFile login.json
$token = $login.accessToken
$H = @{ Authorization = "Bearer $token"; "User-Agent" = "Mozilla/5.0" }

# Monitoring
Invoke-RestMethod "http://localhost:8000/api/v1/monitoring/overview" -Headers $H | ConvertTo-Json
Invoke-RestMethod -Method POST "http://localhost:8000/api/v1/monitoring/seed-demo" -Headers $H | ConvertTo-Json
Invoke-RestMethod "http://localhost:8000/api/v1/sensors?page=1&size=10" -Headers $H | ConvertTo-Json -Depth 4
Invoke-RestMethod "http://localhost:8000/api/v1/alerts?page=1&size=10" -Headers $H | ConvertTo-Json -Depth 4

# Satellite (اصفهان تقریبی)
Invoke-RestMethod "http://localhost:8000/api/v1/satellite/ndvi?lat=32.65&lon=51.67" -Headers $H | ConvertTo-Json -Depth 4
Invoke-RestMethod "http://localhost:8000/api/v1/satellite/timeseries?lat=32.65&lon=51.67&days=60" -Headers $H | ConvertTo-Json -Depth 3
Invoke-RestMethod "http://localhost:8000/api/v1/satellite/indices?lat=32.65&lon=51.67&days=60" -Headers $H | ConvertTo-Json -Depth 3
Invoke-RestMethod -Method POST "http://localhost:8000/api/v1/satellite/change-detection?lat=32.65&lon=51.67&days=120" -Headers $H | ConvertTo-Json

# Science status
Invoke-RestMethod "http://localhost:8000/api/v1/science/status" -Headers $H | ConvertTo-Json -Depth 4
```

## FE

با `pnpm run dev`:

- http://localhost:5173/monitoring
- http://localhost:5173/simulators
- http://localhost:5173/satellite (اگر route تعریف شده)

## معیار پذیرش فاز ۲ (حداقل)

| معیار | انتظار |
|--------|--------|
| monitoring/overview | 200 + status ok |
| seed-demo sensors | seeded ≥ 0 |
| satellite/ndvi یا timeseries | 200 + data یا synthetic |
| scenario router در health | دیگر در failed_routers نباشد |
| data router | لود شود |
