# Satellite module (Section 6)

## Architecture

```
apps/satellite/
  providers/base.py          BBox, NDVIResult, abstract API
  providers/gee_provider.py  Google Earth Engine (optional creds)
  providers/copernicus_provider.py  CDSE OData catalogue
  providers/planetary_provider.py   MPC STAC (optional pystac-client)
  providers/synthetic.py     offline fallback
  service.py                 cache → GEE → MPC → synthetic
  processors/                NDVI + change rules
  tasks.py                   Celery change detection + weekly check
  aquacrop_bridge.py         NDVI → canopy cover → AquaCrop
  router.py                  HTTP API
  catalog.py                 free sources + 36 roles
```

## Fallback order

1. Redis cache (if `REDIS_URL`)
2. GEE — needs `GEE_SERVICE_ACCOUNT`, `GEE_CREDENTIALS_FILE`, `GEE_PROJECT_ID` + `earthengine-api`
3. Planetary Computer — needs `pystac-client` (pip)
4. Synthetic — always

Copernicus username/password enable **catalogue** queries (`COPERNICUS_USERNAME` / `COPERNICUS_PASSWORD`).

## Env keys

```
GEE_SERVICE_ACCOUNT=
GEE_CREDENTIALS_FILE=
GEE_PROJECT_ID=
COPERNICUS_USERNAME=
COPERNICUS_PASSWORD=
REDIS_URL=redis://localhost:6379/0
```

## API

- Existing point API: `/api/v1/satellite/ndvi|timeseries|soil-moisture|catalog`
- Service-level change: `POST /api/v1/satellite/change-detection`
- Availability multi-provider: `GET /api/v1/satellite/availability`

## AquaCrop bridge

`apps/satellite/aquacrop_bridge.run_aquacrop_with_satellite` maps NDVI series to canopy cover and runs the local AquaCrop stub with calibration metadata.

## Cost note

Partner Tier GEE + CDSE + MPC keep bulk analysis near $0 for agri/climate use; Sentinel Hub WMS is optional for map tiles.
