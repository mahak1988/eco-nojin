# Remaining work (honest backlog)

Updated: 2026-07-28

## Done in repo (code)

- [x] Science API mount: `apps/api/routes/science.py`
- [x] AquaCrop conceptual + RothC-26.3 + SCS-CN (not FAO/SWAT binaries)
- [x] NDVI→canopy bridge, simulation_runs model, Wave2 docs
- [x] FE `/science` page wired to science API
- [x] Unit/contract tests for formulas + router import

## Blocked on your machine / credentials

| Item | Why |
|------|-----|
| Docker + PostGIS | Docker not installed on user Windows host |
| Real GEE NDVI | Needs Google Earth Engine service account |
| RS256 in production | Needs openssl key pair + env |
| measured coverage % | Run `pytest --cov` locally |
| Locust p95 | Run load test against deployed API |
| Official AquaCrop/SWAT+ binaries | External install + licensing |

## Next engineering priorities

1. Confirm `science_loaded: true` after `git pull` + uvicorn restart
2. Install Docker Desktop → `docker compose up` postgres/redis
3. GEE service account → `docs/GEE_SETUP.md`
4. Wire remaining FE pages that still use static mock where API exists
5. Full RBAC audit on every POST when `REQUIRE_AUTH_FOR_WRITES=true`
