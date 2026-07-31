# Pull EcoCoin P0–P3 into local Windows project

```powershell
cd D:\econojin.com
git fetch origin
git checkout feature/ecocoin-p0-p3
git pull origin feature/ecocoin-p0-p3
```

Or merge to main after review:

```powershell
git checkout main
git pull origin main
git merge origin/feature/ecocoin-p0-p3
```

## Branch contents (non-breaking)

- `docs/ecocoin/*` — SSOT and phase reports
- `contracts/foundry/*` — new Foundry stack (existing Hardhat under `contracts/contracts/` kept)
- `ecocoin/apps/api/*` — package with ledger models/routes (existing `apps/api/routes/ecocoin.py` unchanged)
- `alembic/versions/20260731_0001*` / `0002*` — when present

Full source also remains in development artifacts until all batches are on the branch.

## After pull

1. Review `docs/ecocoin/MERGE_INSTRUCTIONS.md`
2. Run migrations if Alembic files present
3. Confirm health: `curl.exe -H "User-Agent: Mozilla/5.0" http://127.0.0.1:8000/health`
4. Start Phase 4 only after local smoke test
