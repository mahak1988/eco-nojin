# Phase 3 — Technical debt (partial)

## Done in this commit

- `apps/shared_core/timeutil.py` → `utc_now()` (timezone-aware)
- Core ORM models migrated off `datetime.utcnow`:
  - farms, crops, planting, inventory, monitoring, economics
  - simulation/run_store explicit timestamps
- `pytest.ini` is single source of truth; removed `[tool.pytest.ini_options]` from `pyproject.toml`
- filterwarnings for residual DeprecationWarning / Starlette noise

## Remaining (follow-up)

Still using `datetime.utcnow` in some modules (admin_panel, community, education, library, games, simulation scenario/runs, schemas, scripts). Migrate with same pattern:

```python
from apps.shared_core.timeutil import utc_now
# default=utc_now  or  created_at=utc_now()
```

Starlette `HTTP_*` deprecations come from framework/deps; suppress until upstream upgrades.
