# EO + Weather modules

## Satellite (Sentinel-2 indices)

| Index | Formula | Bands |
|-------|---------|-------|
| NDVI | (NIR−Red)/(NIR+Red) | B08, B04 |
| NDWI | (Green−NIR)/(Green+NIR) | B03, B08 |
| NDMI | (NIR−SWIR)/(NIR+SWIR) | B08, B11 |
| SMI | composite moisture [0–1] | NDVI+NDWI+LST proxy |

**Endpoints**
- `GET /api/v1/satellite/indices?lat=&lon=&days=&persist=true`
- `GET /api/v1/satellite/timeseries`
- `GET /api/v1/satellite/spatial/nearby`
- `POST /api/v1/satellite/indices/refresh` (RBAC `satellite:write`)

**Cache:** table `satellite_index_cache` (WKT + lat/lon). On Postgres use PostGIS `ST_DWithin`.

**Providers:** Planetary Computer STAC (optional deps) → synthetic S2 curves.

```bash
pip install pystac-client planetary-computer  # optional live STAC
```

## Weather (ERA5 / CHIRPS-like)

Open-Meteo archive (no key):
- `GET /api/v1/weather/era5`
- `GET /api/v1/weather/chirps`
- `GET /api/v1/weather/alerts` — frost / flood / drought
- `GET /api/v1/weather/climate` — bundle

True CHIRPS grids can replace precip via GEE when credentials exist.

## Spatial

- `GET /api/v1/farms/spatial/nearby?lat=&lon=&radius_m=`
- PostGIS extension: `ensure_postgis(engine)` on Postgres startup

## Tests

```bash
pytest tests/unit/test_indices.py tests/unit/test_weather_alerts.py tests/unit/test_sentinel_fetcher.py -q
```
