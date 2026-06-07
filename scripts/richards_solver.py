"""
Richards Equation Solver for Soil Water Dynamics
=================================================
1D and 2D numerical solver for unsaturated flow using van Genuchten-Mualem model.
Fully open-source implementation using NumPy/SciPy.

References:
- van Genuchten (1980): "A closed-form equation for predicting hydraulic conductivity"
- Richards (1931): "Capillary conduction of liquids through porous mediums"
"""

import warnings
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import newton


@dataclass
class VanGenuchtenParams:
    """van Genuchten-Mualem soil hydraulic parameters"""

    theta_r: float  # Residual water content [m³/m³]
    theta_s: float  # Saturated water content [m³/m³]
    alpha: float  # Inverse of air entry suction [1/cm]
    n: float  # Pore-size distribution index [-]
    K_s: float  # Saturated hydraulic conductivity [cm/day]
    l: float = 0.5  # Pore connectivity parameter [-]

    @property
    def m(self) -> float:
        """Calculate m = 1 - 1/n"""
        return 1 - 1 / self.n


class VanGenuchtenModel:
    """van Genuchten-Mualem water retention and hydraulic conductivity model"""

    def __init__(self, params: VanGenuchtenParams):
        self.params = params

    def theta(self, h: np.ndarray) -> np.ndarray:
        """
        Calculate water content from pressure head.

        Parameters:
        -----------
        h : np.ndarray
            Pressure head [cm] (negative for unsaturated)

        Returns:
        --------
        theta : np.ndarray
            Volumetric water content [m³/m³]
        """
        p = self.params
        h = np.asarray(h)

        # Avoid division by zero
        h = np.where(h >= 0, 1e-6, h)

        Se = (1 + np.abs(p * p.alpha) ** p.n) ** (-p.m)
        return p.theta_r + Se * (p.theta_s - p.theta_r)

    def h(self, theta: np.ndarray) -> np.ndarray:
        """
        Calculate pressure head from water content (inverse).

        Parameters:
        -----------
        theta : np.ndarray
            Volumetric water content [m³/m³]

        Returns:
        --------
        h : np.ndarray
            Pressure head [cm]
        """
        p = self.params
        theta = np.asarray(theta)

        # Bounds checking
        theta = np.clip(theta, p.theta_r + 1e-6, p.theta_s - 1e-6)

        Se = (theta - p.theta_r) / (p.theta_s - p.theta_r)
        return -((Se ** (-1 / p.m) - 1) ** (1 / p.n)) / p.alpha

    def K(self, h: np.ndarray) -> np.ndarray:
        """
        Calculate hydraulic conductivity from pressure head.

        Parameters:
        -----------
        h : np.ndarray
            Pressure head [cm]

        Returns:
        --------
        K : np.ndarray
            Hydraulic conductivity [cm/day]
        """
        p = self.params
        h = np.asarray(h)

        Se = (1 + np.abs(p.alpha * h) ** p.n) ** (-p.m)
        return p.K_s * Se**p.l * (1 - (1 - Se ** (1 / p.m)) ** p.m) ** 2

    def C(self, h: np.ndarray) -> np.ndarray:
        """
        Calculate specific water capacity d(theta)/d(h).

        Parameters:
        -----------
        h : np.ndarray
            Pressure head [cm]

        Returns:
        --------
        C : np.ndarray
            Specific water capacity [1/cm]
        """
        p = self.params
        h = np.asarray(h)

        # Numerical derivative for stability
        dh = 1e-4
        return (self.theta(h + dh) - self.theta(h - dh)) / (2 * dh)


