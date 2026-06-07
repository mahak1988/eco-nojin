# api/modules/structures/optimizer.py
import numpy as np
import math
import random
import geojson
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# کتابخانه بهینه‌سازی چندهدفه
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.optimize import minimize
from pymoo.util.ref_dirs import get_reference_directions

router = APIRouter(prefix="/structures", tags=["Spatial-Hydraulic Optimizer"])

# ==============================================================================
# ۱. تعریف مشخصات ۱۱ سازه آبخیزداری و حفاظت خاک
# ==============================================================================
STRUCTURE_SPECS = {
    1: {"name": "بند خاکی/سنگی (Check Dam)", "max_slope": 15, "min_depth": 1.0, "cost_factor": 1.2},
    2: {"name": "نوار تراز (Swale)", "max_slope": 8, "min_depth": 0.5, "cost_factor": 0.4},
    3: {"name": "ترانشه نفوذی (Infiltration Trench)", "max_slope": 10, "min_depth": 0.8, "cost_factor": 0.6},
    4: {"name": "حوضچه نفوذی (Percolation Tank)", "max_slope": 5, "min_depth": 1.5, "cost_factor": 1.5},
    5: {"name": "بند گابیونی (Gabion)", "max_slope": 20, "min_depth": 1.0, "cost_factor": 1.8},
    6: {"name": "تراس‌بندی (Terracing)", "max_slope": 25, "min_depth": 0.6, "cost_factor": 0.8},
    7: {"name": "میکروکچمنت (Micro-catchment)", "max_slope": 12, "min_depth": 0.4, "cost_factor": 0.3},
    8: {"name": "سرریز V شکل (V-notch Weir)", "max_slope": 10, "min_depth": 0.5, "cost_factor": 0.5},
    9: {"name": "بند شنی (Sand Dam)", "max_slope": 8, "min_depth": 2.0, "cost_factor": 1.3},
    10: {"name": "بند زیرسطحی (Subsurface Dam)", "max_slope": 5, "min_depth": 1.5, "cost_factor": 2.0},
    11: {"name": "نوار بافر زیستی (Bio-swale)", "max_slope": 10, "min_depth": 0.5, "cost_factor": 0.2},
}

