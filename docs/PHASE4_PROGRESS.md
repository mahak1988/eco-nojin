# Phase 4 progress

## Backend verified (user machine)
- `GET /api/v1/crops` → envelope OK
- `GET /api/v1/farms` → envelope OK
- `pytest tests/contract/test_phase3_api.py` → 7 passed

## This wave
- `POST /api/v1/crops/seed-demo` — open in non-production (no RBAC block)
- `POST /api/v1/farms/seed-demo` — 3 demo farms if empty
- FE Farms/Crops pages: auto-seed when empty + i18n `t()`

## Commands
```powershell
git pull origin main
# restart API
curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://127.0.0.1:8000/api/v1/crops/seed-demo
curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://127.0.0.1:8000/api/v1/farms/seed-demo
curl.exe -H "User-Agent: Mozilla/5.0" "http://127.0.0.1:8000/api/v1/crops?page=1&size=5"
curl.exe -H "User-Agent: Mozilla/5.0" "http://127.0.0.1:8000/api/v1/farms?page=1&size=5"

cd apps\web
Copy-Item .env.example .env.local -ErrorAction SilentlyContinue
pnpm dev
# open http://localhost:5173/crops and /farms
```

## Next (still Phase 4)
- Wire LoginForm fully to cookie + Bearer fallback
- DashboardPage → `/api/v1/dashboard/stats`
- Expand i18n namespaces (farms, crops, science)
