"""Free Earth-Observation stack — Sentinel + NASA + DEM + vegetation + erosion.

All sources are zero-cost:
  • Microsoft Planetary Computer STAC (Sentinel-1/2, Landsat, MODIS, DEM)
  • Open-Meteo (elevation, climate, soil moisture proxy)
  • Local RUSLE-lite (erosion risk from slope × cover × rain)

No paid APIs or proprietary binaries.
"""

from __future__ import annotations

import logging
import math
from datetime import date, timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

# Free collections on Planetary Computer
COLLECTIONS: dict[str, dict[str, str]] = {
    "sentinel-2-l2a": {
        "family": "ESA Sentinel",
        "use": "optical 10m — NDVI, EVI, land cover, crop monitoring",
    },
    "sentinel-1-grd": {
        "family": "ESA Sentinel",
        "use": "SAR C-band — soil moisture proxy, flood, all-weather",
    },
    "sentinel-3-olci-l2-lfr": {
        "family": "ESA Sentinel",
        "use": "ocean/land colour — vegetation, chlorophyll",
    },
    "landsat-c2-l2": {
        "family": "NASA/USGS Landsat",
        "use": "optical 30m — long archive NDVI, burn, land change",
    },
    "modis-13Q1-061": {
        "family": "NASA MODIS",
        "use": "16-day NDVI/EVI 250m — climate & drought trends",
    },
    "modis-11A1-061": {
        "family": "NASA MODIS",
        "use": "daily land surface temperature (LST)",
    },
    "modis-10A1-061": {
        "family": "NASA MODIS",
        "use": "daily snow cover",
    },
    "copernicus-dem-glo-30": {
        "family": "Copernicus DEM",
        "use": "30m elevation / slope / topography",
    },
    "nasadem": {
        "family": "NASA DEM",
        "use": "SRTM-based elevation ~30m",
    },
    "era5-pds": {
        "family": "ECMWF ERA5",
        "use": "reanalysis climate — temp, precip, wind",
    },
}


def _open_catalog():
    import pystac_client

    try:
        import planetary_computer as pc

        return pystac_client.Client.open(STAC_URL, modifier=pc.sign_inplace)
    except Exception:
        return pystac_client.Client.open(STAC_URL)


def catalog_overview() -> dict[str, Any]:
    return {
        "policy": "zero-cost EO only",
        "primary_hub": "Microsoft Planetary Computer STAC",
        "climate_hub": "Open-Meteo (no key)",
        "collections": [
            {"id": k, **v} for k, v in COLLECTIONS.items()
        ],
        "derived_products": [
            "NDVI / EVI / NDWI (Sentinel-2)",
            "VCI + anomaly drought",
            "DEM elevation + slope",
            "RUSLE-lite soil erosion risk",
            "LST climate warming signal (MODIS when available)",
            "Open-Meteo soil moisture & precipitation",
        ],
        "endpoints": {
            "catalog": "/api/v1/satellite/eo/catalog",
            "summary": "/api/v1/satellite/eo/summary?lat=&lon=",
            "vegetation": "/api/v1/satellite/eo/vegetation?lat=&lon=",
            "dem": "/api/v1/satellite/eo/dem?lat=&lon=",
            "erosion": "/api/v1/satellite/eo/erosion?lat=&lon=",
            "climate": "/api/v1/satellite/eo/climate?lat=&lon=",
            "scenes": "/api/v1/satellite/eo/scenes?lat=&lon=&collection=sentinel-2-l2a",
            "ndvi": "/api/v1/satellite/ndvi?lat=&lon=",
            "vci": "/api/v1/satellite/vci?lat=&lon=",
        },
    }


