"""
HYDRUS-1D Soil Water Flow Simulator (Clean Room)
==================================================
Implements van Genuchten (1980) equations for unsaturated soil water flow.

Formula: theta(h) = theta_r + (theta_s - theta_r) / (1 + |alpha*h|^n)^m
         K(h) = Ks * Se^0.5 * (1 - (1 - Se^(1/m))^m)^2

Reference: van Genuchten, M.Th. (1980). A closed-form equation for predicting
           the hydraulic conductivity of unsaturated soils. SSSAJ 44(5):892-898.

Not the official HYDRUS binary. Clean Room implementation for decision support.
"""
from __future__ import annotations
import math
from typing import Any

ENGINE = "conceptual"
ENGINE_VERSION = "1.0.0"
DISCLAIMER = (
    "Clean Room implementation of van Genuchten equations. "
    "Not the official HYDRUS binary. For decision support only."
)

# Soil hydraulic parameters (van Genuchten 1980, Carsel & Parrish 1988)
SOIL_PARAMS = {
    "sand": {"theta_r": 0.045, "theta_s": 0.43, "alpha": 0.145, "n": 2.68, "Ks": 712.8},
    "loamy_sand": {"theta_r": 0.057, "theta_s": 0.41, "alpha": 0.124, "n": 2.28, "Ks": 350.2},
    "sandy_loam": {"theta_r": 0.065, "theta_s": 0.41, "alpha": 0.075, "n": 1.89, "Ks": 106.1},
    "loam": {"theta_r": 0.078, "theta_s": 0.43, "alpha": 0.036, "n": 1.56, "Ks": 24.96},
    "silt_loam": {"theta_r": 0.067, "theta_s": 0.45, "alpha": 0.020, "n": 1.41, "Ks": 10.8},
    "clay_loam": {"theta_r": 0.095, "theta_s": 0.41, "alpha": 0.019, "n": 1.31, "Ks": 6.24},
    "clay": {"theta_r": 0.068, "theta_s": 0.38, "alpha": 0.008, "n": 1.09, "Ks": 4.8},
}


def van_genuchten_theta(h: float, theta_r: float, theta_s: float, alpha: float, n: float) -> float:
    """Soil water content from pressure head (van Genuchten 1980, Eq. 2)."""
    m = 1.0 - 1.0 / n
    denom = 1.0 + abs(alpha * h) ** n
    if denom <= 0:
        return theta_r
    return theta_r + (theta_s - theta_r) / (denom ** m)


def van_genuchten_k(h: float, Ks: float, theta_r: float, theta_s: float, alpha: float, n: float) -> float:
    """Hydraulic conductivity from pressure head (van Genuchten 1980, Eq. 8)."""
    theta = van_genuchten_theta(h, theta_r, theta_s, alpha, n)
    if theta_s <= theta_r:
        return Ks
    Se = (theta - theta_r) / (theta_s - theta_r)
    Se = max(0.001, min(1.0, Se))
    m = 1.0 - 1.0 / n
    inner = 1.0 - Se ** (1.0 / m)
    if inner < 0:
        inner = 0.0
    return Ks * (Se ** 0.5) * (inner ** m) ** 2


def run_hydrus_1d(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """HYDRUS-1D style soil water balance simulation."""
    p = dict(params or {})
    soil_type = str(p.get("soil_type", "loam"))
    sp = SOIL_PARAMS.get(soil_type, SOIL_PARAMS["loam"])

    days = max(1, min(365, int(float(p.get("days", 30)))))
    irrigation_mm_day = max(0.0, float(p.get("irrigation_mm_day", 0)))
    et_mm_day = max(0.0, float(p.get("et_mm_day", 5)))
    initial_moisture = float(p.get("initial_moisture", 0.25))
    depth_cm = float(p.get("depth_cm", 100))

    current_moisture = max(sp["theta_r"], min(sp["theta_s"], initial_moisture))
    drainage_total = 0.0
    deep_perc_total = 0.0
    runoff_total = 0.0

    for day in range(days):
        # Root water uptake (simplified Feddes model)
        theta_fc = van_genuchten_theta(-330, sp["theta_r"], sp["theta_s"], sp["alpha"], sp["n"])
        available_water = max(0.0, (current_moisture - sp["theta_r"]) * depth_cm * 10.0)
        uptake = min(et_mm_day, available_water * 0.6)

        # Infiltration from irrigation
        infil = min(irrigation_mm_day, (sp["theta_s"] - current_moisture) * depth_cm * 10.0)

        # Drainage below root zone
        h_avg = -100.0 * (1.0 - current_moisture / sp["theta_s"])
        k_unsat = van_genuchten_k(h_avg, sp["Ks"], sp["theta_r"], sp["theta_s"], sp["alpha"], sp["n"])
        drainage = min(k_unsat, max(0.0, available_water * 0.1))
        drainage_total += drainage

        # Deep percolation (10% of drainage reaches below soil profile)
        deep_perc_total += drainage * 0.1

        # Water balance update
        delta = (infil - uptake - drainage) / (depth_cm * 10.0)
        current_moisture += delta
        current_moisture = max(sp["theta_r"], min(sp["theta_s"], current_moisture))

    # Soil water storage
    water_storage_mm = current_moisture * depth_cm * 10.0

    # Field capacity and wilting point
    theta_fc = van_genuchten_theta(-330, sp["theta_r"], sp["theta_s"], sp["alpha"], sp["n"])
    theta_wp = van_genuchten_theta(-15000, sp["theta_r"], sp["theta_s"], sp["alpha"], sp["n"])
    plant_available_water_mm = (theta_fc - theta_wp) * depth_cm * 10.0

    return {
        "engine": ENGINE,
        "engine_version": ENGINE_VERSION,
        "model": "HYDRUS-1D (Clean Room)",
        "citation": "van Genuchten, M.Th. (1980). SSSAJ 44(5):892-898.",
        "disclaimer": DISCLAIMER,
        "soil_type": soil_type,
        "van_genuchten_params": sp,
        "days": days,
        "initial_moisture": initial_moisture,
        "final_moisture": round(current_moisture, 4),
        "field_capacity": round(theta_fc, 4),
        "wilting_point": round(theta_wp, 4),
        "plant_available_water_mm": round(plant_available_water_mm, 1),
        "water_storage_mm": round(water_storage_mm, 1),
        "total_drainage_mm": round(drainage_total, 2),
        "deep_percolation_mm": round(deep_perc_total, 2),
        "total_irrigation_mm": round(irrigation_mm_day * days, 1),
        "water_balance_mm": round(irrigation_mm_day * days - uptake * days - drainage_total, 2),
        "completed_at": None,
    }
