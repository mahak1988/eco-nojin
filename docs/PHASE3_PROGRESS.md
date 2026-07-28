# Phase 3 Progress

**Date:** 2026-07-28

## Done (Wave 1)

- Postgres opt-in via FORCE_POSTGRES + asyncpg URL normalization
- Science API namespace `/api/v1/science/*`
- SWAT+ hydrology proxy, advanced AquaCrop, scenarios, climate ETL
- GEE status endpoint
- Alembic 20260728_0003

## Blocked on user environment

- Docker not installed on previous machine → use local Postgres or install Docker Desktop
- GEE requires Google Cloud service account JSON

## Next

Wave 2: persist runs, Celery heavy jobs, NDVI calibration path end-to-end