class RichardsEquation1D:
    """
    1D Richards equation solver using method of lines.

    Solves: d(theta)/dt = d/dz[K(h)*(dh/dz + 1)]

    Uses implicit time stepping for stability.
    """

    def __init__(
        self,
        vg_params: VanGenuchtenParams,
        dz: float = 1.0,  # Spatial step [cm]
        max_depth: float = 200.0,
    ):  # Domain depth [cm]
        self.vg = VanGenuchtenModel(vg_params)
        self.dz = dz
        self.z = np.arange(0, max_depth + dz, dz)  # Depth grid [cm]
        self.n_nodes = len(self.z)

    def solve(
        self,
        initial_theta: np.ndarray,
        boundary_conditions: dict,
        time_span: Tuple[float, float],
        time_step: float = 3600,  # seconds
        rainfall: Optional[np.ndarray] = None,
        et: Optional[np.ndarray] = None,
    ) -> dict:
        """
        Solve 1D Richards equation.

        Parameters:
        -----------
        initial_theta : np.ndarray
            Initial water content profile [m³/m³]
        boundary_conditions : dict
            {'top': 'flux' or 'head', 'bottom': 'free' or 'head', ...}
        time_span : tuple
            (start_time, end_time) in seconds
        time_step : float
            Output time step [seconds]
        rainfall : np.ndarray, optional
            Surface flux time series [cm/day]
        et : np.ndarray, optional
            Evapotranspiration time series [cm/day]

        Returns:
        --------
        results : dict
            {'theta': water content [time, depth],
             'h': pressure head [time, depth],
             'flux': vertical flux [time, depth]}
        """
        from scipy.integrate import solve_ivp

        # Convert initial conditions
        h_initial = self.vg.h(initial_theta)

        # Time points for output
        t_eval = np.arange(time_span[0], time_span[1] + time_step, time_step)

        def rhs(t, h_profile):
            """Right-hand side of ODE system"""
            # Calculate theta and derivatives
            theta = self.vg.theta(h_profile)
            C = self.vg.C(h_profile)
            K = self.vg.K(h_profile)

            # Avoid division by zero
            C = np.maximum(C, 1e-10)

            # Calculate dh/dz using central differences
            dh_dz = np.zeros(self.n_nodes)
            dh_dz[1:-1] = (h_profile[2:] - h_profile[:-2]) / (2 * self.dz)

            # Boundary conditions for gradient
            if boundary_conditions.get("top") == "flux":
                # Neumann BC at top
                q_top = boundary_conditions.get("top_flux", 0)
                dh_dz[0] = (q_top / K[0]) - 1
            elif boundary_conditions.get("top") == "head":
                dh_dz[0] = (boundary_conditions["top_head"] - h_profile[0]) / self.dz

            if boundary_conditions.get("bottom") == "head":
                dh_dz[-1] = (boundary_conditions["bottom_head"] - h_profile[-1]) / self.dz
            # else: free drainage (dh/dz = 0) at bottom

            # Calculate K*(dh/dz + 1)
            flux = K * (dh_dz + 1)

            # Calculate d/dz[K*(dh/dz + 1)] using central differences
            dflux_dz = np.zeros(self.n_nodes)
            dflux_dz[1:-1] = (flux[2:] - flux[:-2]) / (2 * self.dz)

            # Boundary fluxes
            if boundary_conditions.get("top") == "flux":
                dflux_dz[0] = (flux[1] - boundary_conditions.get("top_flux", 0)) / self.dz
            if boundary_conditions.get("bottom") == "head":
                dflux_dz[-1] = (boundary_conditions.get("bottom_flux", 0) - flux[-2]) / self.dz

            # Richards equation: d(theta)/dt = d/dz[K*(dh/dz + 1)]
            # Using chain rule: d(theta)/dt = C * dh/dt
            dh_dt = dflux_dz / C

            return dh_dt

        # Solve ODE system
        sol = solve_ivp(
            rhs,
            time_span,
            h_initial,
            method="BDF",  # Implicit for stiffness
            t_eval=t_eval / 86400,  # Convert to days
            vectorized=False,
        )

        if not sol.success:
            warnings.warn(f"Richards solver warning: {sol.message}")

        # Post-process results
        results = {
            "time": sol.t * 86400,  # Convert back to seconds
            "h": sol.y.T,  # [time, depth]
            "theta": self.vg.theta(sol.y.T),
            "K": self.vg.K(sol.y.T),
        }

        # Calculate fluxes
        results["flux"] = self._calculate_fluxes(results["h"], rainfall, et)

        return results

    def _calculate_fluxes(
        self, h_profile: np.ndarray, rainfall: Optional[np.ndarray], et: Optional[np.ndarray]
    ) -> np.ndarray:
        """Calculate vertical water fluxes"""
        n_time, n_depth = h_profile.shape
        flux = np.zeros((n_time, n_depth))

        for t in range(n_time):
            K = self.vg.K(h_profile[t])
            dh_dz = np.gradient(h_profile[t], self.dz)
            flux[t] = -K * (dh_dz + 1)  # Negative for downward positive

            # Apply surface boundary condition
            if rainfall is not None and t < len(rainfall):
                flux[t, 0] = rainfall[t] - (et[t] if et is not None else 0)

        return flux


class SoilWaterCalibrator:
    """Calibrate van Genuchten parameters from TDR/soil moisture data"""

    @staticmethod
    def calibrate_from_tdr(
        observed_theta: np.ndarray, observed_h: np.ndarray, initial_guess: VanGenuchtenParams
    ) -> VanGenuchtenParams:
        """
        Calibrate van Genuchten parameters against TDR measurements.

        Parameters:
        -----------
        observed_theta : np.ndarray
            Measured water contents [m³/m³]
        observed_h : np.ndarray
            Measured pressure heads [cm]
        initial_guess : VanGenuchtenParams
            Initial parameter estimates

        Returns:
        --------
        calibrated_params : VanGenuchtenParams
            Optimized parameters
        """
        from scipy.optimize import least_squares

        def residuals(params_array):
            """Calculate residuals between model and observations"""
            params = VanGenuchtenParams(*params_array)
            vg = VanGenuchtenModel(params)

            # Predict theta from h
            theta_pred = vg.theta(observed_h)

            # RMSE residuals
            return theta_pred - observed_theta

        # Parameter bounds (physically realistic)
        bounds = (
            [0.0, 0.2, 0.001, 1.1, 0.1, 0.0],  # Lower bounds
            [0.2, 0.6, 0.1, 5.0, 1000, 1.0],  # Upper bounds
        )

        # Initial guess as array
        x0 = [
            initial_guess.theta_r,
            initial_guess.theta_s,
            initial_guess.alpha,
            initial_guess.n,
            initial_guess.K_s,
            initial_guess.l,
        ]

        # Optimize
        result = least_squares(residuals, x0, bounds=bounds, method="trf")

        if not result.success:
            warnings.warn(f"Calibration warning: {result.message}")

        return VanGenuchtenParams(*result.x)
