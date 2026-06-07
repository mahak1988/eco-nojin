"""ERA5-Land Data Fetcher (Real or Simulated)"""
import json
import os
import random
import sys
from datetime import datetime

from scripts.core.logger import UnifiedLogger

logger = UnifiedLogger.get_logger(__name__)


PROJECT = r"D:\\econojin.com"
sys.path.insert(0, PROJECT)

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(PROJECT, ".env"))
except Exception as e:
    pass

BBOX = [51.2, 35.5, 51.3, 35.6]
VARS = ["2m_temperature", "total_precipitation", "surface_net_solar_radiation"]


def download_era5(start=2023, end=2023, out_dir=None):
    if out_dir is None:
        out_dir = os.path.join(PROJECT, "data", "raw", "era5")
    os.makedirs(out_dir, exist_ok=True)
    logger.info(f"[INFO] ERA5: {start}-{end} for BBOX {BBOX}")

    uid = os.getenv("CDS_API_UID", "").strip()
    key = os.getenv("CDS_API_KEY", "").strip()

    if not uid or not key or "your" in uid.lower():
        logger.info("[INFO] No CDS credentials - running SIMULATION mode")
        return _simulate(start, end, out_dir)

    try:
        import cdsapi

        client = cdsapi.Client(url=os.getenv("CDS_API_URL"), key=f"{uid}:{key}")
        downloaded = []
        for year in range(start, end + 1):
            fn = f"era5_land_PILOT_{year}.nc"
            fp = os.path.join(out_dir, fn)
            req = {
                "product_type": "reanalysis",
                "variable": VARS,
                "year": str(year),
                "month": [f"{m:02d}" for m in range(1, 13)],
                "day": [f"{d:02d}" for d in range(1, 29)],
                "time": ["00:00", "06:00", "12:00", "18:00"],
                "area": BBOX,
                "format": "netcdf",
            }
            logger.info(f"[INFO] Downloading {year}...")
            client.retrieve("reanalysis-era5-land", req, fp)
            downloaded.append({"file": fn, "size_mb": round(os.path.getsize(fp) / 1e6, 2)})
            logger.info(f"[OK] Saved: {fn}")
        return {"status": "success", "count": len(downloaded), "files": downloaded}
    except ImportError:
        logger.error("[ERROR] Install cdsapi: pip install cdsapi")
        return {"status": "error", "msg": "cdsapi missing"}
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        return {"status": "error", "msg": str(e)}


def _simulate(start, end, out_dir):
    simulated = []
    for year in range(start, end + 1):
        fn = f"era5_land_PILOT_{year}.nc"
        fp = os.path.join(out_dir, fn)
        with open(fp, "w") as f:
            f.write(f"# ERA5-Land Simulation\n# BBOX:{BBOX}\n# Year:{year}\n")
            f.write("# datetime,temp_C,precip_mm,solar_MJ\n")
            for m in range(1, 13):
                for d in range(1, 29):
                    for h in [0, 6, 12, 18]:
                        t = round(15 + random.uniform(-8, 12), 1)
                        p = round(max(0, random.expovariate(0.4)), 1)
                        s = round(12 + random.uniform(-5, 10), 1)
                        f.write(f"{year}-{m:02d}-{d:02d}T{h:02d}:00,{t},{p},{s}\n")
        simulated.append({"file": fn, "size_kb": round(os.path.getsize(fp) / 1024, 1)})
        logger.info(f"[SIM] Created: {fn}")
    return {"status": "simulated", "count": len(simulated), "files": simulated}


if __name__ == "__main__":
    logger.info("=== ERA5-Land Fetcher ===")
    r = download_era5(2023, 2023)
    logger.info(f"\n[RESULT] {r['status'].upper()}: {r['count']} files")
    if r.get("files"):
        logger.info(f"Sample: {r['files'][0]}")
    logger.info(f"\n[SUCCESS] ERA5 fetcher complete!")
    if r["status"] == "simulated":
        logger.info("For REAL data: Register at https://cds.climate.copernicus.eu")
