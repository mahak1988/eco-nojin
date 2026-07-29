# Econojin ML (Classical)

## Models
| Model | Algorithm | Target |
|-------|-----------|--------|
| Yield | Ridge linear regression | relative yield 0–1 |
| Risk | Multiclass logistic (OVR) | low / medium / high |
| Anomaly | Z-score | feature outlier |

## Engine
Pure Python (`apps/ml/classical.py`) — **no sklearn required**.

Trained on physics-inspired **synthetic** samples (`apps/ml/synthetic_data.py`).
Artifacts: `data/ml_models.json`.

## API
- `GET /api/v1/ml/status`
- `POST /api/v1/ml/train?n_samples=1000`
- `POST /api/v1/ml/predict`
- `POST /api/v1/ml/predict-from-watch?lat=&lon=&days=`
- `GET /api/v1/ml/features`

## Honesty
Not a deep-learning production model. Retrain with real farm labels before operational decisions.
