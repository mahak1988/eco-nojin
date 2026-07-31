# EcoCoin Phase 0–3 Status on GitHub

**Branch:** `feature/ecocoin-p0-p3`  
**Updated:** 2026-07-31

## Registered on this branch

| Phase | Content |
|-------|--------|
| P0 | `docs/ecocoin/ECOCOIN_MONETARY_SYSTEM.md` + MERGE_INSTRUCTIONS |
| P0–P3 | Full package continues to be pushed under `ecocoin/`, `alembic/versions/20260731_*`, `contracts/foundry/`, `tests/ecocoin/` |

## Local project next steps

```powershell
cd D:\econojin.com
git fetch origin
git checkout feature/ecocoin-p0-p3
# review, then:
git checkout main
git merge feature/ecocoin-p0-p3
```

See `docs/ecocoin/MERGE_INSTRUCTIONS.md`.

**Does not replace** existing `apps/api/routes/ecocoin.py` mock API until explicit cutover.