# ==============================================================================
# ۲. تعریف مسئله بهینه‌سازی چندهدفه (NSGA-III Problem)
# ==============================================================================
class SpatialHydraulicProblem(ElementwiseProblem):
    def __init__(self):
        # متغیرهای تصمیم: 
        # x[0]: نوع سازه (1 تا 11) -> پیوسته در نظر گرفته شده و در evaluate گرد می‌شود
        # x[1]: فاصله بین سازه‌ها (متر) [10, 200]
        # x[2]: عرض/طول سازه (متر) [1, 50]
        # x[3]: عمق سازه (متر) [0.3, 3.0]
        super().__init__(
            n_var=4,
            n_obj=3,
            n_ieq_constr=2, # دو قید نامساوی
            xl=np.array([1.0, 10.0, 1.0, 0.3]),
            xu=np.array([11.0, 200.0, 50.0, 3.0])
        )

    def _evaluate(self, x, out, *args, **kwargs):
        # دریافت پارامترهای ورودی از context (در صورت نیاز به توسعه)
        # در اینجا برای سادگی، پارامترهای هیدرولوژیکی فرضی اما واقع‌گرایانه استفاده می‌شود
        design_rainfall = 50.0  # mm/hr
        catchment_area = 10.0   # ha
        slope = 8.0             # %
        twi_score = 0.6         # شاخص رطوبت توپوگرافی نرمال‌شده (0 تا 1)

        # گرد کردن نوع سازه به نزدیک‌ترین عدد صحیح
        struct_id = int(round(x[0]))
        if struct_id < 1: struct_id = 1
        if struct_id > 11: struct_id = 11
        
        spacing = x[1]
        width = x[2]
        depth = x[3]
        
        specs = STRUCTURE_SPECS[struct_id]

        # --- محاسبه توابع هدف (Objectives) ---
        
        # هدف ۱: کمینه‌سازی هزینه (تخمین بر اساس حجم عملیات خاکی * ضریب هزینه سازه)
        volume = width * depth * spacing
        obj1_cost = volume * specs["cost_factor"]

        # هدف ۲: کمینه‌سازی ریسک هیدرولیک (انحراف از ظرفیت مهار رواناب)
        # استفاده از روش عقلایی (Rational Method) ساده‌شده برای تخمین دبی
        runoff_coeff = 0.5
        peak_q = (runoff_coeff * design_rainfall * catchment_area) / 360.0  # m3/s
        
        # ظرفیت مهار تقریبی بر اساس ابعاد (فرمول ساده‌شده حوضچه)
        capture_capacity = (width * depth * 0.8) / 10.0  # ضریب تبدیل فرضی
        
        # جریمه اگر ظرفیت کمتر از دبی پیک باشد
        hydraulic_risk = max(0, peak_q - capture_capacity) * 1000
        obj2_risk = hydraulic_risk

        # هدف ۳: کمینه‌سازی ناکارآمدی مکانی (تطابق با شیب و TWI)
        # هر سازه شیب بهینه‌ای دارد. انحراف از آن جریمه دارد.
        slope_penalty = max(0, slope - specs["max_slope"]) * 10
        twi_mismatch = abs(twi_score - (depth / 3.0)) * 50 # فرض: عمق بیشتر نیاز به TWI بالاتر دارد
        obj3_spatial = slope_penalty + twi_mismatch

        # --- محاسبه قیود (Constraints) ---
        # قید ۱: عمق باید از حداقل مجاز سازه بیشتر باشد (g(x) <= 0)
        g1 = specs["min_depth"] - depth
        
        # قید ۲: شیب زمین نباید از حداکثر مجاز سازه بیشتر باشد (g(x) <= 0)
        g2 = slope - specs["max_slope"]

        out["F"] = [obj1_cost, obj2_risk, obj3_spatial]
        out["G"] = [g1, g2]


# ==============================================================================
# ۳. مدل‌های Pydantic برای FastAPI
# ==============================================================================
class OptimizationRequest(BaseModel):
    design_rainfall: float = Field(..., description="بارش طراحی (mm/hr)")
    catchment_area: float = Field(..., description="مساحت حوضه آبریز (ha)")
    slope_percent: float = Field(..., description="شیب زمین (%)")
    soil_texture: str = Field(..., description="بافت خاک: 'sandy', 'loam', 'clay'")
    target_structures: List[int] = Field(default=[1, 2, 4, 5], description="لیست ID سازه‌های مجاز برای بهینه‌سازی")

class ParetoSolution(BaseModel):
    structure_id: int
    structure_name: str
    spacing_m: float
    width_m: float
    depth_m: float
    volume_m3: float
    cost_index: float
    risk_index: float
    spatial_index: float
    confidence_interval_95: Dict[str, float]
    geojson_layout: Dict[str, Any]

class OptimizationResponse(BaseModel):
    status: str
    num_solutions: int
    solutions: List[ParetoSolution]


