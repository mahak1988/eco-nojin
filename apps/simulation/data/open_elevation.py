"""
Open-Elevation API client (no API key).
Returns ground elevation (m) for coordinates. Useful for lapse-rate temperature
correction and RUSLE LS factor. Docs: https://open-elevation.com/
"""
import asyncio
import json
import urllib.request


async def get_elevation(lat: float, lon: float) -> float | None:
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"

    def _fetch():
        req = urllib.request.Request(url, headers={"User-Agent": "EcoNojin/2.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())

    try:
        data = await asyncio.to_thread(_fetch)
        results = data.get("results", [])
        if results:
            return float(results[0].get("elevation", 0))
    except Exception:
        pass
    return None
