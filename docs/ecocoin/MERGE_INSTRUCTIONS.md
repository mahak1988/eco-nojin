# EcoCoin Phase 0–3 — Merge into local project

**Branch:** `feature/ecocoin-p0-p3`  
**Date:** 2026-07-31

## What was added (isolated, non-breaking)

| Path | Content |
|------|--------|
| `docs/ecocoin/*` | SSOT: monetary, allocation, impact L1–L4, contracts, deployment, plan, phase progress |
| `alembic/versions/20260731_0001_eco_core_tables.py` | eco_treasury_buckets, claims, mint_events, balances, idempotency |
| `alembic/versions/20260731_0002_eco_impact_tables.py` | evidence, peer_votes, verifiers, cap_ledger |
| `ecocoin/apps/api/*` | Models, schemas, services, routes (claims/reward/treasury/impact) |
| `contracts/foundry/*` | EcoCoin, BucketTreasury, ImpactClaimRegistry, ImpactRewardEngine + Foundry tests |
| `tests/ecocoin/*` | Unit + integration tests |

Existing `apps/api/routes/ecocoin.py` (mock wallet/staking) is **not overwritten**.

## Local pull

```powershell
cd D:\econojin.com
git fetch origin
git checkout feature/ecocoin-p0-p3
# or merge into main after review:
git checkout main
git pull origin main
git merge origin/feature/ecocoin-p0-p3
```

## Wire routers (optional)

```python
# PYTHONPATH must include repo root and ecocoin package parent
from ecocoin.apps.api.routes.ecocoin import router as eco_ledger_router, get_db
from ecocoin.apps.api.routes.ecocoin_impact import router as eco_impact_router
app.dependency_overrides[get_db] = get_async_session
app.include_router(eco_ledger_router, prefix="/api/v1")
app.include_router(eco_impact_router, prefix="/api/v1")
```

Or copy modules under `apps/api/` when ready to replace mock paths.

## Tests

```bash
pip install pytest pytest-asyncio aiosqlite sqlalchemy pydantic
PYTHONPATH=ecocoin:. pytest tests/ecocoin -q
```

## Next

Phase 4: wallet UI, oracle worker, transparency dashboard — after local merge verified.
