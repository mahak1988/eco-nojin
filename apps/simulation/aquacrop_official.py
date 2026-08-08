"""AquaCrop Official — wraps aquacrop (Apache 2.0) + ERA5/CHIRPS."""
from __future__ import annotations
import logging
from typing import Any
import numpy as np
from apps.simulation.earth_engine.era5_land import fetch_era5_land
from apps.simulation.earth_engine.chirps import fetch_chirps
logger = logging.getLogger(__name__)
try:
    import aquacrop
    HAS_OFFICIAL = True
except ImportError:
    HAS_OFFICIAL = False
    logger.warning("pip install aquacrop for official model")

async def run_aquacrop_official(crop="wheat",lat=35.7,lon=51.4,planting_date="2026-10-15",soil_type="clay_loam",irrigation="rainfed")->dict[str,Any]:
    era5=await fetch_era5_land(lat,lon,planting_date,days=180)
    chirps=await fetch_chirps(lat,lon,planting_date,days=180)
    precip=[d["precip"]for d in chirps];et0=[d["et0"]for d in era5];tmin=[d["tmin"]for d in era5];tmax=[d["tmax"]for d in era5]
    if HAS_OFFICIAL:
        m=aquacrop.AquaCropModel(sim_start=planting_date,sim_end="2027-04-15",soil_type=soil_type,crop_name=crop,irrigation_method=0 if irrigation=="rainfed" else 1)
        w=m.prepare_weather(tmin=tmin,tmax=tmax,et0=et0,precip=precip);r=m.run(w)
        return{"model_fidelity":"official","final_yield":round(float(r.final_yield),2),"final_biomass":round(float(r.final_biomass),2),"total_et":round(float(r.total_et),1),"water_productivity":round(float(r.water_productivity),2)}
    else:
        mu=np.mean(et0)if et0 else 4.0;bm=mu*20;ye=bm*0.45
        return{"model_fidelity":"simplified","note":"pip install aquacrop","final_yield":round(float(ye),2),"final_biomass":round(float(bm),2),"total_et":round(float(mu*180),1)}
