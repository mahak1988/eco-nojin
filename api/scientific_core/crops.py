# api/scientific_core/crops.py
"""
پایگاه داده محصولات و ضرایب Kc
مرجع: FAO-56 (Allen et al., 1998)
       FAO-24 (Doorenbos & Pruitt, 1977)
       Wright (1982) - ASCE
"""
from typing import Dict, List, Optional


# پایگاه داده محصولات با ضرایب Kc چهار مرحله‌ای
CROPS_DATABASE = {
    # غلات
    "wheat": {
        "name_fa": "گندم",
        "name_en": "Wheat",
        "name_scientific": "Triticum aestivum",
        "family": "Poaceae",
        "type": "cereal",
        "kc": {"init": 0.30, "dev": None, "mid": 1.15, "end": 0.30},
        "stages_days": [30, 50, 40, 30],  # init, dev, mid, late
        "root_depth_cm": {"init": 20, "dev": 50, "mid": 80, "end": 80},
        "depletion_fraction": 0.55,
        "harvest_index": 0.45,
        "max_height_m": 1.0,
        "y_potential_t_ha": 8.0,
    },
    "barley": {
        "name_fa": "جو",
        "name_en": "Barley",
        "name_scientific": "Hordeum vulgare",
        "family": "Poaceae",
        "type": "cereal",
        "kc": {"init": 0.30, "mid": 1.15, "end": 0.25},
        "stages_days": [25, 45, 40, 30],
        "root_depth_cm": {"init": 20, "dev": 45, "mid": 70, "end": 70},
        "depletion_fraction": 0.55,
        "harvest_index": 0.42,
        "max_height_m": 0.9,
        "y_potential_t_ha": 7.0,
    },
    "maize": {
        "name_fa": "ذرت",
        "name_en": "Maize",
        "name_scientific": "Zea mays",
        "family": "Poaceae",
        "type": "cereal",
        "kc": {"init": 0.30, "mid": 1.20, "end": 0.50},
        "stages_days": [25, 55, 40, 30],
        "root_depth_cm": {"init": 20, "dev": 60, "mid": 100, "end": 100},
        "depletion_fraction": 0.55,
        "harvest_index": 0.48,
        "max_height_m": 2.5,
        "y_potential_t_ha": 12.0,
    },
    "rice": {
        "name_fa": "برنج",
        "name_en": "Rice",
        "name_scientific": "Oryza sativa",
        "family": "Poaceae",
        "type": "cereal",
        "kc": {"init": 1.05, "mid": 1.20, "end": 0.90},
        "stages_days": [30, 60, 40, 30],
        "root_depth_cm": {"init": 10, "dev": 30, "mid": 50, "end": 50},
        "depletion_fraction": 1.00,
        "harvest_index": 0.50,
        "max_height_m": 1.2,
        "y_potential_t_ha": 10.0,
    },
    "sorghum": {
        "name_fa": "سورگوم",
        "name_en": "Sorghum",
        "name_scientific": "Sorghum bicolor",
        "family": "Poaceae",
        "type": "cereal",
        "kc": {"init": 0.30, "mid": 1.15, "end": 0.40},
        "stages_days": [30, 50, 40, 30],
        "root_depth_cm": {"init": 20, "dev": 60, "mid": 120, "end": 120},
        "depletion_fraction": 0.55,
        "harvest_index": 0.45,
        "max_height_m": 2.0,
        "y_potential_t_ha": 9.0,
    },
    # حبوبات
    "soybean": {
        "name_fa": "سویا",
        "name_en": "Soybean",
        "name_scientific": "Glycine max",
        "family": "Fabaceae",
        "type": "legume",
        "kc": {"init": 0.30, "mid": 1.15, "end": 0.35},
        "stages_days": [30, 45, 40, 25],
        "root_depth_cm": {"init": 15, "dev": 40, "mid": 70, "end": 70},
        "depletion_fraction": 0.60,
        "harvest_index": 0.42,
        "max_height_m": 0.9,
        "y_potential_t_ha": 4.0,
    },
    "chickpea": {
        "name_fa": "نخود",
        "name_en": "Chickpea",
        "name_scientific": "Cicer arietinum",
        "family": "Fabaceae",
        "type": "legume",
        "kc": {"init": 0.30, "mid": 1.10, "end": 0.25},
        "stages_days": [30, 40, 40, 25],
        "root_depth_cm": {"init": 15, "dev": 40, "mid": 80, "end": 80},
        "depletion_fraction": 0.55,
        "harvest_index": 0.30,
        "max_height_m": 0.6,
        "y_potential_t_ha": 2.5,
    },
    "lentil": {
        "name_fa": "عدس",
        "name_en": "Lentil",
        "name_scientific": "Lens culinaris",
        "family": "Fabaceae",
        "type": "legume",
        "kc": {"init": 0.30, "mid": 1.05, "end": 0.20},
        "stages_days": [25, 40, 35, 25],
        "root_depth_cm": {"init": 15, "dev": 35, "mid": 60, "end": 60},
        "depletion_fraction": 0.55,
        "harvest_index": 0.28,
        "max_height_m": 0.5,
        "y_potential_t_ha": 2.0,
    },
    # سبزیجات
    "tomato": {
        "name_fa": "گوجه‌فرنگی",
        "name_en": "Tomato",
        "name_scientific": "Solanum lycopersicum",
        "family": "Solanaceae",
        "type": "vegetable",
        "kc": {"init": 0.35, "mid": 1.15, "end": 0.70},
        "stages_days": [30, 40, 50, 30],
        "root_depth_cm": {"init": 20, "dev": 50, "mid": 80, "end": 80},
        "depletion_fraction": 0.55,
        "harvest_index": 0.65,
        "max_height_m": 1.2,
        "y_potential_t_ha": 80.0,
    },
    "potato": {
        "name_fa": "سیب‌زمینی",
        "name_en": "Potato",
        "name_scientific": "Solanum tuberosum",
        "family": "Solanaceae",
        "type": "vegetable",
        "kc": {"init": 0.35, "mid": 1.15, "end": 0.45},
        "stages_days": [30, 45, 40, 25],
        "root_depth_cm": {"init": 15, "dev": 40, "mid": 60, "end": 60},
        "depletion_fraction": 0.55,
        "harvest_index": 0.80,
        "max_height_m": 0.7,
        "y_potential_t_ha": 45.0,
    },
    "onion": {
        "name_fa": "پیاز",
        "name_en": "Onion",
        "name_scientific": "Allium cepa",
        "family": "Amaryllidaceae",
        "type": "vegetable",
        "kc": {"init": 0.35, "mid": 1.05, "end": 0.75},
        "stages_days": [35, 50, 40, 25],
        "root_depth_cm": {"init": 15, "dev": 30, "mid": 40, "end": 40},
        "depletion_fraction": 0.55,
        "harvest_index": 0.85,
        "max_height_m": 0.5,
        "y_potential_t_ha": 50.0,
    },
    # صنعتی
    "cotton": {
        "name_fa": "پنبه",
        "name_en": "Cotton",
        "name_scientific": "Gossypium hirsutum",
        "family": "Malvaceae",
        "type": "industrial",
        "kc": {"init": 0.35, "mid": 1.15, "end": 0.30},
        "stages_days": [40, 60, 50, 30],
        "root_depth_cm": {"init": 20, "dev": 60, "mid": 120, "end": 120},
        "depletion_fraction": 0.65,
        "harvest_index": 0.35,
        "max_height_m": 1.3,
        "y_potential_t_ha": 4.0,
    },
    "sugarbeet": {
        "name_fa": "چغندرقند",
        "name_en": "Sugar Beet",
        "name_scientific": "Beta vulgaris",
        "family": "Amaranthaceae",
        "type": "industrial",
        "kc": {"init": 0.35, "mid": 1.10, "end": 0.65},
        "stages_days": [40, 60, 60, 30],
        "root_depth_cm": {"init": 20, "dev": 50, "mid": 90, "end": 90},
        "depletion_fraction": 0.65,
        "harvest_index": 0.75,
        "max_height_m": 0.7,
        "y_potential_t_ha": 75.0,
    },
    "sugarcane": {
        "name_fa": "نیشکر",
        "name_en": "Sugarcane",
        "name_scientific": "Saccharum officinarum",
        "family": "Poaceae",
        "type": "industrial",
        "kc": {"init": 0.40, "mid": 1.25, "end": 0.75},
        "stages_days": [60, 120, 180, 60],
        "root_depth_cm": {"init": 25, "dev": 80, "mid": 150, "end": 150},
        "depletion_fraction": 0.70,
        "harvest_index": 0.65,
        "max_height_m": 4.0,
        "y_potential_t_ha": 120.0,
    },
    # علوفه
    "alfalfa": {
        "name_fa": "یونجه",
        "name_en": "Alfalfa",
        "name_scientific": "Medicago sativa",
        "family": "Fabaceae",
        "type": "forage",
        "kc": {"init": 0.30, "mid": 1.20, "end": 0.75},
        "stages_days": [20, 40, 30, 20],
        "root_depth_cm": {"init": 20, "dev": 60, "mid": 150, "end": 150},
        "depletion_fraction": 0.65,
        "harvest_index": 0.90,
        "max_height_m": 0.8,
        "y_potential_t_ha": 18.0,
    },
    # درختان میوه
    "apple": {
        "name_fa": "سیب",
        "name_en": "Apple",
        "name_scientific": "Malus domestica",
        "family": "Rosaceae",
        "type": "fruit_tree",
        "kc": {"init": 0.35, "mid": 1.05, "end": 0.60},
        "stages_days": [60, 90, 90, 60],
        "root_depth_cm": {"init": 40, "dev": 80, "mid": 140, "end": 140},
        "depletion_fraction": 0.65,
        "harvest_index": 0.60,
        "max_height_m": 4.0,
        "y_potential_t_ha": 40.0,
    },
    "grape": {
        "name_fa": "انگور",
        "name_en": "Grape",
        "name_scientific": "Vitis vinifera",
        "family": "Vitaceae",
        "type": "fruit_tree",
        "kc": {"init": 0.30, "mid": 0.80, "end": 0.50},
        "stages_days": [50, 80, 80, 50],
        "root_depth_cm": {"init": 30, "dev": 70, "mid": 120, "end": 120},
        "depletion_fraction": 0.60,
        "harvest_index": 0.70,
        "max_height_m": 2.0,
        "y_potential_t_ha": 25.0,
    },
    "pistachio": {
        "name_fa": "پسته",
        "name_en": "Pistachio",
        "name_scientific": "Pistacia vera",
        "family": "Anacardiaceae",
        "type": "fruit_tree",
        "kc": {"init": 0.30, "mid": 0.85, "end": 0.55},
        "stages_days": [60, 90, 90, 60],
        "root_depth_cm": {"init": 40, "dev": 100, "mid": 180, "end": 180},
        "depletion_fraction": 0.65,
        "harvest_index": 0.45,
        "max_height_m": 5.0,
        "y_potential_t_ha": 3.5,
    },
    "date_palm": {
        "name_fa": "نخل خرما",
        "name_en": "Date Palm",
        "name_scientific": "Phoenix dactylifera",
        "family": "Arecaceae",
        "type": "fruit_tree",
        "kc": {"init": 0.35, "mid": 0.90, "end": 0.60},
        "stages_days": [60, 90, 90, 60],
        "root_depth_cm": {"init": 50, "dev": 120, "mid": 200, "end": 200},
        "depletion_fraction": 0.65,
        "harvest_index": 0.55,
        "max_height_m": 20.0,
        "y_potential_t_ha": 12.0,
    },
    "walnut": {
        "name_fa": "گردو",
        "name_en": "Walnut",
        "name_scientific": "Juglans regia",
        "family": "Juglandaceae",
        "type": "fruit_tree",
        "kc": {"init": 0.35, "mid": 1.05, "end": 0.60},
        "stages_days": [60, 90, 90, 60],
        "root_depth_cm": {"init": 40, "dev": 90, "mid": 150, "end": 150},
        "depletion_fraction": 0.65,
        "harvest_index": 0.50,
        "max_height_m": 15.0,
        "y_potential_t_ha": 4.0,
    },
}


