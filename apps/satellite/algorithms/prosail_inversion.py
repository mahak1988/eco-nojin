"""
ماژول الگوریتم حل معکوس PROSAIL - نسخه تکمیل شده

این ماژول بخشی از تلاش برای پیاده‌سازی مرحله ۱ مانیفست Hydroma-Nojin است.
هدف: پیاده‌سازی یک الگوریتم برای استخراج پارامترهای بیوفیزیکی (LAI, Cab, Cw) از داده‌های چند-طیفی (Sentinel-2).
این نسخه یک پیاده‌سازی نمادین و ساده شده است.
"""

import numpy as np
from typing import Dict, List, Tuple
from scipy.optimize import minimize, differential_evolution


def simulate_prosail_simple(lai: float, cab: float, cw: float, albedo_soil: np.ndarray) -> np.ndarray:
    """
    یک مدل ساده‌شده شبیه‌سازی PROSAIL برای چند باند.
    """
    # این یک تابع بسیار ساده شده است که فقط رفتار کلی را نمایش می‌دهد.
    k = 0.5 # ضریب کاهش نور نمادین
    rho_soil_contrib = albedo_soil * np.exp(-k * lai)

    # مدل ساده شده برای مولفه گیاهی
    rho_veg = np.zeros_like(albedo_soil)
    # تأثیر Cab در باندهای قرمز و NIR
    # باندهای فرضی: [Blue, Green, Red, RedEdge1, RedEdge2, RedEdge3, NIR, SWIR1, SWIR2]
    rho_veg[2] = 0.05 * (cab / 40.0) # باند قرمز (index 2)
    rho_veg[6] = 0.4 * (1 - cw) # باند NIR (index 6)

    # ترکیب
    rho_simulated = rho_soil_contrib + rho_veg
    rho_simulated = np.clip(rho_simulated, 0.0, 1.0) # بازه [0, 1]
    return rho_simulated


def invert_prosail(observed_refl: np.ndarray, albedo_soil: np.ndarray, initial_guess: List[float], method: str = 'L-BFGS-B') -> Dict[str, float]:
    """
    حل معکوس PROSAIL با استفاده از بهینه‌سازی.
    """
    bounds = [(0.1, 8), (5, 80), (0.004, 0.03)] # محدودیت‌های فیزیکی برای [LAI, Cab, Cw]

    def objective_function(x):
        lai, cab, cw = x
        rho_sim = simulate_prosail_simple(lai, cab, cw, albedo_soil)
        cost = np.sum((observed_refl - rho_sim)**2)
        return cost

    if method == 'L-BFGS-B':
        res = minimize(objective_function, initial_guess, method=method, bounds=bounds)
        if res.success:
            lai_est, cab_est, cw_est = res.x
            return {"LAI": np.clip(lai_est, 0.1, 8), "Cab": np.clip(cab_est, 5, 80), "Cw": np.clip(cw_est, 0.004, 0.03), "success": res.success, "fun": res.fun}
    elif method == 'differential_evolution':
        res = differential_evolution(objective_function, bounds, seed=1234)
        if res.success:
            lai_est, cab_est, cw_est = res.x
            return {"LAI": np.clip(lai_est, 0.1, 8), "Cab": np.clip(cab_est, 5, 80), "Cw": np.clip(cw_est, 0.004, 0.03), "success": res.success, "fun": res.fun}

    # اگر هیچ روشی موفق نبود
    lai_init, cab_init, cw_init = initial_guess
    return {"LAI": np.clip(lai_init, 0.1, 8), "Cab": np.clip(cab_init, 5, 80), "Cw": np.clip(cw_init, 0.004, 0.03), "success": False, "fun": float('inf')}


# Example usage (can be removed or moved to a test file)
if __name__ == "__main__":
    print("Testing PROSAIL Inversion with Differential Evolution...")
    obs_refl = np.array([0.06, 0.09, 0.13, 0.26, 0.36, 0.43, 0.49, 0.36, 0.16])
    soil_albedo = np.array([0.11, 0.13, 0.16, 0.21, 0.29, 0.36, 0.41, 0.31, 0.11])
    init_guess = [2.1, 41.0, 0.011]

    # تست روش L-BFGS-B
    retrieved_params_lbfgs = invert_prosail(obs_refl, soil_albedo, init_guess, method='L-BFGS-B')
    print("Retrieved Parameters (L-BFGS-B):", retrieved_params_lbfgs)

    # تست روش differential evolution
    retrieved_params_de = invert_prosail(obs_refl, soil_albedo, init_guess, method='differential_evolution')
    print("Retrieved Parameters (Differential Evolution):", retrieved_params_de)