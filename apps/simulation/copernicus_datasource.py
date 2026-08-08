"""Copernicus Data Space — free commercial alternative to GEE (deprecated Apr 2026)."""
import logging;logger=logging.getLogger(__name__)
async def fetch_s2_ndvi(lat:float,lon:float,date_from:str,date_to:str)->dict:
    logger.info(f"Copernicus S2 NDVI ({lat},{lon})")
    return{"source":"Copernicus DS","satellite":"Sentinel-2","resolution":"10m","ndvi_mean":0.45,"ndvi_std":0.08,"note":"Replace with CDSE OAuth2 API call"}
async def fetch_s1_soil_moisture(lat:float,lon:float,date:str)->dict:
    logger.info(f"Copernicus S1 moisture ({lat},{lon})")
    return{"source":"Copernicus","satellite":"Sentinel-1","resolution":"20m","soil_moisture":0.28,"unit":"m3/m3","note":"Replace with S1 GRD via CDSE"}
GEE_WARNING="GEE is no longer free for commercial use (Apr 2026). Migrate to Copernicus CDSE."
