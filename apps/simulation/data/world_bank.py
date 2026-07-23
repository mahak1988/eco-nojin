"""
World Bank Open Data API client (no API key).
Agricultural/economic indicators for calibration & comparison.
Docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
"""
import asyncio
import json
import urllib.request

BASE = "https://api.worldbank.org/v2"

INDICATORS = {
    "AG.YLD.CREL.KG": "cereal_yield_kg_ha",
    "AG.LND.ARBL.HA": "arable_land_ha",
    "AG.LND.AGRI.ZS": "agricultural_land_pct",
    "AG.LND.FRST.ZS": "forest_area_pct",
    "AG.H2O.FWAG.ZS": "water_withdrawal_agri_pct",
}


async def get_indicators(country_code: str, year_from: int = 2010, year_to: int = 2023) -> dict:
    """Fetch agricultural indicators for a country (ISO2/ISO3 code)."""
    out = {}
    for code, friendly in INDICATORS.items():
        url = f"{BASE}/country/{country_code}/indicator/{code}?format=json&date={year_from}:{year_to}&per_page=50"

        def _fetch(u=url):
            req = urllib.request.Request(u, headers={"User-Agent": "EcoNojin/2.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())

        try:
            data = await asyncio.to_thread(_fetch)
            if len(data) > 1 and isinstance(data[1], list):
                series = {
                    str(item["date"]): item["value"]
                    for item in data[1] if item.get("value") is not None
                }
                out[friendly] = series
        except Exception:
            pass
    return out
