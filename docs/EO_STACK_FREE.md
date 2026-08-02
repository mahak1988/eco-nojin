# Free EO Stack — EcoNojin / Hydroma

Zero-cost Earth Observation.

## Sources

| Domain | Source | Cost |
|--------|--------|------|
| Optical 10m NDVI | Sentinel-2 L2A (Planetary Computer) | Free |
| SAR | Sentinel-1 GRD STAC | Free |
| Long archive | Landsat C2 L2 | Free |
| Climate NDVI/LST | NASA MODIS STAC | Free |
| Elevation/slope | Open-Meteo + Copernicus DEM | Free |
| Weather/soil moisture | Open-Meteo | Free |
| Erosion risk | RUSLE-lite local | Free |

## Endpoints

```
GET /api/v1/satellite/eo/catalog
GET /api/v1/satellite/eo/sensors?lat=&lon=
GET /api/v1/satellite/eo/scenes?lat=&lon=&collection=sentinel-2-l2a
GET /api/v1/satellite/eo/vegetation?lat=&lon=
GET /api/v1/satellite/eo/dem?lat=&lon=
GET /api/v1/satellite/eo/erosion?lat=&lon=
GET /api/v1/satellite/eo/climate?lat=&lon=
GET /api/v1/satellite/eo/summary?lat=&lon=
GET /api/v1/satellite/ndvi
GET /api/v1/satellite/vci
```

Collections: sentinel-2-l2a, sentinel-1-grd, landsat-c2-l2, modis-13Q1-061, modis-11A1-061, copernicus-dem-glo-30, nasadem, era5-pds.

RUSLE-lite is a relative pilot ranking score, not a formal RUSLE2 certificate.