class CropCalculator:
    """محاسبات مربوط به محصول"""
    
    @classmethod
    def get_kc_at_stage(cls, crop_key: str, growth_day: int) -> float:
        """محاسبه Kc در روز مشخص"""
        crop = CROPS_DATABASE.get(crop_key)
        if not crop:
            return 0.8
        
        kc = crop["kc"]
        stages = crop["stages_days"]
        
        if growth_day <= stages[0]:
            return kc["init"]
        elif growth_day <= stages[0] + stages[1]:
            progress = (growth_day - stages[0]) / stages[1]
            return kc["init"] + progress * (kc["mid"] - kc["init"])
        elif growth_day <= stages[0] + stages[1] + stages[2]:
            return kc["mid"]
        else:
            total_mid = stages[0] + stages[1] + stages[2]
            progress = min(1.0, (growth_day - total_mid) / stages[3])
            return kc["mid"] + progress * (kc["end"] - kc["mid"])
    
    @classmethod
    def get_growth_stage(cls, crop_key: str, growth_day: int) -> str:
        """تعیین مرحله رشد"""
        crop = CROPS_DATABASE.get(crop_key)
        if not crop:
            return "نامشخص"
        
        stages = crop["stages_days"]
        stage_names = ["اولیه", "توسعه", "میانی", "پایانی"]
        
        if growth_day <= stages[0]:
            return stage_names[0]
        elif growth_day <= stages[0] + stages[1]:
            return stage_names[1]
        elif growth_day <= stages[0] + stages[1] + stages[2]:
            return stage_names[2]
        else:
            return stage_names[3]
    
    @classmethod
    def estimate_yield(cls, crop_key: str, water_stress_days: int, 
                       total_days: int) -> Dict:
        """
        تخمین عملکرد با در نظر گرفتن تنش آبی
        مرجع: FAO-32 (Doorenbos & Kassam, 1979)
        (Ya/Ym) = 1 - Ky × (1 - ETa/ETm)
        """
        crop = CROPS_DATABASE.get(crop_key)
        if not crop:
            return {}
        
        # ضریب حساسیت به کم‌آبی Ky (مقادیر FAO-33)
        ky_values = {
            "wheat": 1.10, "barley": 0.90, "maize": 1.25,
            "rice": 1.10, "sorghum": 1.05, "soybean": 1.10,
            "cotton": 0.85, "sugarbeet": 1.05, "tomato": 1.10,
            "potato": 1.15, "alfalfa": 1.10,
        }
        
        ky = ky_values.get(crop_key, 1.0)
        stress_ratio = water_stress_days / total_days if total_days > 0 else 0
        yield_reduction = ky * stress_ratio
        relative_yield = max(0, 1 - yield_reduction)
        actual_yield = crop["y_potential_t_ha"] * relative_yield
        
        return {
            "crop_name_fa": crop["name_fa"],
            "potential_yield_t_ha": crop["y_potential_t_ha"],
            "actual_yield_t_ha": round(actual_yield, 2),
            "yield_reduction_percent": round(yield_reduction * 100, 1),
            "ky_factor": ky,
            "stress_ratio": round(stress_ratio, 3),
        }


# تابع کمکی
def get_all_crops_summary() -> Dict:
    """خلاصه تمام محصولات"""
    return {
        key: {
            "name_fa": c["name_fa"],
            "name_en": c["name_en"],
            "type": c["type"],
            "kc_mid": c["kc"]["mid"],
            "total_days": sum(c["stages_days"]),
            "y_potential_t_ha": c["y_potential_t_ha"],
        }
        for key, c in CROPS_DATABASE.items()
    }
