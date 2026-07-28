# Source of Truth — Phase 1 & 2 (aligned with repository)

**Date:** 2026-07-28  
**Rule:** This document describes only what exists in `mahak1988/eco-nojin`. No marketing numbers.

## Completion definition (MVP-100%)

Phase 1–2 **MVP** is complete when all checklist rows below are ✅ in code and callable without Docker (SQLite) or with Docker (Postgres).

### Backend checklist

| Area | Status | Notes |
|------|--------|-------|
| Auth + cookies + refresh revoke | ✅ | |
| RBAC seed + require_permission | ✅ | soft-skip local if REQUIRE_AUTH_FOR_WRITES=false |
| Farms CRUD + spatial nearby | ✅ | PostGIS when PG; else Haversine |
| Crops catalog + rotation + yield + disease | ✅ | rule-based |
| Water dashboard + balance + schedules | ✅ | |
| Inventory + analytics + cost | ✅ | |
| Planting plans/tasks + season/growth | ✅ | |
| Monitoring sensors/alerts + WS | ✅ | |
| Satellite NDVI/NDWI/NDMI/EVI/SMI | ✅ | synthetic default; STAC optional |
| Weather forecast/current/ERA5/alerts | ✅ | Open-Meteo; heat/drought/flood/frost |
| Simulation aquacrop/rothc/coupling | ✅ | local/Celery stub |
| Dashboard overview | ✅ | |
| AI agents chat (auth) + public providers/feedback | ✅ | LLM keys optional |
| Alembic linear chain | ✅ | through 20260728_0002 |

### Explicitly NOT claimed

- FAO AquaCrop binary package / full SWAT+ basin calibration
- sentinelhub paid download pipeline
- Measured 78% pytest coverage / Locust p95
- Full PWA offline + Zustand migration of entire FE
- Psychology / Store / Desktop product modules as production systems

### Frontend

~60 page components exist; many call real APIs; quality is uneven. **Not** asserted as 100% production UX.

### Verify

```powershell
git pull origin main
pytest tests/unit/test_indices.py tests/unit/test_weather_alerts.py tests/unit/test_sentinel_fetcher.py -q
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/dashboard/overview
curl.exe -H "User-Agent: Mozilla/5.0" "http://localhost:8000/api/v1/satellite/indices?lat=32.65&lon=51.67"
curl.exe -H "User-Agent: Mozilla/5.0" "http://localhost:8000/api/v1/weather/alerts?lat=32.65&lon=51.67"
curl.exe -H "User-Agent: Mozilla/5.0" "http://localhost:8000/api/v1/planting/season-plan?crop=wheat"
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/ai-agents/providers
```

### Ready for next report (Phase 3)

Inputs needed: Docker/Postgres, optional GEE keys, acceptance of SSOT scope above.
