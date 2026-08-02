# Free Science Stack (Phase 1 + Phase 2)

**Cost:** zero. All engines and EO paths are free/open-source.

## Phase 1 — Optional pure-Python models

| Engine | Package | How to enable | Fallback |
|--------|---------|---------------|----------|
| AquaCrop-OSPy | `pip install aquacrop` | `engine=ospy` or `engine=free` in params | `aquacrop_advanced` (conceptual) |
| pyRothC | `pip install pyRothC` | `engine=pyrothc` or `engine=free` | `rothc_model` (in-repo RothC-26.3) |

Default path (no `engine` / `engine=conceptual`) is unchanged → existing tests stay green.

### Code entry points

- `apps/simulation/aquacrop_ospy_engine.py` → `run_aquacrop_with_optional_ospy`
- `apps/simulation/rothc_pyrothc_engine.py` → `run_rothc_with_optional_pyrothc`
- `apps/simulation/tasks.py` routes Celery + local runs through the optional engines

## Phase 2 — Free EO (Planetary Computer first)

| Provider | Role | Cost |
|----------|------|------|
| **Microsoft Planetary Computer** | Primary NDVI (STAC Sentinel-2 L2A) | Free |
| Google Earth Engine | Secondary (needs service account) | Free research tier / keys |
| Synthetic | Always-on fallback | Free |
| Copernicus | Catalogue / availability | Free registration |

### Order in `SatelliteService`

1. Redis cache (if configured)
2. **Planetary Computer** (free)
3. GEE (if available)
4. Synthetic

### Planetary modes

- **raster** — when `planetary-computer` + `rioxarray` + `rasterio` installed: real B04/B08 NDVI on clipped COGs
- **metadata** — STAC-only cloud-weighted NDVI estimate (no heavy download); still free and usable for chains

Provider string in results: `microsoft-planetary-computer:raster` or `...:metadata`.

### Install (local)

```bash
pip install aquacrop pyRothC planetary-computer pystac-client rioxarray rasterio
```

### Weather (already free)

Open-Meteo (no API key) in `apps/weather/era5_chirps.py`.

### Disclaimer

AquaCrop-OSPy is **not** the official FAO AquaCrop binary. Conceptual and OSPy paths are for decision support. Document engine/provider name in API responses.
