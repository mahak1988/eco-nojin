# api/modules/structures/calculator.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import math
import random

router = APIRouter(prefix="/structures", tags=["Structures Dimensioning"])

class StructureInput(BaseModel):
    structure_type: str = Field(..., description="نوع سازه: 'check_dam' یا 'swale'")
    design_rainfall: float = Field(..., description="بارش طراحی (mm/hr)")
    catchment_area: float = Field(..., description="مساحت حوضه آبریز (ha)")
    slope_percent: float = Field(..., description="شیب زمین (%)")
    soil_texture: str = Field(..., description="بافت خاک: 'sandy', 'loam', 'clay'")

class DimensionOutput(BaseModel):
    structure_type: str
    recommended_width_m: float
    recommended_depth_m: float
    required_volume_m3: float
    manning_n: float
    confidence_interval_95: dict
    geojson_marker: dict

# ضرایب زبری مانینگ بر اساس بافت خاک
MANNING_COEFFICIENTS = {
    "sandy": 0.025,
    "loam": 0.035,
    "clay": 0.045
}

@router.post("/calculate-dimensions", response_model=DimensionOutput)
async def calculate_dimensions(data: StructureInput):
    try:
        # 1. محاسبه دبی پیک (Peak Discharge) با روش Rational (ساده‌شده برای نمونه)
        # Q = C * I * A  (C: ضریب رواناب، I: شدت بارش، A: مساحت)
        runoff_coeff = 0.6 if data.soil_texture == "clay" else 0.4 if data.soil_texture == "loam" else 0.2
        peak_discharge_m3s = (runoff_coeff * data.design_rainfall * data.catchment_area) / 360
        
        # 2. محاسبه ابعاد با استفاده از معادله مانینگ (Q = (1/n) * A * R^(2/3) * S^(1/2))
        n = MANNING_COEFFICIENTS.get(data.soil_texture, 0.035)
        slope_decimal = data.slope_percent / 100
        
        # تخمین اولیه عرض و عمق (بهینه‌سازی ساده‌شده)
        if data.structure_type == "check_dam":
            base_width = max(2.0, peak_discharge_m3s * 1.5)
            depth = max(1.5, (peak_discharge_m3s / (base_width * (slope_decimal**0.5) / n))**0.6)
            volume = base_width * depth * 10 # تخمین حجم حوضچه
        else: # swale
            base_width = max(1.0, peak_discharge_m3s * 0.8)
            depth = max(0.5, (peak_discharge_m3s / (base_width * (slope_decimal**0.5) / n))**0.6)
            volume = base_width * depth * 50 # طول فرضی 50 متر
            
        # 3. تحلیل مونت‌کارلو ساده برای بازه اطمینان ۹۵٪
        simulations = 1000
        volumes = []
        for _ in range(simulations):
            noise = random.uniform(0.85, 1.15) # ±15% عدم قطعیت در پارامترها
            volumes.append(volume * noise)
        
        volumes.sort()
        ci_95 = {
            "lower_bound": round(volumes[int(0.025 * simulations)], 2),
            "upper_bound": round(volumes[int(0.975 * simulations)], 2)
        }

        # 4. تولید GeoJSON Marker (مختصات فرضی برای نمونه)
        geojson = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [59.6 + random.uniform(-0.01, 0.01), 36.3 + random.uniform(-0.01, 0.01)] # مختصات نمونه خراسان
            },
            "properties": {
                "name": f"{data.structure_type}_optimized",
                "volume_m3": volume,
                "status": "ready_for_deployment"
            }
        }

        return DimensionOutput(
            structure_type=data.structure_type,
            recommended_width_m=round(base_width, 2),
            recommended_depth_m=round(depth, 2),
            required_volume_m3=round(volume, 2),
            manning_n=n,
            confidence_interval_95=ci_95,
            geojson_marker=geojson
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در محاسبه هیدرولیک: {str(e)}")