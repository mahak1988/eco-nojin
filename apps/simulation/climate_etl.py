"""Climate data pipeline — Open-Meteo archive → model-ready series."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

logger = logging.getLogger(__name__)


def fetch_climate_series(
    lat: float,
    lon: float,
    days: int = 30,
) -> dict[str, Any]:
    """
    Pull daily temp/precip (Open-Meteo archive). Offline fallback synthetic.
    Output shaped for AquaCrop / SWAT drivers.
    """
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=max(days - 1, 0))
    try:
        import httpx

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration",
            "timezone": "auto",
        }
        with httpx.Client(timeout=30.0) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        daily = data.get("daily") or {}
        times = daily.get("time") or []
        series = []
        for i, t in enumerate(times):
            series.append(
                {
                    "date": t,
                    "temp_mean_c": (daily.get("temperature_2m_mean") or [None])[i],
                    "temp_max_c": (daily.get("temperature_2m_max") or [None])[i],
                    "temp_min_c": (daily.get("temperature_2m_min") or [None])[i],
                    "precip_mm": (daily.get("precipitation_sum") or [None])[i],
                    "et0_mm": (daily.get("et0_fao_evapotranspiration") or [None])[i],
                }
            )
        et0_vals = [float(x["et0_mm"] or 0) for x in series]
        precip_vals = [float(x["precip_mm"] or 0) for x in series]
        return {
            "source": "open-meteo-archive",
            "lat": lat,
            "lon": lon,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "series": series,
            "drivers": {
                "et0_mm_day": round(sum(et0_vals) / max(len(et0_vals), 1), 2),
                "rain_mm_day": round(sum(precip_vals) / max(len(precip_vals), 1), 2),
                "rain_mm_total": round(sum(precip_vals), 2),
                "et0_mm_year_proxy": round(sum(et0_vals) / max(len(et0_vals), 1) * 365, 1),
                "precip_mm_year_proxy": round(sum(precip_vals) / max(len(precip_vals), 1) * 365, 1),
            },
        }
    except Exception as e:
        logger.warning("climate ETL fallback: %s", e)
        series = []
        for i in range(days):
            d = start + timedelta(days=i)
            series.append(
                {
                    "date": d.isoformat(),
                    "temp_mean_c": 28.0 + (i % 7) * 0.3,
                    "temp_max_c": 35.0,
                    "temp_min_c": 20.0,
                    "precip_mm": 0.2 if i % 11 else 5.0,
                    "et0_mm": 5.0,
                }
            )
        return {
            "source": "synthetic-climate",
            "lat": lat,
            "lon": lon,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "series": series,
            "drivers": {
                "et0_mm_day": 5.0,
                "rain_mm_day": 0.6,
                "rain_mm_total": 0.6 * days,
                "et0_mm_year_proxy": 1825.0,
                "precip_mm_year_proxy": 220.0,
            },
            "error": str(e)[:120],
        }
