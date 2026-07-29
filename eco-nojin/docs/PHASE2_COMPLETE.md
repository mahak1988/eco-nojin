# Phase 2 — Complete report

**Date:** 2026-07-27  
**Scope:** Scientific monitoring, simulation jobs, satellite EO/GIS

## Checklist (Section 5)

### Backend

| ID | Item | Status |
|----|------|--------|
| F2.1 | monitoring sensors/readings/alerts/rules | ✅ |
| F2.2 | AquaCrop/RothC Celery + CSV/PDF | ✅ (sync fallback) |
| F2.2 | compare endpoint | ✅ `POST /simulations/compare` |
| F2.3 | satellite catalog + roles (36) | ✅ |
| F2.3 | NDVI / topography / thermal / soil moisture | ✅ |
| WS | `/ws/monitoring` | ✅ |

### Frontend (17 pages target)

| Group | Routes | Status |
|-------|--------|--------|
| Monitoring ×6 | `/monitoring`, `/soil`, `/weather`, `/map`, `/alerts`, `/rules` | ✅ |
| Simulators ×7 | hub (existing), aquacrop, rothc, my-simulations, comparison, detail | ✅ core |
| Satellite ×4 | dashboard, timeseries, change, fields | ✅ |

### Known limitations (next phase)

- Full calibrated AquaCrop/RothC engines (current = transparent stubs)
- Redis required only for true async Celery queue
- Live GEE/Copernicus STAC needs optional credentials for production bulk
- Lighthouse / contract tests for all Phase-2 endpoints still incremental

## Acceptance mapping

| Criterion | Evidence |
|-----------|----------|
| AquaCrop runs + PDF path | `POST /api/v1/simulations/aquacrop` → `export_pdf` |
| NDVI on map flow | `/satellite` + Leaflet + `/ndvi` |
| Sensor → alert | seed-demo + push reading + rules |
| Free provider fallback | synthetic + Open-Meteo + OpenTopoData |

## Terminology

See [GLOSSARY_FA_EN.md](./GLOSSARY_FA_EN.md).
