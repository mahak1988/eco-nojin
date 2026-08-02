# Phase 7 — Free runtime stack & monitoring

## Runtime

- API: FastAPI + SQLite (local) or Neon Postgres (cloud free)
- Science: conceptual models always; OSPy/pyRothC optional
- Satellite: Planetary Computer → synthetic
- Weather: Open-Meteo (no key)

## Health

`GET /health` reports:

- database ok/fail
- security toggles
- loaded routers (incl. `science_e2e`)

## Monitoring (free)

| Tool | Use |
|------|-----|
| Sentry free tier | Optional `SENTRY_DSN` |
| Platform logs | Render/Fly logs |
| `/health` + uptime robot | UptimeRobot free |

## Local smoke

```powershell
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/v1/science/status
curl http://127.0.0.1:8000/api/v1/science/e2e-mrv/isfahan-wheat
```
