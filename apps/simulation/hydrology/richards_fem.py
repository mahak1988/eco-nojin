"""
ماژول حل معادله ریچاردز با استفاده از روش المان محدود (FEM) - نسخه اولیه

این کلاس بخشی از تلاش برای پیاده‌سازی مرحله ۱ مانیفست Hydroma-Nojin است.
هدف: پیاده‌سازی یک حل‌کننده عددی پیشرفته‌تر برای معادله ریچاردز با استفاده از FEM.
این نسخه یک پیاده‌سازی بسیار ساده شده و نمادین است و فقط یک نمونه از ساختار کلی را نشان می‌دهد.
"""

import numpy as np
from scipy.sparse import diags, linalg
from typing import Dict, Tuple, Union


class RichardsFEMSolver:
    """
    حل‌کننده معادله ریچاردز با استفاده از روش المان محدود (FEM) - نسخه اولیه.

    این نسخه یک مدل ۱ بعدی ساده شده است و از توابع شکل خطی استفاده می‌کند.
    """

    def __init__(self, theta_initial: np.ndarray, h_initial: np.ndarray, depth: float, num_elements: int, dt: float):
        """
        مقداردهی اولیه حل‌کننده FEM.

        Args:
            theta_initial: آرایه 1 بعدی، مقدار اولیه رطوبت حجمی در گره‌های عمقی.
            h_initial: آرایه 1 بعدی، مقدار اولیه هدای اولیه در گره‌های عمقی.
            depth: عمق کل لایه خاک (متر).
            num_elements: تعداد المان‌های FEM.
            dt: گام زمانی (ثانیه).
        """
        self.nz = num_elements + 1  # تعداد گره‌ها = تعداد المان‌ها + 1
        self.depth = depth
        self.dt = dt
        self.dz = depth / num_elements  # طول هر المان

        # تعداد گره‌ها باید با theta و h مطابقت داشته باشد
        assert len(theta_initial) == self.nz
        assert len(h_initial) == self.nz

        self.theta = theta_initial
        self.h = h_initial
        # متغیرهای مربوط به ماتریس جرم و سفتی
        self.M = None
        self.K_global = None
        self.initialize_matrices()

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

    def calculate_h_from_theta(self, theta: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        """محاسبه h از theta (همانند قبل)."""
        Se = (theta - params["theta_r"]) / (params["theta_s"] - params["theta_r"])
        Se = np.clip(Se, 1e-6, 1.0 - 1e-6)
        h = (np.power(np.power(Se, -1.0/params["m"]) - 1.0, 1.0/params["n"]) / (-params["alpha"]))
        h = np.where(h > 0, -h, h)
        return h

    def calculate_theta_from_h(self, h: np.ndarray, params: Dict[str, float]) -> np.ndarray:
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

    def solve_step(self, params: Dict[str, float], Ks: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        یک گام زمانی از حل FEM معادله ریچاردز را انجام می‌دهد.
        این یک نسخه بسیار ساده شده است.
        """
        # 1. محاسبه K بر اساس h فعلی
        K_local = self.calculate_K(self.h, Ks, params)
        
        # 2. ensamble ماتریس K_global جدید
        self.assemble_global_K(K_local)

        # 3. تشکیل سمت چپ معادله: (M/dt + K_global) * h_new = M/dt * h_old
        A = self.M / self.dt + self.K_global
        b = (self.M / self.dt) @ self.h # @ نماد ضرب ماتریسی است

        # 4. حل سیستم معادلات خطی برای h_new
        h_new = linalg.spsolve(A, b)

        # 5. محاسبه theta_new از روی h_new
        theta_new = self.calculate_theta_from_h(h_new, params)

        # 6. بروزرسانی وضعیت داخلی
        self.h = h_new
        self.theta = theta_new

        return self.theta.copy(), self.h.copy()


# Example usage (can be removed or moved to a test file)
if __name__ == "__main__":
    print("Testing RichardsFEMSolver...")
    nz = 10
    depth = 1.0 # 1 meter
    dt = 3600 # 1 hour
    num_elem = nz - 1
    theta_ini = np.ones(nz) * 0.3 # Initial volumetric moisture
    h_ini = np.linspace(-100, -1000, nz) # Initial pressure head (negative)

    solver = RichardsFEMSolver(theta_ini, h_ini, depth, num_elem, dt)
    vg_params = solver.van_genuchten_params(alpha=1.0, n=1.5, theta_s=0.5, theta_r=0.05)
    
    print("Initial Theta:", solver.theta)
    print("Initial Head (h):", solver.h)
    
    Ks_val = 1e-5 # Saturated hydraulic conductivity (m/s)
    for i in range(2): # Run 2 time steps for demo
        theta_new, h_new = solver.solve_step(vg_params, Ks_val)
        print(f"Step {i+1} - Theta: {theta_new}")
        print(f"Step {i+1} - Head (h): {h_new}")