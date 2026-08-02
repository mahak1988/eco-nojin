# Free Science Stack (Phase 1)

**Cost:** zero. All engines and EO paths are free/open-source.

## Optional pure-Python models

| Engine | Package | How to enable | Fallback |
|--------|---------|---------------|----------|
| AquaCrop-OSPy | `pip install aquacrop` | `engine=ospy` or `engine=free` in params | `aquacrop_advanced` (conceptual) |
| pyRothC | `pip install pyRothC` | `engine=pyrothc` or `engine=free` | `rothc_model` (in-repo RothC-26.3) |

Default path (no `engine` / `engine=conceptual`) is unchanged → existing tests stay green.

### Code entry points

- `apps/simulation/aquacrop_ospy_engine.py` → `run_aquacrop_with_optional_ospy`
- `apps/simulation/rothc_pyrothc_engine.py` → `run_rothc_with_optional_pyrothc`
- `apps/simulation/tasks.py` routes Celery + local runs through the optional engines

### Install (local)

```bash
pip install aquacrop pyRothC planetary-computer pystac-client rioxarray rasterio
```

### Satellite (already in repo)

- `apps/satellite/providers/planetary_provider.py` — Microsoft Planetary Computer STAC (free)
- `copernicus_provider.py`, `synthetic.py` — fallbacks
- Weather: Open-Meteo (free, no API key) in `apps/weather/era5_chirps.py`

### Disclaimer

AquaCrop-OSPy is **not** the official FAO AquaCrop binary. Conceptual and OSPy paths are for decision support. Document engine name in API responses (`engine`, `model`, `disclaimer`).
