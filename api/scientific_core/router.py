# api/scientific_core/router.py
"""
Router مرکزی برای دسترسی به تمام مدل‌های علمی
"""
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Dict, List, Optional

from . import indices, hydrology, crops, carbon, erosion, drought, soil_water, databases



class ThresholdsResponse(BaseModel):
    """آستانه‌های شاخص‌های علمی"""
    ndvi_min: float = -1.0
    ndvi_max: float = 1.0
    evi_min: float = -1.0
    evi_max: float = 1.0
    soil_moisture_min: float = 0.0
    soil_moisture_max: float = 100.0
    temperature_min: float = -50.0
    temperature_max: float = 60.0
    ph_min: float = 0.0
    ph_max: float = 14.0
    spi_drought_threshold: float = -1.0
    spei_drought_threshold: float = -1.0


router = APIRouter(prefix="/scientific", tags=["Scientific Core"])


# ============ Models ============
class BandsInput(BaseModel):
    blue: Optional[float] = None
    green: Optional[float] = None
    red: Optional[float] = None
    nir: Optional[float] = None
    red_edge: Optional[float] = None
    swir1: Optional[float] = None
    swir2: Optional[float] = None


class SCS_CN_Input(BaseModel):
    rainfall_mm: float
    curve_number: float = 75
    amc: str = "AMC_II"


class RUSLE_Input(BaseModel):
    r_factor: float = 400
    soil_texture: str = "loam"
    land_use: str = "cropland_conventional"
    conservation: str = "no_practice"
    slope_length_m: float = 50
    slope_percent: float = 5


class RothC_Input(BaseModel):
    initial_soc: float = 2.5
    carbon_input_t_ha: float = 2.0
    clay_percent: float = 25
    mean_temp_c: float = 18
    annual_rain_mm: float = 500
    years: int = 30


class IPCC_Tier1_Input(BaseModel):
    area_ha: float
    soc_reference: float = 30.0
    land_use_factor: str = "cropland_continued"
    management_factor: str = "full_tillage"
    input_factor: str = "medium"
    time_period: int = 20


class SPI_Input(BaseModel):
    precipitation: List[float]
    time_scale: int = 3


# ============ Endpoints ============
@router.get("/", response_model=Dict[str, Any])
async def scientific_core_info():
    """اطلاعات کلی هسته علمی"""
    return {
        "name": "Econojin Scientific Core",
        "version": "1.0.0",
        "modules": {
            "spectral_indices": ["NDVI", "EVI", "SAVI", "MSAVI2", "GNDVI", "ARVI", "NDRE", "NDWI", "MNDWI", "NBR", "NDBI"],
            "hydrology": ["SCS-CN", "Rational", "Horton", "Philip", "Green-Ampt", "Muskingum"],
            "crops": ["FAO-56 Kc", "Penman-Monteith", "AquaCrop", "GDD"],
            "carbon": ["RothC", "Century", "ICBM", "IPCC Tier 1"],
            "erosion": ["RUSLE", "MUSLE", "RWEQ"],
            "drought": ["SPI", "SPEI", "VHI", "KBDI"],
            "soil_water": ["van Genuchten", "Brooks-Corey", "Campbell", "FAO-56 Balance"],
        },
        "databases": {
            "soils": len(databases.SOIL_TEXTURE_DATABASE),
            "crops": len(crops.CROPS_DATABASE),
        },
    }


@router.get("/soils", response_model=Dict[str, Any])
async def list_soils():
    """لیست تمام خاک‌های USDA"""
    return databases.get_all_soils()


@router.get("/crops", response_model=Dict[str, Any])
async def list_crops():
    """لیست تمام محصولات"""
    return crops.get_all_crops_summary()


@router.post("/indices/calculate", response_model=Dict[str, Any])
async def calculate_indices(bands: BandsInput):
    """محاسبه تمام شاخص‌های طیفی"""
    bands_dict = bands.dict(exclude_none=True)
    results = indices.SpectralIndices.calculate_all(bands_dict)
    
    # اضافه کردن تفسیر
    if "NDVI" in results:
        results["NDVI_interpretation"] = indices.SpectralIndices.interpret_ndvi(results["NDVI"])
    
    return {"bands": bands_dict, "indices": results}


@router.post("/hydrology/scs-cn", response_model=Dict[str, Any])
async def calculate_scs_cn(input: SCS_CN_Input):
    """محاسبه رواناب SCS-CN"""
    return hydrology.SCS_CN.calculate(input.rainfall_mm, input.curve_number, input.amc)


@router.post("/erosion/rusle", response_model=Dict[str, Any])
async def calculate_rusle(input: RUSLE_Input):
    """محاسبه فرسایش RUSLE"""
    return erosion.RUSLE.calculate(
        r=input.r_factor,
        soil_texture=input.soil_texture,
        land_use=input.land_use,
        conservation=input.conservation,
        slope_length_m=input.slope_length_m,
        slope_percent=input.slope_percent,
    )


@router.post("/carbon/rothc", response_model=Dict[str, Any])
async def calculate_rothc(input: RothC_Input):
    """شبیه‌سازی RothC"""
    return carbon.RothC.simulate_year(
        initial_soc=input.initial_soc,
        carbon_input_t_ha=input.carbon_input_t_ha,
        clay_percent=input.clay_percent,
        mean_temp_c=input.mean_temp_c,
        annual_rain_mm=input.annual_rain_mm,
        years=input.years,
    )


@router.post("/carbon/ipcc-tier1", response_model=Dict[str, Any])
async def calculate_ipcc(input: IPCC_Tier1_Input):
    """محاسبه IPCC Tier 1"""
    return carbon.IPCC_Tier1.calculate(
        area_ha=input.area_ha,
        soc_reference=input.soc_reference,
        f_lu=input.land_use_factor,
        f_mg=input.management_factor,
        f_i=input.input_factor,
        time_period=input.time_period,
    )


@router.post("/drought/spi", response_model=Dict[str, Any])
async def calculate_spi(input: SPI_Input):
    """محاسبه SPI"""
    return drought.SPI.calculate(input.precipitation, input.time_scale)


@router.get("/thresholds", response_model=ThresholdsResponse)
async def get_thresholds():
    """آستانه‌های شاخص‌ها"""
    return databases.get_all_thresholds()


@router.get("/crops/{crop_key}", response_model=Dict[str, Any])
async def get_crop_details(crop_key: str):
    """جزئیات یک محصول"""
    crop = crops.CROPS_DATABASE.get(crop_key)
    if not crop:
        raise HTTPException(404, "محصول یافت نشد")
    return crop


@router.get("/crops/{crop_key}/kc/{day}", response_model=Dict[str, Any])
async def get_kc_at_day(crop_key: str, day: int):
    """ضریب Kc در روز مشخص"""
    kc = crops.CropCalculator.get_kc_at_stage(crop_key, day)
    stage = crops.CropCalculator.get_growth_stage(crop_key, day)
    return {"crop": crop_key, "day": day, "kc": round(kc, 3), "stage": stage}
