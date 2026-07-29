# Soil models, global SA, final reports

## Soil engines
| Model | Endpoint | Output |
|-------|----------|--------|
| RothC-26.3 | `POST /api/v1/science/rothc?with_sa=true` | ΔSOC + optional global SA + `report` |
| RUSLE proxy | `POST /api/v1/science/soil/rusle` | A=R·K·LS·C·P + risk class |
| Profile | `POST /api/v1/science/soil/profile` | layers, AWC, SOC depth |

## Global sensitivity (soil)
```
GET /api/v1/science/sensitivity/rothc?n_sobol=32
GET /api/v1/science/sensitivity/rusle?n_sobol=32
```
Methods: **SRC**, **Morris (μ\*)**, **Saltelli–Sobol (S1, ST)**.

- RothC target: 15-year **ΔSOC**
- RUSLE target: **A** (t/ha/year)

## Final report schema (`result.report`)
- executive_summary_fa/en
- formulas, metrics, risks[], recommendations
- sensitivity.top_ST (when SA requested)
- disclaimer

AquaCrop / SCS responses also embed `report` via `report_builder`.