async def search_scenes(
    lat: float,
    lon: float,
    collection: str = "sentinel-2-l2a",
    days: int = 60,
    max_items: int = 12,
    cloud_max: Optional[float] = 40.0,
) -> dict[str, Any]:
    """List recent STAC items for a free collection around a point."""
    end = date.today()
    start = end - timedelta(days=days)
    delta = 0.05
    bbox = [lon - delta, lat - delta, lon + delta, lat + delta]
    meta = COLLECTIONS.get(collection, {"family": "unknown", "use": ""})
    try:
        catalog = _open_catalog()
        kwargs: dict[str, Any] = {
            "collections": [collection],
            "bbox": bbox,
            "datetime": f"{start.isoformat()}/{end.isoformat()}",
            "max_items": max_items,
        }
        if cloud_max is not None and "sentinel-2" in collection or "landsat" in collection:
            kwargs["query"] = {"eo:cloud_cover": {"lt": cloud_max}}
        search = catalog.search(**kwargs)
        items = list(search.items())
        rows = []
        for it in items:
            props = it.properties or {}
            rows.append(
                {
                    "id": it.id,
                    "date": it.datetime.date().isoformat() if it.datetime else None,
                    "cloud_cover": props.get("eo:cloud_cover"),
                    "platform": props.get("platform") or props.get("instruments"),
                    "collection": collection,
                }
            )
        return {
            "lat": lat,
            "lon": lon,
            "collection": collection,
            "family": meta.get("family"),
            "use": meta.get("use"),
            "start": start.isoformat(),
            "end": end.isoformat(),
            "count": len(rows),
            "scenes": rows,
            "provider": "microsoft-planetary-computer",
        }
    except Exception as e:
        logger.warning("STAC search %s failed: %s", collection, e)
        return {
            "lat": lat,
            "lon": lon,
            "collection": collection,
            "count": 0,
            "error": str(e)[:200],
            "scenes": [],
        }


async def multi_sensor_availability(lat: float, lon: float, days: int = 60) -> dict[str, Any]:
    """Quick scene counts for key free sensors."""
    keys = [
        "sentinel-2-l2a",
        "sentinel-1-grd",
        "landsat-c2-l2",
        "modis-13Q1-061",
        "copernicus-dem-glo-30",
    ]
    out = []
    for col in keys:
        cloud = 40.0 if "sentinel-2" in col or "landsat" in col else None
        r = await search_scenes(lat, lon, collection=col, days=days, max_items=5, cloud_max=cloud)
        out.append(
            {
                "collection": col,
                "family": r.get("family"),
                "count": r.get("count", 0),
                "error": r.get("error"),
                "sample_id": (r.get("scenes") or [{}])[0].get("id") if r.get("scenes") else None,
            }
        )
    return {"lat": lat, "lon": lon, "days": days, "sensors": out}


