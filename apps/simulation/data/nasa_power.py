"""
NASA POWER API Client — Fetches real-world historical weather data.
Docs: https://power.larc.nasa.gov/docs/
"""
import httpx
from typing import Optional

async def fetch_nasa_power_data(lat: float, lon: float, start_date: str, end_date: str) -> dict:
    """
    Fetches daily temperature and precipitation data.
    Note: For production, add your API key or handle rate limits.
    """
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "T2M,PRECTOTCORR",  # Temperature at 2m, Corrected Precipitation
        "community": "RE",
        "format": "JSON",
        "start": start_date,
        "end": end_date,
        "latitude": lat,
        "longitude": lon,
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract and format the time series
            timeseries = data.get("properties", {}).get("parameter", {})
            return {
                "source": "NASA POWER",
                "lat": lat,
                "lon": lon,
                "temp_c": timeseries.get("T2M", {}),
                "precip_mm": timeseries.get("PRECTOTCORR", {}),
                "status": "success"
            }
    except Exception as e:
        return {"source": "NASA POWER", "status": "error", "message": str(e)}
