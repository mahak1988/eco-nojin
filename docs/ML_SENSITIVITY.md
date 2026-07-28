# ML Sensitivity Analysis

## Local methods
| Method | Description |
|--------|-------------|
| Coefficient importance | \|β\| standardized |
| OAT | ±rel_step; elasticity |
| Tornado | rank \|Δy\| |
| Partial dependence | 1D sweep |

## Global methods
| Method | Description | Cost |
|--------|-------------|------|
| **SRC** | Standardized regression coefficients (global linear slopes) | O(N·d) |
| **Morris** | Elementary effects μ*, σ | O(r·(d+1)) |
| **Saltelli–Sobol** | S1 (first-order), ST (total-order) | O(N·(d+2)) |

### Interpretation
- **S1**: variance explained by Xi alone  
- **ST**: total contribution including interactions  
- **ST − S1**: interaction share  
- **μ* high, σ low**: linear influential factor  
- **μ* high, σ high**: nonlinear / interactions  
- **Low SRC R²**: response not linear → trust Sobol more than SRC  

N small (default 48–64) is noisy; production: N≥512 or SALib.

## API
```
GET  /api/v1/ml/sensitivity?rel_step=0.1
GET  /api/v1/ml/sensitivity/global?n_sobol=48&target=yield
GET  /api/v1/ml/sensitivity/sobol?n_base=48
GET  /api/v1/ml/sensitivity/morris?n_trajectories=16
GET  /api/v1/ml/sensitivity/src?n_samples=180
```

## Code
- Local: `apps/ml/sensitivity.py`
- Global: `apps/ml/global_sensitivity.py`
- Tests: `tests/unit/test_global_sensitivity.py`
