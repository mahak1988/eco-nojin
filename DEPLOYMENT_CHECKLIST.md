# 🚀 Econojin Deployment Checklist — v2.0

## ⚠️ Pre-deployment Gate
- [ ] `ENVIRONMENT=production` set in .env
- [ ] `SECRET_KEY` ≥32 random chars
- [ ] All `SERVICE_TOKEN_*` filled
- [ ] `DEBUG=False`
- [ ] `git remote -v` = mahak1988/eco-nojin

---

## 1. Security
- [ ] scenario/router: `Depends(get_current_user)`
- [ ] runs/router: `user_id==current_user["id"]`
- [ ] `.bandit` skips=[] (no exceptions)
- [ ] config.py: LLM_PROVIDER includes "xai"
- [ ] No endpoint takes user_id from body
- [ ] Rate limiting active (5 failures → lockout)
- [ ] CORS restricted to production domain

## 2. Backend
- [ ] `pip install -r requirements.txt`
- [ ] `pip install -r requirements-scientific.txt`
- [ ] `torch>=2.0` installed (for PINN)
- [ ] `aquacrop>=3.0` installed
- [ ] `celery -A apps.shared_core.celery_app.celery_app worker`
- [ ] Redis connected
- [ ] PostgreSQL + PostGIS 15 running
- [ ] `docker-compose.prod.yml` celery path correct
- [ ] `openssl rand -hex 32` → SECRET_KEY

## 3. Database
- [ ] `alembic upgrade head`
- [ ] Tables: users, simulation_runs, scenarios, comparison_sessions, model_chains
- [ ] user_id column: Integer + ForeignKey

## 4. Smart Contract
- [ ] `cd contracts && npm install`
- [ ] `@openzeppelin/contracts` v5 installed
- [ ] `npx hardhat compile` — no errors
- [ ] `npx hardhat test` — all 10 pass
- [ ] `npx hardhat run scripts/deploy.ts --network polygon`
- [ ] Contract verified on Polygonscan
- [ ] `GENESIS_SUPPLY = 50_000_000e18` confirmed
- [ ] TREASURY_ADDRESS set
- [ ] `slither contracts/` — no critical/high
- [ ] ⛔ Legal consultation before exchange listing

## 5. Scientific Models
- [ ] AquaCrop official connected to ERA5/CHIRPS
- [ ] RothC 5-pool Rothamsted formulas correct
- [ ] `model_fidelity_badges.py` covers all 22 models
- [ ] Fidelity badge in all API responses
- [ ] UQ output always range (ci_95), not single number
- [ ] vm0042 registered as fidelity="official"

## 6. Data Sources
- [ ] GEE → Copernicus CDSE migration complete
- [ ] `copernicus_datasource.py` OAuth2 token valid
- [ ] ERA5 Land: `earth_engine/era5_land.py` (CDS API)
- [ ] CHIRPS: `earth_engine/chirps.py` (HTTP)
- [ ] Sentinel-2: Copernicus CDSE / Sentinel Hub
- [ ] Sentinel-1: SAR via CDSE
- [ ] ⚠️ GEE no longer free for commercial use (Apr 2026)

## 7. Frontend
- [ ] `cd apps/web && npm install && npm run build` — no errors
- [ ] i18next loads fa.json + en.json
- [ ] RTL: dir="rtl" on <html> when locale='fa'
- [ ] Vazirmatn font from CDN
- [ ] ModelFidelityBadge + UncertaintyRange visible
- [ ] LanguageSwitcher 🇮🇷/🇬🇧 functional
- [ ] API base URL → production backend

## 8. AI Agents
- [ ] ClimateAgent + AgronomyAgent active (Ollama)
- [ ] `AgentFactory.list_available()` includes climate/agronomy
- [ ] RAG: VM0042, ISO 14064-2, FAO-56

## 9. Admin Panel
- [ ] simulator_health.py dashboard
- [ ] `get_all_health()` returns 22 models
- [ ] AuditLog + toggle_model working

## 10. Infrastructure
- [ ] Liara: 4 apps (Backend/Frontend/Admin/CMS) + PostgreSQL + Redis + Storage
- [ ] ArvanCloud CDN (free 20GB) + WAF optional
- [ ] DNS: domain → Arvan → Liara
- [ ] SSL via Arvan CDN
- [ ] Docker: `docker-compose.prod.yml` tested
- [ ] Mosquitto removed or documented

## 11. Integration Tests
- [ ] `pytest apps/simulation/hydrology/tests/ -v` (4 files)
- [ ] `pytest apps/simulation/validation/tests/ -v` (1 file)
- [ ] `npx hardhat test` (10 tests)
- [ ] `curl /health` → 200
- [ ] `curl /api/v1/science/status` → model list
- [ ] `curl -X POST /api/v1/auth/login` → JWT token
- [ ] `curl -H "Authorization: Bearer <token>" /api/v1/simulation/scenarios` → user scenarios
- [ ] Frontend: 12 routes navigable

## 12. Legal (pre-launch)
- [ ] ⛔ Crypto advertising banned in Iran (Feb 2025)
- [ ] ⛔ P2P crypto payments restricted
- [ ] ⛔ Treasury token sale = securities risk
- [ ] ⛔ Iranian founder KYC ≠ offshore company sufficient
- [ ] International fintech/crypto lawyer consulted

---

## 🚦 Go/No-Go Matrix

| Gate | Criteria | Status |
|------|----------|--------|
| Security | Zero Trust + no IDOR | ⬜ |
| Contract | 10 tests + Slither clean | ⬜ |
| Backend | Celery + DB + Redis | ⬜ |
| Models | AquaCrop/RothC/UQ valid | ⬜ |
| Data | Copernicus CDSE token | ⬜ |
| Frontend | Build + i18n works | ⬜ |
| Legal | Lawyer consulted | ⬜ |

**ALL GATES ✅ BEFORE PRODUCTION**
