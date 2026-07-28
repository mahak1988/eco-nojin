# Scientific formulas in Econojin (open implementations)

**Important:** These are process models using published equations. They are **not** the proprietary/binary FAO AquaCrop or USDA SWAT+ software packages.

| Component | Equations | Reference |
|-----------|-----------|-----------|
| ET0 Hargreaves–Samani | `ET0 = 0.0023·Ra·(Tmean+17.8)·√(Tmax-Tmin)` | Hargreaves & Samani 1985 |
| ET0 FAO-56 PM | Standard daily Penman–Monteith | Allen et al. FAO-56 |
| Crop ETc | `ETc = Kc·ET0` | FAO-56 |
| Water stress Ks | Linear below RAW | FAO AquaCrop concept |
| Yield response | `Y/Yx = 1 − Ky(1 − Ta/Tc)` | FAO-33 |
| SCS-CN runoff | `Q=(P−0.2S)²/(P+0.8S)`, `S=25.4(1000/CN−10)` | NRCS |
| RothC pools | DPM,RPM,BIO,HUM,IOM + a,b,c modifiers | Coleman & Jenkinson |
| NDVI | `(NIR−Red)/(NIR+Red)` | Rouse et al. |
| NDWI | `(Green−NIR)/(Green+NIR)` | McFeeters |

## Live vs estimated inputs

- Climate: Open-Meteo archive when network available; else documented synthetic climate for offline tests
- NDVI: GEE/MPC when credentials exist; else synthetic series only for offline UX
- Yield bases: literature attainable yields, not farm-measured until user data linked
