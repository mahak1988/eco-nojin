# Phase 2 progress

## Backend

| ID | Module | Status |
|----|--------|--------|
| F2.1 | apps/monitoring | Done — sensors, readings, alerts, rules |
| F2.2 | Celery AquaCrop/RothC + PDF/CSV | Done (sync fallback if Redis down) |
| F2.3 | apps/satellite | Catalog + roles + topography/thermal/NDVI |
| WS | /ws/monitoring | Done |

## Free satellite / GIS sources (no key for dev)

| Source | Roles |
|--------|-------|
| Sentinel-2 | vegetation, optical |
| Landsat 8/9 | vegetation, thermal, optical |
| MODIS / VIIRS | vegetation, thermal |
| Sentinel-1 SAR | radar, soil |
| SRTM / ASTER / OpenTopoData | topography |
| NASA POWER / Open-Meteo | precipitation, thermal |
| OSM / NASA GIBS | gis_basemap, optical |

API:
- GET /api/v1/satellite/catalog?role=topography
- GET /api/v1/satellite/topography
- GET /api/v1/satellite/thermal
- GET /api/v1/satellite/ndvi
- GET /api/v1/satellite/by-role?role=vegetation

Simulations:
- POST /api/v1/simulations/aquacrop
- POST /api/v1/simulations/rothc
- GET /api/v1/simulations/jobs/{task_id}

WebSocket: ws://localhost:8000/ws/monitoring

## Celery (optional)

```bash
redis-server
celery -A apps.shared_core.celery_app.celery_app worker -l info
```

Without Redis, API runs models synchronously and still writes PDF/CSV under artifacts/simulation_exports/.
