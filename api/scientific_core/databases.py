# api/scientific_core/databases.py
"""
پایگاه‌های داده مرجع برای تمام ماژول‌ها
"""

# ============================================================
# USDA Soil Texture Database (11 نوع)
# ============================================================
SOIL_TEXTURE_DATABASE = {
    "sand": {
        "name_fa": "شن",
        "name_en": "Sand",
        "sand_percent": 90, "silt_percent": 5, "clay_percent": 5,
        "theta_r": 0.045, "theta_s": 0.430,
        "alpha_vg": 0.145, "n_vg": 2.68,
        "k_sat_cm_day": 8.25,
        "bulk_density": 1.55,
        "field_capacity": 0.10, "wilting_point": 0.05,
        "usda_class": "sand",
    },
    "loamy_sand": {
        "name_fa": "شن لومی",
        "name_en": "Loamy Sand",
        "sand_percent": 80, "silt_percent": 12, "clay_percent": 8,
        "theta_r": 0.057, "theta_s": 0.410,
        "alpha_vg": 0.124, "n_vg": 2.28,
        "k_sat_cm_day": 4.50,
        "bulk_density": 1.50,
        "field_capacity": 0.14, "wilting_point": 0.07,
    },
    "sandy_loam": {
        "name_fa": "لومی شنی",
        "name_en": "Sandy Loam",
        "sand_percent": 65, "silt_percent": 20, "clay_percent": 15,
        "theta_r": 0.065, "theta_s": 0.410,
        "alpha_vg": 0.075, "n_vg": 1.89,
        "k_sat_cm_day": 2.50,
        "bulk_density": 1.45,
        "field_capacity": 0.20, "wilting_point": 0.10,
    },
    "loam": {
        "name_fa": "لوم",
        "name_en": "Loam",
        "sand_percent": 40, "silt_percent": 40, "clay_percent": 20,
        "theta_r": 0.078, "theta_s": 0.430,
        "alpha_vg": 0.036, "n_vg": 1.56,
        "k_sat_cm_day": 1.20,
        "bulk_density": 1.35,
        "field_capacity": 0.27, "wilting_point": 0.13,
    },
    "silt_loam": {
        "name_fa": "لومی سیلتی",
        "name_en": "Silty Loam",
        "sand_percent": 20, "silt_percent": 65, "clay_percent": 15,
        "theta_r": 0.067, "theta_s": 0.450,
        "alpha_vg": 0.028, "n_vg": 1.45,
        "k_sat_cm_day": 0.80,
        "bulk_density": 1.30,
        "field_capacity": 0.32, "wilting_point": 0.14,
    },
    "sandy_clay_loam": {
        "name_fa": "لومی رسی شنی",
        "name_en": "Sandy Clay Loam",
        "sand_percent": 55, "silt_percent": 15, "clay_percent": 30,
        "theta_r": 0.100, "theta_s": 0.390,
        "alpha_vg": 0.059, "n_vg": 1.51,
        "k_sat_cm_day": 0.60,
        "bulk_density": 1.35,
        "field_capacity": 0.25, "wilting_point": 0.14,
    },
    "clay_loam": {
        "name_fa": "لومی رسی",
        "name_en": "Clay Loam",
        "sand_percent": 30, "silt_percent": 35, "clay_percent": 35,
        "theta_r": 0.095, "theta_s": 0.410,
        "alpha_vg": 0.019, "n_vg": 1.31,
        "k_sat_cm_day": 0.35,
        "bulk_density": 1.30,
        "field_capacity": 0.32, "wilting_point": 0.20,
    },
    "silty_clay_loam": {
        "name_fa": "لومی رسی سیلتی",
        "name_en": "Silty Clay Loam",
        "sand_percent": 10, "silt_percent": 55, "clay_percent": 35,
        "theta_r": 0.089, "theta_s": 0.430,
        "alpha_vg": 0.016, "n_vg": 1.26,
        "k_sat_cm_day": 0.25,
        "bulk_density": 1.25,
        "field_capacity": 0.35, "wilting_point": 0.21,
    },
    "sandy_clay": {
        "name_fa": "رسی شنی",
        "name_en": "Sandy Clay",
        "sand_percent": 55, "silt_percent": 5, "clay_percent": 40,
        "theta_r": 0.100, "theta_s": 0.380,
        "alpha_vg": 0.027, "n_vg": 1.23,
        "k_sat_cm_day": 0.30,
        "bulk_density": 1.35,
        "field_capacity": 0.30, "wilting_point": 0.20,
    },
    "silty_clay": {
        "name_fa": "رسی سیلتی",
        "name_en": "Silty Clay",
        "sand_percent": 5, "silt_percent": 50, "clay_percent": 45,
        "theta_r": 0.089, "theta_s": 0.400,
        "alpha_vg": 0.013, "n_vg": 1.17,
        "k_sat_cm_day": 0.18,
        "bulk_density": 1.25,
        "field_capacity": 0.37, "wilting_point": 0.24,
    },
    "clay": {
        "name_fa": "رس",
        "name_en": "Clay",
        "sand_percent": 20, "silt_percent": 20, "clay_percent": 60,
        "theta_r": 0.068, "theta_s": 0.380,
        "alpha_vg": 0.010, "n_vg": 1.15,
        "k_sat_cm_day": 0.12,
        "bulk_density": 1.20,
        "field_capacity": 0.38, "wilting_point": 0.25,
    },
}


