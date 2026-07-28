# Phase 3 — Wave 2 Complete

**Date:** 2026-07-28

## Delivered

| # | Item | Implementation |
|---|------|----------------|
| 1 | Persist runs | `simulation_runs` ORM + `save_run_async` / `save_run_sync` + `GET /api/v1/science/runs` |
| 2 | Celery heavy models | `science.run_aquacrop_advanced`, `science.run_swat` — `async_mode: true` on POST bodies |
| 3 | NDVI → canopy | `GET /api/v1/science/ndvi-canopy` + `use_ndvi_canopy` on AquaCrop + pipeline |
| 4 | PostGIS farm index | `farms.geom` + GIST; `POST /api/v1/farms/spatial/ensure-index`; startup `ensure_farms_spatial` |

## Verify (SQLite ok for 1–3)

```powershell
git pull origin main
pytest tests/unit/test_wave2.py tests/unit/test_phase3_models.py -q
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000

curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" `
  -d "{\"days\":20,\"persist\":true}" http://localhost:8000/api/v1/science/aquacrop-advanced

curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/science/runs

curl.exe -H "User-Agent: Mozilla/5.0" `
  "http://localhost:8000/api/v1/science/ndvi-canopy?lat=32.65&lon=51.67&days=60"

curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" `
  -d "{\"lat\":32.65,\"lon\":51.67,\"days\":30,\"use_ndvi_canopy\":true}" `
  http://localhost:8000/api/v1/science/aquacrop-advanced
```

## Celery (optional Redis)

```powershell
# terminal 1
celery -A apps.shared_core.celery_app.celery_app worker -l info
# terminal 2 — queue job
curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" `
  -d "{\"days\":30,\"async_mode\":true}" http://localhost:8000/api/v1/science/aquacrop-advanced
```

## Postgres spatial

```powershell
$env:FORCE_POSTGRES="1"
$env:DATABASE_URL="postgresql+asyncpg://econojin:econojin@127.0.0.1:5432/econojin"
alembic upgrade head
curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/farms/spatial/ensure-index
curl.exe -H "User-Agent: Mozilla/5.0" "http://localhost:8000/api/v1/farms/spatial/nearby?lat=32.65&lon=51.67&radius_m=50000"
```

On SQLite, `ensure-index` returns `{"ok": false, "reason": "not_postgres"}` — expected.
