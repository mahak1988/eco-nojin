# Phase 2 progress

## Backend

| ID | Module | Status |
|----|--------|--------|
| F2.1 | apps/monitoring | Done — sensors, readings, alerts, rules, overview, seed |
| F2.2 | apps/simulation | Existing routers; Celery/PDF upgrade pending |
| F2.3 | apps/satellite | Done — provider chain + synthetic NDVI fallback; GEE/Copernicus slots ready |

## Endpoints live

- GET /api/v1/monitoring/overview
- GET/POST /api/v1/sensors
- GET/POST /api/v1/sensors/:id/readings
- GET /api/v1/alerts
- POST /api/v1/alert-rules
- GET /api/v1/satellite/availability|ndvi|timeseries|fields
- POST /api/v1/satellite/change-detection

## Frontend

- /monitoring — hub
- /satellite — NDVI map + timeseries

## Next

- Celery tasks for AquaCrop/RothC + PDF export
- WS /ws/monitoring
- Real GEE/Copernicus provider classes behind same interface
- Remaining monitoring/simulator pages
