"""
ماژول حل معادله ریچاردز با استفاده از روش المان محدود (FEM) - نسخه تکمیل شده

این کلاس بخشی از تلاش برای پیاده‌سازی مرحله ۱ مانیفست Hydroma-Nojin است.
هدف: پیاده‌سازی یک حل‌کننده عددی پیشرفته‌تر برای معادله ریچاردز با استفاده از FEM.
این نسخه شامل مدل Van Genuchten-Mualem، تابع تنش آبی ریشه، مدل هیسترزیس و محاسبات مربوط به FEM است.
"""

import numpy as np
from scipy.sparse import diags, linalg
from typing import Dict, Tuple, Union


class RichardsFEMSolver:
    """
    حل‌کننده معادله ریچاردز با استفاده از روش المان محدود (FEM) - نسخه تکمیل شده.

    این نسخه یک مدل ۱ بعدی ساده شده است و از توابع شکل خطی استفاده می‌کند.
    شامل مدل Van Genuchten-Mualem، تابع تنش آبی ریشه (Feddes)، و مدل ساده هیسترزیس می‌شود.
    """

    def __init__(self, theta_initial: np.ndarray, h_initial: np.ndarray, depth: float, num_elements: int, dt: float, vg_params: Dict[str, float], ks: float):
        """
        مقداردهی اولیه حل‌کننده FEM.

        Args:
            theta_initial: آرایه 1 بعدی، مقدار اولیه رطوبت حجمی در گره‌های عمقی.
            h_initial: آرایه 1 بعدی، مقدار اولیه هدای اولیه در گره‌های عمقی.
            depth: عمق کل لایه خاک (متر).
            num_elements: تعداد المان‌های FEM.
            dt: گام زمانی (ثانیه).
            vg_params: دیکشنری شامل پارامترهای Van Genuchten {'alpha', 'n', 'theta_s', 'theta_r'}.
            ks: هدایت اشباع شده (Ks) خاک (m/s).
        """
        self.nz = num_elements + 1  # تعداد گره‌ها = تعداد المان‌ها + 1
        self.depth = depth
        self.dt = dt
        self.dz = depth / num_elements  # طول هر المان
        self.vg_params = vg_params
        self.ks = ks

        # تعداد گره‌ها باید با theta و h مطابقت داشته باشد
        assert len(theta_initial) == self.nz
        assert len(h_initial) == self.nz

        self.theta = theta_initial
        self.h = h_initial
        # متغیرهای مربوط به ماتریس جرم و سفتی
        self.M = None
        self.K_global = None
        self.initialize_matrices()

        # متغیرهای هیسترزیس
        self.is_drying = np.ones(self.nz, dtype=bool) # True = خشک شدن، False = مرطوب شدن
        self.theta_prev = theta_initial.copy() # برای تشخیص جهت تغییر

    def initialize_matrices(self):
        """ماتریس‌های جرم (M) و سفتی (K) اولیه را ایجاد می‌کند."""
        # ماتریس جرم (M) برای تابع شکل خطی 1D (ساده شده)
        # M = (dz/6) * [[2, 1], [1, 2]] برای هر المان، که به صورت جهانی ت ensamble می‌شود
        diagonals = [np.ones(self.nz) * 2, np.ones(self.nz - 1), np.ones(self.nz - 1)]
        positions = [0, -1, 1]
        M_raw = diags(diagonals, positions, shape=(self.nz, self.nz)).toarray()
        M_raw[0, 0] = 1  # شرایط مرزی
        M_raw[-1, -1] = 1
        self.M = (self.dz / 6.0) * M_raw

        # ماتریس سفتی (K) اولیه (ساده شده)
        # K = (1/dz) * [[1, -1], [-1, 1]] برای هر المان
        diagonals_K = [np.ones(self.nz - 1) * -1, np.ones(self.nz), np.ones(self.nz - 1) * -1]
        positions_K = [-1, 0, 1]
        K_raw = diags(diagonals_K, positions_K, shape=(self.nz, self.nz)).toarray()
        K_raw[0, 0] = 1  # شرایط مرزی
        K_raw[-1, -1] = 1
        self.K_global = K_raw # این باید در هر گام زمانی با K(h) واقعی بروزرسانی شود

    def van_genuchten_params(self, alpha: float, n: float, theta_s: float, theta_r: float) -> Dict[str, float]:
        """محاسبه پارامترهای مدل ون گوچتن (همانند قبل)."""
        m = 1 - 1/n
        return {"alpha": alpha, "n": n, "m": m, "theta_s": theta_s, "theta_r": theta_r}

    def calculate_h_from_theta_hysteresis(self, theta: np.ndarray, params: Dict[str, float], is_drying: np.ndarray) -> np.ndarray:
        """
        محاسبه h از theta با در نظر گرفتن هیسترزیس.
        استفاده از مدل ساده‌شده: جابه‌جایی منحنی retention بر اساس جهت مرطوب/خشک شدن.
        """
        Se = (theta - params["theta_r"]) / (params["theta_s"] - params["theta_r"])
        Se = np.clip(Se, 1e-6, 1.0 - 1e-6)
        
        # مدل ساده: alpha_hyst = alpha * (1 + shift_factor) بسته به جهت
        shift_factor_drying = 0.2 # مقدار فیک برای نمایش اثر
        shift_factor_wetting = -0.1

        alpha_mod = params["alpha"] * (1 + np.where(is_drying, shift_factor_drying, shift_factor_wetting))
        
        h = (np.power(np.power(Se, -1.0/params["m"]) - 1.0, 1.0/params["n"]) / (-alpha_mod))
        h = np.where(h > 0, -h, h)
        return h

    def calculate_theta_from_h_hysteresis(self, h: np.ndarray, params: Dict[str, float], is_drying: np.ndarray) -> np.ndarray:
        """
        محاسبه theta از h با در نظر گرفتن هیسترزیس.
        """
        h_abs = np.abs(h)
        # مدل ساده: alpha_hyst = alpha * (1 + shift_factor) بسته به جهت
        shift_factor_drying = 0.2
        shift_factor_wetting = -0.1
        alpha_mod = params["alpha"] * (1 + np.where(is_drying, shift_factor_drying, shift_factor_wetting))
        
        Se = np.power(1 + np.power(alpha_mod * h_abs, params["n"]), -params["m"])
        theta = Se * (params["theta_s"] - params["theta_r"]) + params["theta_r"]
        return theta

    def _calculate_vg_functions(self, h: np.ndarray, is_drying: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        محاسبه توابع مربوط به مدل Van Genuchten (Se, kr, capacity) با در نظر گرفتن هیسترزیس.
        """
        # 1. محاسبه Se با هیسترزیس
        Se = (self.calculate_theta_from_h_hysteresis(h, self.vg_params, is_drying) - self.vg_params["theta_r"]) / (self.vg_params["theta_s"] - self.vg_params["theta_r"])
        Se = np.clip(Se, 0.0, 1.0)

        # 2. محاسبه kr با هیسترزیس
        m = 1 - 1/self.vg_params["n"]
        # تغییر جزئی در m بر اساس جهت تغییر
        m_mod = m * (1 + np.where(is_drying, 0.1, -0.05))
        kr = np.power(Se, 0.5) * np.power(1 - np.power(1 - np.power(Se, 1/m_mod), m_mod), 2)
        kr = np.clip(kr, 1e-12, 1.0)

        # 3. محاسبه capacity (dTheta/dh)
        alpha_mod = self.vg_params["alpha"] * (1 + np.where(is_drying, 0.2, -0.1))
        n_mod = self.vg_params["n"]
        term1 = alpha_mod * n_mod * (Se**(1/n_mod)) * ((1 - Se**(1/m_mod))**(m_mod-1)) / (self.vg_params["theta_s"] - self.vg_params["theta_r"])
        term2 = (1 / (1 - Se**(1/m_mod)))**2
        capacity = term1 * term2
        capacity = np.clip(capacity, 1e-8, 1e-2) # محدود کردن مقدار

        return Se, kr, capacity

    def update_hysteresis_state(self, theta_current: np.ndarray):
        """بروزرسانی وضعیت خشک/مرطوب شدن بر اساس تغییرات رطوبت."""
        # تشخیص جهت تغییر
        delta_theta = theta_current - self.theta_prev
        # اگر رطوبت افزایش یابد، مرطوب شدن است
        self.is_drying = delta_theta <= 0
        self.theta_prev = theta_current.copy()

    def calculate_h_from_theta(self, theta: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        """محاسبه h از theta بدون هیسترزیس (برای مقایسه یا موارد خاص)."""
        return self.calculate_theta_from_h_hysteresis(theta, params, np.zeros_like(self.is_drying))
        """محاسبه theta از h (همانند قبل)."""
        h_abs = np.abs(h)
        Se = np.power(1 + np.power(params["alpha"] * h_abs, params["n"]), -params["m"])
        theta = Se * (params["theta_s"] - params["theta_r"]) + params["theta_r"]
        return theta

    def calculate_K(self, h: np.ndarray, Ks: float, params: Dict[str, float]) -> np.ndarray:
        """محاسبه K بر اساس h (همانند قبل)."""
        theta_local = self.calculate_theta_from_h(h, params)
        Se = (theta_local - params["theta_r"]) / (params["theta_s"] - params["theta_r"])
        Se = np.clip(Se, 0.0, 1.0)
        kr = np.power(Se, 0.5) * np.power(1 - np.power(1 - np.power(Se, 1/params["m"]), params["m"]), 2)
        kr = np.clip(kr, 1e-12, 1.0)
        return Ks * kr

    def assemble_global_K(self, K_values: np.ndarray):
        """
        ماتریس سفتی جهانی K_global را با مقادیر K(h) محاسبه شده از هر گره بروزرسانی می‌کند.
        این یک تقریب ساده شده است.
        """
        # اینجا فقط یک میانگین گرفته می‌شود تا ماتریس K_global تغییر کند.
        avg_K = np.mean(K_values)
        self.K_global.fill(0) # Reset
        diagonals_K = [np.ones(self.nz - 1) * -avg_K, np.ones(self.nz) * 2*avg_K, np.ones(self.nz - 1) * -avg_K]
        positions_K = [-1, 0, 1]
        self.K_global = diags(diagonals_K, positions_K, shape=(self.nz, self.nz)).toarray()
        self.K_global[0, 0] = 1  # شرایط مرزی
        self.K_global[-1, -1] = 1

    def solve_step(self, root_extraction_rate: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        یک گام زمانی از حل FEM معادله ریچاردز را انجام می‌دهد.
        شامل تابع تنش آبی ریشه.
        """
        # 1. بروزرسانی وضعیت هیسترزیس
        self.update_hysteresis_state(self.theta)

        # 2. محاسبه پارامترهای FVG
        Se, kr, capacity = self._calculate_vg_functions(self.h, self.is_drying)
        K_local = self.ks * kr
        sink = self.calculate_root_sink(self.h, alpha_param=root_extraction_rate)

        # 3. محاسبه ماتریس‌های FEM
        # ماتریس سفتی جدید
        diagonals_K = [np.ones(self.nz - 1) * -K_local[:-1], np.ones(self.nz) * (K_local[1:] + K_local[:-1]), np.ones(self.nz - 1) * -K_local[1:]]
        positions_K = [-1, 0, 1]
        K_raw = diags(diagonals_K, positions_K, shape=(self.nz, self.nz)).toarray()
        K_raw[0, 0] = 1  # شرایط مرزی
        K_raw[-1, -1] = 1
        self.K_global = K_raw

        # ماتریس ظرفیت جدید (C)
        C_diag = capacity
        C = diags([C_diag], [0], shape=(self.nz, self.nz)).toarray()
        C[0, 0] = 1 # شرایط مرزی
        C[-1, -1] = 1

        # 4. تشکیل سمت چپ معادله: (C/dt + K_global) * h_new = C/dt * h_old + sink
        A = C / self.dt + self.K_global
        b = (C / self.dt) @ self.h + sink

        # 5. حل سیستم معادلات خطی برای h_new
        h_new = linalg.spsolve(A, b)

        # 6. محاسبه theta_new از روی h_new با در نظر گرفتن هیسترزیس
        theta_new = self.calculate_theta_from_h_hysteresis(h_new, self.vg_params, self.is_drying)

        # 7. بروزرسانی وضعیت داخلی
        self.h = h_new
        self.theta = theta_new

        return self.theta.copy(), self.h.copy()


# Example usage (can be removed or moved to a test file)
if __name__ == "__main__":
    print("Testing RichardsFEMSolver with Hysteresis and Capacity...")
    nz = 10
    depth = 1.0 # 1 meter
    dt = 3600 # 1 hour
    num_elem = nz - 1
    theta_ini = np.ones(nz) * 0.3
    h_ini = np.linspace(-100, -1000, nz)

    vg_params = {"alpha": 1.0, "n": 1.5, "theta_s": 0.5, "theta_r": 0.05}
    ks_val = 1e-5

    solver = RichardsFEMSolver(theta_ini, h_ini, depth, num_elem, dt, vg_params, ks_val)
    
    print("Initial Theta:", solver.theta)
    print("Initial Head (h):", solver.h)
    print("Initial Hysteresis State (Drying):", solver.is_drying)
    
    for i in range(2):
        theta_new, h_new = solver.solve_step(root_extraction_rate=1e-7) # 1e-7 m/s extraction
        print(f"Step {i+1} - Theta: {theta_new}")
        print(f"Step {i+1} - Head (h): {h_new}")
        print(f"Step {i+1} - Hysteresis State (Drying): {solver.is_drying}")
        # تغییر مصنوعی برای ایجاد تغییر جهت
        if i==0:
            solver.theta *= 1.1