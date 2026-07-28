# SSOT — Phase 0–3 status (honest, matches repository)

**Updated:** 2026-07-28  
**Rule:** Numbers without measurement are forbidden. Inflated progress reports are obsolete.

## What is true in the repo

### Phase 0 infrastructure
- FastAPI entry `apps/main.py`, CORS limited, local rate-limit optional
- Alembic chain through `20260728_0004`
- RBAC models + `require_permission`
- Auth with cookies path; JWT HS256 default, RS256 optional
- Celery app + Redis config; works when Redis is up
- Docker compose: postgres(postgis) + redis + api + worker + beat

### Phase 1 agriculture core (API)
- `apps/farms`, `crops`, `water`, `planting`, `inventory`, `weather`, `notifications`
- Auth/register/login paths under users
- Specialized crop fields, rotation/yield/disease helpers
- **Not claimed:** measured Lighthouse >80, full 26 FE pages production-polished

### Phase 2 monitoring / EO / simulation MVP
- `apps/monitoring`, `apps/satellite` (GEE/MPC/synthetic providers)
- Weather alerts: drought/flood/frost/heat
- AquaCrop/RothC stubs + coupling + PDF/CSV export helpers
- WebSocket module present

### Phase 3 Wave 1–2
- `/api/v1/science/*` — swat proxy, aquacrop advanced, scenarios, climate ETL
- `simulation_runs` persist, NDVI→canopy, Celery tasks (lazy)
- PostGIS `farms.geom` + GIST when Postgres

## Explicitly false / not measured

| Claim in marketing report | Reality |
|---------------------------|---------|
| Backend coverage 78% | Not measured project-wide; unit tests exist for indices/weather/phase3 |
| Frontend 100% API-connected / 39 pages | Many pages exist; connection quality uneven |
| p95 ~180ms Locust | Not run in this environment |
| Official FAO AquaCrop / SWAT+ binary | Process proxies only |
| sentinelhub paid pipeline | Optional/synthetic + GEE when keyed |
| Zustand/PWA full production | Partial at best |

## Verify science routes after pull

```powershell
git pull origin main
# MUST fully stop and restart uvicorn (Ctrl+C then):
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
# Log must contain: science: router loaded

curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/science/status
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/science/runs
curl.exe -H "User-Agent: Mozilla/5.0" "http://localhost:8000/api/v1/science/ndvi-canopy?lat=32.65&lon=51.67&days=60"

# PowerShell JSON body (use single-quoted -d):
curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" `
  -d '{"days":20,"persist":true}' `
  http://localhost:8000/api/v1/science/aquacrop-advanced
```

If log shows `science: ...` warning, paste that line — do not assume 100% without `router loaded`.