def _http_json(url: str, timeout: float = 20.0) -> dict[str, Any]:
    import urllib.request
    import json

    req = urllib.request.Request(url, headers={"User-Agent": "EcoNojin/2.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def open_meteo_elevation(lat: float, lon: float) -> dict[str, Any]:
    """Free elevation from Open-Meteo (SRTM-based)."""
    url = f"https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lon}"
    try:
        data = _http_json(url)
        elev = (data.get("elevation") or [None])[0]
        return {
            "lat": lat,
            "lon": lon,
            "elevation_m": elev,
            "source": "open-meteo/SRTM",
            "provider": "open-meteo",
        }
    except Exception as e:
        return {"lat": lat, "lon": lon, "elevation_m": None, "error": str(e)[:120]}


def open_meteo_climate(lat: float, lon: float, days: int = 30) -> dict[str, Any]:
    """Free climate + soil moisture proxy (Open-Meteo)."""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        "et0_fao_evapotranspiration"
        "&hourly=soil_moisture_0_to_7cm,soil_temperature_0cm"
        f"&forecast_days={min(days, 16)}"
        "&past_days=14"
        "&timezone=auto"
    )
    try:
        data = _http_json(url, timeout=25.0)
        daily = data.get("daily") or {}
        hourly = data.get("hourly") or {}
        sm = hourly.get("soil_moisture_0_to_7cm") or []
        sm_valid = [x for x in sm if x is not None]
        tmax = daily.get("temperature_2m_max") or []
        tmin = daily.get("temperature_2m_min") or []
        precip = daily.get("precipitation_sum") or []
        et0 = daily.get("et0_fao_evapotranspiration") or []
        return {
            "lat": lat,
            "lon": lon,
            "source": "open-meteo",
            "provider": "open-meteo",
            "temperature": {
                "max_c_recent": max([t for t in tmax if t is not None], default=None),
                "min_c_recent": min([t for t in tmin if t is not None], default=None),
                "mean_max_c": round(sum(t for t in tmax if t is not None) / max(len([t for t in tmax if t is not None]), 1), 2)
                if any(t is not None for t in tmax)
                else None,
            },
            "precipitation_mm_sum": round(sum(p for p in precip if p is not None), 2),
            "et0_mm_sum": round(sum(e for e in et0 if e is not None), 2),
            "soil_moisture_0_7cm_mean": round(sum(sm_valid) / len(sm_valid), 4) if sm_valid else None,
            "warming_note": "Use long MODIS LST / ERA5 for multi-decadal warming; Open-Meteo gives current window",
            "daily_dates": daily.get("time"),
            "raw_daily_keys": list(daily.keys()),
        }
    except Exception as e:
        return {"lat": lat, "lon": lon, "error": str(e)[:160], "source": "open-meteo"}


def estimate_slope_pct(lat: float, lon: float, elev_m: Optional[float]) -> float:
    """Rough slope proxy: query 4 nearby elevations (Open-Meteo)."""
    if elev_m is None:
        return 5.0  # mild default
    d = 0.01  # ~1 km
    try:
        pts = [
            open_meteo_elevation(lat + d, lon),
            open_meteo_elevation(lat - d, lon),
            open_meteo_elevation(lat, lon + d),
            open_meteo_elevation(lat, lon - d),
        ]
        elevs = [p.get("elevation_m") for p in pts if p.get("elevation_m") is not None]
        if not elevs:
            return 5.0
        diff = max(abs(e - elev_m) for e in elevs)
        # rise/run over ~1110 m
        slope_pct = min(60.0, (diff / 1110.0) * 100.0)
        return round(slope_pct, 2)
    except Exception:
        return 5.0


def rusle_lite(
    *,
    slope_pct: float,
    ndvi: float,
    rain_mm_month: float,
    soil_erodibility: float = 0.3,
) -> dict[str, Any]:
    """Simplified RUSLE-style relative erosion risk (0–100).

    A ∝ R · K · LS · C · P  (P assumed 1)
    Not a regulatory model — relative ranking for pilots.
    """
    # R factor proxy from monthly rain
    r = max(0.0, min(100.0, rain_mm_month * 0.5))
    k = max(0.05, min(0.6, soil_erodibility))
    # LS from slope %
    ls = min(20.0, 0.3 + (slope_pct / 10.0) ** 1.3)
    # C from NDVI (high vegetation → low C)
    ndvi_c = max(-0.2, min(0.95, ndvi))
    c = max(0.02, min(1.0, 1.15 - 1.2 * ndvi_c))
    p = 1.0
    a = r * k * ls * c * p
    # normalize to 0–100 risk score
    risk = max(0.0, min(100.0, a * 2.5))
    if risk < 15:
        label = "low"
    elif risk < 35:
        label = "moderate"
    elif risk < 60:
        label = "high"
    else:
        label = "severe"
    return {
        "model": "RUSLE-lite (relative)",
        "risk_score_0_100": round(risk, 1),
        "label": label,
        "factors": {
            "R_rain_proxy": round(r, 2),
            "K_soil": k,
            "LS_slope": round(ls, 2),
            "C_cover": round(c, 3),
            "P_support": p,
            "slope_pct": slope_pct,
            "ndvi": ndvi,
            "rain_mm_month_proxy": rain_mm_month,
        },
        "note": "Relative ranking for landscape pilots — not ISO/FAO formal RUSLE2 output",
    }


async def vegetation_bundle(lat: float, lon: float, days: int = 60) -> dict[str, Any]:
    """Sentinel-2 NDVI path + VCI context + Landsat/MODIS scene counts."""
    from apps.satellite.fast_ndvi import fast_timeseries

    ndvi_pack = await fast_timeseries(lat, lon, days, raster_budget=0)
    s2 = await search_scenes(lat, lon, "sentinel-2-l2a", days=days, max_items=8)
    ls = await search_scenes(lat, lon, "landsat-c2-l2", days=min(days * 2, 120), max_items=5)
    modis = await search_scenes(
        lat, lon, "modis-13Q1-061", days=min(days * 3, 180), max_items=5, cloud_max=None
    )
    return {
        "lat": lat,
        "lon": lon,
        "sentinel2_ndvi": {
            "count": ndvi_pack.get("count"),
            "mode": ndvi_pack.get("mode"),
            "provider": ndvi_pack.get("provider"),
            "latest_vci": ndvi_pack.get("latest_vci"),
            "timeseries_tail": (ndvi_pack.get("timeseries") or [])[-6:],
        },
        "scene_counts": {
            "sentinel-2-l2a": s2.get("count"),
            "landsat-c2-l2": ls.get("count"),
            "modis-13Q1-061": modis.get("count"),
        },
        "interpretation": {
            "ndvi_lt_0.2": "bare / sparse / dry season",
            "ndvi_0.2_0.5": "moderate vegetation",
            "ndvi_gt_0.5": "dense green cover",
        },
    }


async def dem_bundle(lat: float, lon: float) -> dict[str, Any]:
    elev = open_meteo_elevation(lat, lon)
    slope = estimate_slope_pct(lat, lon, elev.get("elevation_m"))
    dem_stac = await search_scenes(
        lat, lon, "copernicus-dem-glo-30", days=3650, max_items=3, cloud_max=None
    )
    return {
        "lat": lat,
        "lon": lon,
        "elevation_m": elev.get("elevation_m"),
        "slope_pct_proxy": slope,
        "elevation_source": elev.get("source"),
        "copernicus_dem_stac": {
            "count": dem_stac.get("count"),
            "sample": (dem_stac.get("scenes") or [])[:2],
            "error": dem_stac.get("error"),
        },
        "uses": ["watershed", "terrace design", "RUSLE LS factor", "flood plain"],
    }


async def erosion_bundle(lat: float, lon: float, days: int = 30) -> dict[str, Any]:
    from apps.satellite.fast_ndvi import fast_timeseries

    dem = await dem_bundle(lat, lon)
    climate = open_meteo_climate(lat, lon, days=16)
    ndvi_pack = await fast_timeseries(lat, lon, max(days, 30), raster_budget=0)
    ts = ndvi_pack.get("timeseries") or []
    ndvi = ts[-1]["mean_ndvi"] if ts else 0.25
    rain = climate.get("precipitation_mm_sum") or 20.0
    # scale to monthly-ish proxy
    rain_month = float(rain) * (30.0 / max(days, 14))
    risk = rusle_lite(
        slope_pct=float(dem.get("slope_pct_proxy") or 5.0),
        ndvi=float(ndvi),
        rain_mm_month=rain_month,
    )
    return {
        "lat": lat,
        "lon": lon,
        "elevation_m": dem.get("elevation_m"),
        "slope_pct_proxy": dem.get("slope_pct_proxy"),
        "ndvi_latest": ndvi,
        "rain_proxy_mm": round(rain_month, 1),
        "erosion": risk,
        "mitigation_hints": [
            "increase permanent cover (NDVI) → lower C factor",
            "contour / terrace on slopes > 8%",
            "mulch and residue after harvest",
            "check HP-09 watershed package in Hydroma SOPs",
        ],
    }


async def climate_bundle(lat: float, lon: float) -> dict[str, Any]:
    climate = open_meteo_climate(lat, lon)
    modis_lst = await search_scenes(
        lat, lon, "modis-11A1-061", days=30, max_items=5, cloud_max=None
    )
    era5 = await search_scenes(lat, lon, "era5-pds", days=30, max_items=3, cloud_max=None)
    return {
        "lat": lat,
        "lon": lon,
        "open_meteo": climate,
        "nasa_modis_lst_scenes": {
            "collection": "modis-11A1-061",
            "count": modis_lst.get("count"),
            "sample": (modis_lst.get("scenes") or [])[:3],
            "error": modis_lst.get("error"),
            "use": "land surface temperature / heat stress",
        },
        "era5_scenes": {
            "count": era5.get("count"),
            "error": era5.get("error"),
            "use": "long-term climate reanalysis",
        },
        "note": "For multi-decade warming trends prefer ERA5/MODIS LST archives; Open-Meteo covers operational window",
    }


async def full_summary(lat: float, lon: float) -> dict[str, Any]:
    """One-shot free EO package for a farm/pilot point."""
    veg = await vegetation_bundle(lat, lon, days=60)
    dem = await dem_bundle(lat, lon)
    eros = await erosion_bundle(lat, lon)
    clim = await climate_bundle(lat, lon)
    sensors = await multi_sensor_availability(lat, lon, days=60)
    return {
        "lat": lat,
        "lon": lon,
        "policy": "zero-cost: Planetary Computer + Open-Meteo + RUSLE-lite",
        "sensors": sensors.get("sensors"),
        "vegetation": veg,
        "topography": dem,
        "erosion": eros.get("erosion"),
        "climate": {
            "open_meteo": clim.get("open_meteo"),
            "modis_lst_count": (clim.get("nasa_modis_lst_scenes") or {}).get("count"),
        },
        "hydroma_links": {
            "cover_crops": "HP bio-fertilizer + residue → raise NDVI, cut C-factor",
            "watershed": "HP-09",
            "rangeland": "HP rangeland package",
        },
    }
