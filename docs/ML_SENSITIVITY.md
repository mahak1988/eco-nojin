# ML Sensitivity Analysis

## Methods
| Method | Description |
|--------|-------------|
| **Coefficient importance** | \|β\| on standardized features (linear yield / logistic risk) |
| **OAT** | One-at-a-time ±rel_step (default 10%); elasticity and ΔP(high) |
| **Tornado** | Rank features by \|Δ yield\| and \|Δ P(high)\| |
| **Partial dependence** | 1D sweep of top features over operational range |

## API
```
GET  /api/v1/ml/sensitivity?rel_step=0.1
POST /api/v1/ml/sensitivity   # body: baseline, rel_step, pd_features, pd_points
GET  /api/v1/ml/sensitivity/oat
GET  /api/v1/ml/sensitivity/coefficients
GET  /api/v1/ml/sensitivity/partial?feature=mean_ndvi&points=12
```

## Code
- `apps/ml/sensitivity.py`
- UI: `ScienceSensitivityPanel` on `/science`

## Interpretation
- Positive elasticity: feature increase → yield increase
- Tornado length: relative local influence around baseline
- Not global Sobol indices (would need more samples); OAT is local