# ==============================================================================
# ۴. اندپوینت FastAPI برای اجرای بهینه‌سازی
# ==============================================================================
@router.post("/optimize-nsga3", response_model=OptimizationResponse)
async def run_nsga3_optimizer(request: OptimizationRequest):
    try:
        # ۱. پیکربندی الگوریتم NSGA-III
        # برای ۳ هدف، از روش Das-Dennis برای تولید جهت‌های مرجع استفاده می‌کنیم
        ref_dirs = get_reference_directions("das-dennis", n_obj=3, n_partitions=12)
        
        algorithm = NSGA3(
            pop_size=100,
            sampling=FloatRandomSampling(),
            crossover=SBX(prob=0.9, eta=15),
            mutation=PM(prob=0.1, eta=20),
            eliminate_duplicates=True
        )

        # ۲. تعریف مسئله
        problem = SpatialHydraulicProblem()

        # ۳. اجرای بهینه‌سازی
        res = minimize(
            problem,
            algorithm,
            ('n_gen', 150), # تعداد نسل‌ها (برای تولید واقعی می‌توان به ۵۰۰+ افزایش داد)
            seed=42,
            verbose=False
        )

        if res.X is None:
            raise HTTPException(status_code=500, detail="الگوریتم به همگرایی نرسید.")

        # ۴. پردازش جبهه پارتو (Pareto Front)
        solutions = []
        
        # انتخاب حداکثر ۵ راه‌حل برتر از جبهه پارتو برای نمایش به کاربر
        # (مرتب‌سازی بر اساس مجموع نرمال‌شده اهداف)
        f_norm = (res.F - res.F.min(axis=0)) / (res.F.max(axis=0) - res.F.min(axis=0) + 1e-8)
        scores = f_norm.sum(axis=1)
        best_indices = np.argsort(scores)[:5]

        for idx in best_indices:
            x = res.X[idx]
            
            struct_id = int(round(x[0]))
            if struct_id not in request.target_structures:
                continue # فیلتر کردن سازه‌های درخواستی کاربر
                
            spacing = float(x[1])
            width = float(x[2])
            depth = float(x[3])
            volume = width * depth * spacing
            
            # ۵. تحلیل مونت‌کارلو برای بازه اطمینان ۹۵٪
            mc_volumes = []
            for _ in range(500):
                # اعمال نویز گوسی ±۱۰٪ به پارامترهای ورودی
                noise_rain = random.uniform(0.9, 1.1)
                noise_area = random.uniform(0.9, 1.1)
                # بازمحاسبه حجم مورد نیاز بر اساس نویز (ساده‌شده)
                mc_vol = volume * noise_rain * noise_area
                mc_volumes.append(mc_vol)
            
            mc_volumes.sort()
            ci_95 = {
                "lower_bound": round(mc_volumes[int(0.025 * len(mc_volumes))], 2),
                "upper_bound": round(mc_volumes[int(0.975 * len(mc_volumes))], 2)
            }

            # ۶. تولید GeoJSON برای چیدمان مکانی (شبیه‌سازی چیدمان روی کانتور)
            # فرض: شروع از یک نقطه UTM فرضی و ایجاد آرایه‌ای از سازه‌ها با فاصله مشخص
            base_x, base_y = 500000.0, 4000000.0 # مختصات UTM فرضی (زون ۴۰ شمالی)
            features = []
            current_x = base_x
            
            num_structures = max(1, int(100 / spacing)) # شبیه‌سازی ۱۰۰ متر طول کانتور
            
            for i in range(num_structures):
                features.append(geojson.Feature(
                    geometry=geojson.Point((current_x, base_y)),
                    properties={
                        "id": i + 1,
                        "structure": STRUCTURE_SPECS[struct_id]["name"],
                        "width_m": round(width, 2),
                        "depth_m": round(depth, 2),
                        "utm_zone": "40N"
                    }
                ))
                current_x += spacing # فاصله بهینه محاسبه‌شده

            geojson_layout = geojson.FeatureCollection(features)

            solutions.append(ParetoSolution(
                structure_id=struct_id,
                structure_name=STRUCTURE_SPECS[struct_id]["name"],
                spacing_m=round(spacing, 2),
                width_m=round(width, 2),
                depth_m=round(depth, 2),
                volume_m3=round(volume, 2),
                cost_index=round(res.F[idx][0], 2),
                risk_index=round(res.F[idx][1], 2),
                spatial_index=round(res.F[idx][2], 2),
                confidence_interval_95=ci_95,
                geojson_layout=geojson_layout
            ))

        return OptimizationResponse(
            status="success",
            num_solutions=len(solutions),
            solutions=solutions
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در موتور بهینه‌سازی: {str(e)}")