"""
ماژول فیزیک خاک - پیاده‌سازی اولیه معادله ریچاردز

این ماژول بخشی از تلاش برای پیاده‌سازی مانیفست علمی Hydroma-Nojin است.
هدف: پیاده‌سازی یک موتور عددی ساده برای حل معادله ریچاردز.
"""

import numpy as np
from typing import Dict, Tuple, Union


class RichardsEquationSolver:
    """
    حل‌کننده عددی ساده معادله ریچاردز برای جریان آب در خاک غیراشباض.

    این کلاس از روش ضمنی فرونشاند (Implicit Finite Difference Method) استفاده می‌کند.
    """

    def __init__(self, theta_initial: np.ndarray, h_initial: np.ndarray, depth: float, num_nodes: int, dt: float):
        """
        مقداردهی اولیه حل‌کننده.

        Args:
            theta_initial: آرایه 1 بعدی، مقدار اولیه رطوبت حجمی در گره‌های عمقی.
            h_initial: آرایه 1 بعدی، مقدار اولیه هدای اولیه در گره‌های عمقی.
            depth: عمق کل لایه خاک (متر).
            num_nodes: تعداد گره‌های گسسته در عمق.
            dt: گام زمانی (ثانیه).
        """
        self.theta = theta_initial
        self.h = h_initial
        self.depth = depth
        self.nz = num_nodes
        self.dt = dt
        self.dz = depth / (num_nodes - 1)
        self.K = np.ones(num_nodes) * 1e-6  # مقدار اولیه ساده شده برای هدایت هیدرولیکی (m/s)

    def van_genuchten_params(self, alpha: float, n: float, theta_s: float, theta_r: float) -> Dict[str, float]:
        """
        محاسبه پارامترهای مدل ون گوچتن.

        Args:
            alpha: پارامتر مربوط به فشار کشش (1/m).
            n: پارامتر شکل.
            theta_s: رطوبت اشباع.
            theta_r: رطوبت باقیمانده.

        Returns:
            دیکشنری شامل پارامترهای محاسبه شده.
        """
        m = 1 - 1/n
        return {"alpha": alpha, "n": n, "m": m, "theta_s": theta_s, "theta_r": theta_r}

    def calculate_h_from_theta(self, theta: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        """
        محاسبه هد (h) از روی رطوبت (theta) با استفاده از معکوس مدل ون گوچتن.
        """
        Se = (theta - params["theta_r"]) / (params["theta_s"] - params["theta_r"])
        # Avoid division by zero or log of negative numbers
        Se = np.clip(Se, 1e-6, 1.0 - 1e-6)
        h = (np.power(np.power(Se, -1.0/params["m"]) - 1.0, 1.0/params["n"]) / (-params["alpha"]))
        # Capillary pressure is negative, so h should be negative for unsaturated zone
        h = np.where(h > 0, -h, h)
        return h

    def calculate_theta_from_h(self, h: np.ndarray, params: Dict[str, float]) -> np.ndarray:
        """
        محاسبه رطوبت (theta) از روی هد (h) با استفاده از مدل ون گوچتن.
        """
        # Ensure h is negative for unsaturated calculations
        h_abs = np.abs(h)
        Se = np.power(1 + np.power(params["alpha"] * h_abs, params["n"]), -params["m"])
        theta = Se * (params["theta_s"] - params["theta_r"]) + params["theta_r"]
        return theta

    def calculate_K(self, h: np.ndarray, Ks: float, params: Dict[str, float]) -> np.ndarray:
        """
        محاسبه هدایت هیدرولیکی (K) بر اساس h و مدل ون گوچتن-مالم.
        """
        # Calculate effective saturation (Se) from h
        theta_local = self.calculate_theta_from_h(h, params)
        Se = (theta_local - params["theta_r"]) / (params["theta_s"] - params["theta_r"])
        Se = np.clip(Se, 0.0, 1.0)

        # Calculate relative permeability (kr)
        kr = np.power(Se, 0.5) * np.power(1 - np.power(1 - np.power(Se, 1/params["m"]), params["m"]), 2)
        kr = np.clip(kr, 1e-12, 1.0) # Prevent numerical issues
        return Ks * kr

    def solve_step(self, params: Dict[str, float], Ks: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        یک گام زمانی از حل معادله ریچاردز را انجام می‌دهد.
        این یک حل ساده شده است و فقط برای نمایش ایده است.
        """
        # Update K based on current h
        self.K = self.calculate_K(self.h, Ks, params)

        # Simple implicit finite difference (requires solving a system of equations in practice)
        # This is a placeholder for the actual matrix solution (e.g., using scipy.sparse.linalg.spsolve)
        # For now, we just calculate fluxes and apply a basic update.
        
        # Calculate flux between nodes (Darcy's law)
        dh_dz = np.gradient(self.h) / self.dz
        flux = -self.K * dh_dz
        
        # Simple mass balance update (not fully implicit)
        dtheta_dt = -np.gradient(flux) / self.dz
        theta_new = self.theta + self.dt * dtheta_dt
        
        # Recalculate h from new theta
        h_new = self.calculate_h_from_theta(theta_new, params)

        # Update internal state
        self.theta = theta_new
        self.h = h_new

        return self.theta.copy(), self.h.copy()


# Example usage (can be removed or moved to a test file)
if __name__ == "__main__":
    nz = 10
    depth = 1.0 # 1 meter
    dt = 3600 # 1 hour
    theta_ini = np.ones(nz) * 0.3 # Initial volumetric moisture
    h_ini = np.linspace(-100, -1000, nz) # Initial pressure head (negative)

    solver = RichardsEquationSolver(theta_ini, h_ini, depth, nz, dt)
    vg_params = solver.van_genuchten_params(alpha=1.0, n=1.5, theta_s=0.5, theta_r=0.05)
    
    print("Initial Theta:", solver.theta)
    print("Initial Head (h):", solver.h)
    
    Ks_val = 1e-5 # Saturated hydraulic conductivity (m/s)
    for i in range(5): # Run 5 time steps
        theta_new, h_new = solver.solve_step(vg_params, Ks_val)
        print(f"Step {i+1} - Theta: {theta_new}, Head (h): {h_new}")