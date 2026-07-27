# Google Earth Engine — live setup

## Steps

1. Create a Google Cloud project and enable Earth Engine API.
2. Create a **service account**, download JSON key → `secrets/gee-sa.json`.
3. Register the service account email in [Earth Engine](https://code.earthengine.google.com/) (Assets → users).
4. Apply for higher quota / Partner if needed (agri/climate narrative).

## Env

```
GEE_SERVICE_ACCOUNT=sa@project.iam.gserviceaccount.com
GEE_CREDENTIALS_FILE=secrets/gee-sa.json   # or /secrets/gee-sa.json in Docker
GEE_PROJECT_ID=your-gcp-project-id
```

## Python

```bash
pip install earthengine-api
```

## Verify

```bash
curl "http://localhost:8000/api/v1/satellite/availability?lat=32.65&lon=51.67"
# expect provider google-earth-engine with counts when initialized

curl "http://localhost:8000/api/v1/satellite/timeseries?lat=32.65&lon=51.67"
# provider field should become google-earth-engine when GEE succeeds
```

Without credentials the chain falls back to **synthetic** (dev-safe).