# ============================================================
# ضرایب RUSLE بر اساس اقلیم
# ============================================================
R_FACTOR_BY_CLIMATE = {
    "mediterranean": {"annual_r_mm": 500, "r_factor": 350, "description": "مدیترانه‌ای"},
    "arid": {"annual_r_mm": 200, "r_factor": 150, "description": "خشک"},
    "semi_arid": {"annual_r_mm": 350, "r_factor": 250, "description": "نیمه‌خشک"},
    "humid_subtropical": {"annual_r_mm": 1000, "r_factor": 600, "description": "نیمه‌گرمسیری مرطوب"},
    "tropical": {"annual_r_mm": 1500, "r_factor": 900, "description": "گرمسیری"},
    "temperate": {"annual_r_mm": 800, "r_factor": 450, "description": "معتدل"},
}


# ============================================================
# آستانه‌های شاخص‌ها (IPCC, WMO)
# ============================================================
INDEX_THRESHOLDS = {
    "NDVI": {
        "water_snow_cloud": (-1.0, -0.1),
        "bare_soil": (-0.1, 0.1),
        "sparse_vegetation": (0.1, 0.3),
        "moderate_vegetation": (0.3, 0.6),
        "dense_vegetation": (0.6, 0.8),
        "forest": (0.8, 1.0),
    },
    "SPI": {
        "extremely_wet": (2.0, float("inf")),
        "very_wet": (1.5, 2.0),
        "moderately_wet": (1.0, 1.5),
        "near_normal": (-1.0, 1.0),
        "moderately_dry": (-1.5, -1.0),
        "severely_dry": (-2.0, -1.5),
        "extremely_dry": (float("-inf"), -2.0),
    },
    "NBR": {
        "high_regeneration": (0.27, float("inf")),
        "dense_vegetation": (0.1, 0.27),
        "unburned": (-0.1, 0.1),
        "low_severity": (-0.25, -0.1),
        "moderate_severity": (-0.44, -0.25),
        "high_severity": (float("-inf"), -0.44),
    },
}


# ============================================================
# توابع کمکی
# ============================================================
def get_all_soils() -> dict:
    """دریافت تمام خاک‌ها"""
    return SOIL_TEXTURE_DATABASE


def get_soil(key: str) -> dict:
    """دریافت یک خاک خاص"""
    return SOIL_TEXTURE_DATABASE.get(key, SOIL_TEXTURE_DATABASE["loam"])


def get_all_thresholds() -> dict:
    """دریافت تمام آستانه‌ها"""
    return INDEX_THRESHOLDS
