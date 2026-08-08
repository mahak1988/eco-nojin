"""
ماژول موتور چرخه کربن-نیتروژن DayCent بومی - نسخه اولیه

این کلاس بخشی از تلاش برای پیاده‌سازی مرحله ۱ مانیفست Hydroma-Nojin است.
هدف: پیاده‌سازی یک موتور چرخه C/N بر اساس مدل چند-مخزنه DayCent با ۷ مخزن.
این نسخه یک پیاده‌سازی بسیار ساده شده است.
"""

import numpy as np
from typing import Dict, List


class DayCentNative:
    """
    موتور چرخه کربن-نیتروژن DayCent بومی - نسخه اولیه.

    این کلاس یک مدل ۷ مخزنی را برای کربن پیاده‌سازی می‌کند:
    1. Metabolic (MET)
    2. Structural (STR)
    3. Active (ACT)
    4. Slow (SLOW)
    5. Passive (PASS)
    6. DOC (Dissolved Organic Carbon)
    7. Biochar (BC)
    """

    def __init__(self, initial_carbon_pools: Dict[str, float], dt: float = 86400): # dt = 1 day
        """
        مقداردهی اولیه موتور DayCent.

        Args:
            initial_carbon_pools: دیکشنری شامل مقادیر اولیه کربن در هر مخزن {'MET': val, 'STR': val, ...}.
            dt: گام زمانی انتگرال‌گیری (ثانیه).
        """
        self.pools = {
            "MET": initial_carbon_pools.get("MET", 0.0),
            "STR": initial_carbon_pools.get("STR", 0.0),
            "ACT": initial_carbon_pools.get("ACT", 0.0),
            "SLOW": initial_carbon_pools.get("SLOW", 0.0),
            "PASS": initial_carbon_pools.get("PASS", 0.0),
            "DOC": initial_carbon_pools.get("DOC", 0.0),
            "BC": initial_carbon_pools.get("BC", 0.0),
        }
        self.dt = dt
        self.pool_names = list(self.pools.keys())
        self.C = np.array([self.pools[name] for name in self.pool_names])

    def _calculate_environmental_factors(self, temp: float, moisture: float, clay_fraction: float, oxygen: float = 0.2, ph: float = 6.5) -> Dict[str, float]:
        """
        محاسبه ضرایب وابسته به محیط برای نرخ تجزیه.

        Args:
            temp: دمای خاک (Celsius).
            moisture: رطوبت خاک (m³/m³).
            clay_fraction: کسر وزنی رس (0-1).
            oxygen: غلظ اکسیژن (mol/mol). پیش‌فرض ۰.۲.
            ph: pH خاک. پیش‌فرض ۶.۵.

        Returns:
            دیکشنری شامل f(T), f(θ), f(Clay), f(O2), f(pH).
        """
        # --- تابع دما - مدل سه‌بخشی (بخش 3.1.1 مانیفست) ---
        T_min, T_opt, T_max = 0.0, 35.0, 50.0 # Celsius
        Ea = 53000 # J/mol, activation energy
        R = 8.314 # J/(mol*K)
        T_ref = 298.15 # Kelvin

        if temp < T_min or temp > T_max:
            f_T = 0.0
        elif temp <= T_opt:
            f_T = np.exp(Ea / R * (1/T_ref - 1/(temp + 273.15)))
        else: # temp > T_opt
            # تابع گاوسی برای کاهش نرخ در دمای بالا
            sigma_T = 10 # یک پارامتر برای پهنای منحنی
            f_T_opt = np.exp(Ea / R * (1/T_ref - 1/(T_opt + 273.15)))
            f_T = f_T_opt * np.exp(-((temp - T_opt)**2) / (2 * sigma_T**2))

        # --- تابع رطوبت - مدل دو بخشی (بخش 3.1.2 مانیفست) ---
        # فرض مقدارهای فیک برای FC و WP
        theta_wp = 0.1
        theta_fc = 0.3
        theta_s = 0.5 # Porosity
        if moisture < theta_wp:
            f_M = 0.0
        elif theta_wp <= moisture <= theta_fc:
            f_M = 0.6 * (moisture - theta_wp) / (theta_fc - theta_wp)
        elif theta_fc < moisture <= theta_s:
            f_M = 0.6 + 0.4 * (theta_s - moisture) / (theta_s - theta_fc)
        else:
            f_M = 0.0 # اگر اشباع باشد، ممکن است نرخ کاهد

        # --- تابع اکسیژن ---
        # مدل ساده: نرخ تجزیه با کمبود اکسیژن کاهش می‌یابد
        f_O2 = min(1.0, oxygen / 0.15) # اگر O2 کمتر از 15% باشد، نرخ کم می‌شود

        # --- تابع pH ---
        # مدل ساده: نرخ تجزیه در pH بیرون از محدوده ایده‌آل کاهش می‌یابد
        optimal_ph_min, optimal_ph_max = 5.5, 8.0
        if ph < optimal_ph_min or ph > optimal_ph_max:
            f_pH = 0.5 # نصف نرخ ایده‌آل
        else:
            f_pH = 1.0

        # --- تابع رس (تقریبی) ---
        f_Clay = 1.0 + 2 * clay_fraction

        return {"f_T": max(0, min(f_T, 2)), "f_M": max(0, min(f_M, 1)), "f_O2": max(0, min(f_O2, 1)), "f_pH": max(0, min(f_pH, 1)), "f_Clay": max(0, f_Clay)}

    def _calculate_decomposition_rates(self, env_factors: Dict[str, float], base_rates: Dict[str, float]) -> np.ndarray:
        """
        محاسبه نرخ کل تجزیه برای هر مخزن با در نظر گرفتن عوامل محیطی.

        Args:
            env_factors: خروجی _calculate_environmental_factors.
            base_rates: نرخ‌های مرجع تجزیه برای هر مخزن (1/ثانیه).

        Returns:
            آرایه numpy شامل نرخ‌های تجزیه نهایی.
        """
        k_ref = np.array([base_rates[name] for name in self.pool_names])
        f_T = env_factors["f_T"]
        f_M = env_factors["f_M"]
        f_O2 = env_factors["f_O2"]
        f_pH = env_factors["f_pH"]
        f_Clay = env_factors["f_Clay"]

        # نرخ نهایی: k_final = k_ref * f(T) * f(θ) * f(O2) * f(pH) * f(Clay)
        # در این مدل ساده، فرض می‌کنیم تمام عوامل مستقل هستند
        k_total = k_ref * f_T * f_M * f_O2 * f_pH * f_Clay
        return k_total

    def step(self, temp: float, moisture: float, clay_fraction: float, oxygen: float = 0.2, ph: float = 6.5, base_rates: Dict[str, float] = None):
        """
        یک گام زمانی از مدل تجزیه را اجرا می‌کند.

        Args:
            temp: دمای خاک (Celsius).
            moisture: رطوبت خاک (m³/m³).
            clay_fraction: کسر وزنی رس.
            oxygen: غلظ اکسیژن.
            ph: pH خاک.
            base_rates: نرخ‌های مرجع تجزیه (1/ثانیه). اگر None باشد، از مقدار پیش‌فرض استفاده می‌شود.
        """
        if base_rates is None:
            # نرخ‌های مرجع تقریبی (1/ثانیه)
            base_rates = {
                "MET": 1e-6,  # تجزیه سریع
                "STR": 5e-7,
                "ACT": 1e-7,
                "SLOW": 1e-8,
                "PASS": 1e-9, # تجزیه خیلی کند
                "DOC": 1e-6, # بین MET و STR
                "BC": 1e-12 # بسیار پایدار
            }

        env_factors = self._calculate_environmental_factors(temp, moisture, clay_fraction, oxygen, ph)
        k_rates = self._calculate_decomposition_rates(env_factors, base_rates)

        # dC/dt = -k * C (مدل ساده شده جهت نمایش)
        dC_dt = -k_rates * self.C

        # انتگرال‌گیری ساده
        self.C += dC_dt * self.dt

        # بروزرسانی دیکشنری pools
        for i, name in enumerate(self.pool_names):
            self.pools[name] = max(0.0, self.C[i]) # جلوگیری از مقادیر منفی


# Example usage (can be removed or moved to a test file)
if __name__ == "__main__":
    print("Testing DayCentNative...")
    initial_pools = {
        "MET": 10.0,
        "STR": 50.0,
        "ACT": 5.0,
        "SLOW": 100.0,
        "PASS": 20.0,
        "DOC": 2.0,
        "BC": 5.0
    }

    # نرخ‌های مرجع تقریبی (1/ثانیه)
    base_rates = {
        "MET": 1e-6,  # تجزیه سریع
        "STR": 5e-7,
        "ACT": 1e-7,
        "SLOW": 1e-8,
        "PASS": 1e-9, # تجزیه خیلی کند
        "DOC": 1e-6, # بین MET و STR
        "BC": 1e-12 # بسیار پایدار
    }

    model = DayCentNative(initial_pools)

    temp = 25  # Celsius
    moisture = 0.4 # m3/m3
    clay = 0.25 # 0-1
    oxygen = 0.18 # mol/mol
    ph = 7.0

    print("Initial pools:", model.pools)
    for i in range(10): # 10 روز
        model.step(temp, moisture, clay, oxygen, ph, base_rates)
        print(f"Day {(i+1)*1}: {model.pools}")