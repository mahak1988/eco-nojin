# Econojin (اکو نوژین)

**Integrated platform for smart agriculture, water, environment, green economy, and rural community.**

پلتفرم یکپارچه کشاورزی هوشمند، آب، محیط‌زیست، اقتصاد سبز و جامعه روستایی.

## Governance

- **Hard rules:** [docs/CONSTITUTION.md](docs/CONSTITUTION.md) (R1–R23)
- **Glossary fa/en:** [docs/GLOSSARY_FA_EN.md](docs/GLOSSARY_FA_EN.md)
- **Phase 1:** agricultural core (farms, crops, water, risks)
- **Phase 2 (complete):** [docs/PHASE2_COMPLETE.md](docs/PHASE2_COMPLETE.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

UI languages: **fa / en**. Code & API identifiers: **English**.

---

## Status (2026-07-27)

| Area | Status |
|------|--------|
| Phase 0 infrastructure | ✅ local SQLite + Alembic policy |
| Phase 1 agri core | ✅ farms/crops/water/auth/risks |
| Phase 2 monitoring | ✅ sensors, alerts, rules |
| Phase 2 simulation jobs | ✅ AquaCrop/RothC + PDF/CSV |
| Phase 2 satellite | ✅ 36 roles, catalog, SM/NDVI/DEM |
| WebSocket `/ws/monitoring` | ✅ |
| Celery | ✅ optional (sync fallback) |
| RS256 production keys | ⚠️ local may use HS256 settings |
| Full RBAC on every write | ⚠️ partial |

---

## Quickstart

```bash
git clone https://github.com/mahak1988/eco-nojin.git
cd eco-nojin
cp .env.example .env   # if present

pip install -r requirements.txt
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000

cd apps/web && pnpm install && pnpm dev
```

| Service | URL |
|---------|-----|
| API docs | http://localhost:8000/docs |
| Web | http://localhost:5173 |
| Health | http://localhost:8000/health |
| WS monitoring | ws://localhost:8000/ws/monitoring |

### Useful curls

```bash
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/satellite/roles
curl.exe -H "User-Agent: Mozilla/5.0" "http://localhost:8000/api/v1/satellite/soil-moisture?lat=32.65&lon=51.67"
curl.exe -X POST -H "Content-Type: application/json" -H "User-Agent: Mozilla/5.0" ^
  -d "{\"area_ha\":2,\"days\":30}" http://localhost:8000/api/v1/simulations/aquacrop
curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/monitoring/seed-demo
```

Optional Celery worker:

```bash
redis-server
celery -A apps.shared_core.celery_app.celery_app worker -l info
```

---

## Architecture

```
apps/main.py              FastAPI entry + router discovery
apps/shared_core/         config, security, database, websocket, celery
apps/monitoring/          sensors & alerts (Phase 2)
apps/satellite/           EO catalog, roles, providers (Phase 2)
apps/simulation/          AquaCrop/RothC tasks + jobs API
apps/farms|crops|water/   agri core (Phase 1)
apps/risks/               drought/flood/pest heuristics
apps/web/                 React + Vite + TypeScript
docs/                     constitution, phase reports, glossary
```

---

## Phase map

| Phase | Focus | Doc |
|-------|--------|-----|
| 0 | Infra (Alembic, RBAC seed, Docker skeleton) | PHASE0_* |
| 1 | Farms, crops, water, auth UX | PHASE1_* |
| 2 | Monitoring, simulators, satellite | [PHASE2_COMPLETE.md](docs/PHASE2_COMPLETE.md) |
| 3 | Next — community scale / MRV / production hardening | TBD |

---

## License

MIT — see [License](License).
