# Phase 5 — E2E free science + MRV

## Chain

```
NDVI (Planetary → synthetic)
  → canopy cover
  → AquaCrop (conceptual | optional OSPy)
  → RothC (in-repo | optional pyRothC)
  → MRV L1/L2/L3 (mrv_standards)
  → issuable EcoCoin preview
```

**Cost:** zero.

## API

| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/v1/science/e2e-mrv` | Full pipeline |
| GET | `/api/v1/science/e2e-mrv/isfahan-wheat` | Preset گندم اصفهان |

Body example:

```json
{
  "crop": "wheat",
  "lat": 32.65,
  "lon": 51.67,
  "days": 90,
  "engine": "conceptual",
  "use_live_ndvi": false,
  "field_yield_t_ha": 4.0
}
```

`engine=free|ospy|pyrothc` enables optional pure-Python packages when installed.

## Code

- `apps/simulation/science_pipeline_e2e.py`
- Tests: `apps/api/tests/test_science_pipeline_e2e.py`
