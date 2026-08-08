"""
SEBS - Surface Energy Balance System
Implementation based on Su (2002) and extensions for energy balance equations
from typical thesis sections §1.2.3 and §2.3.

Core energy balance:
    Rn = G0 + H + λE

Net radiation, soil heat flux, sensible heat (with dry/wet limits),
evaporative fraction, and actual ET.
"""

from __future__ import annotations

import numpy as np
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass


# Physical constants
STEFAN_BOLTZMANN = 5.670374419e-8  # W m-2 K-4
VON_KARMAN = 0.41
GRAVITY = 9.80665  # m s-2
CP_AIR = 1004.0  # J kg-1 K-1  specific heat of dry air
R_DRY = 287.05  # J kg-1 K-1
LATENT_HEAT_VAP = 2.45e6  # J kg-1  approx at 20°C
PSYCHROMETRIC = 0.665e-3  # kPa °C-1 approx (will be recalculated)


@dataclass
class SEBSInputs:
    """Required remote-sensing and meteorological inputs for SEBS."""
    albedo: np.ndarray          # surface albedo [-]
    emissivity: np.ndarray      # surface emissivity [-]
    lst: np.ndarray             # land surface temperature [K]
    ndvi: np.ndarray            # NDVI [-]
    ndvi_min: float = 0.05
    ndvi_max: float = 0.95
    r_swd: np.ndarray = None    # downward shortwave radiation [W m-2]
    r_lwd: np.ndarray = None    # downward longwave radiation [W m-2]
    ta: np.ndarray = None       # air temperature at reference height [K]
    ea: np.ndarray = None       # actual vapour pressure [kPa]
    u: np.ndarray = None        # wind speed at reference height [m s-1]
    z: float = 2.0              # reference height [m]
    p: float = 101.3            # atmospheric pressure [kPa]
    h_canopy: Optional[np.ndarray] = None  # canopy height [m]
    lai: Optional[np.ndarray] = None       # leaf area index [-]


@dataclass
class SEBSOutputs:
    rn: np.ndarray
    g0: np.ndarray
    h: np.ndarray
    le: np.ndarray
    ef: np.ndarray              # evaporative fraction
    et_mm: np.ndarray           # daily ET equivalent [mm d-1] (approx)
    h_dry: np.ndarray
    h_wet: np.ndarray
    u_star: np.ndarray
    z0m: np.ndarray
    z0h: np.ndarray


def fractional_vegetation_cover(ndvi: np.ndarray, ndvi_min: float = 0.05, ndvi_max: float = 0.95) -> np.ndarray:
    """fc from NDVI (common linear scaling)."""
    fc = (ndvi - ndvi_min) / (ndvi_max - ndvi_min)
    return np.clip(fc, 0.0, 1.0)


def net_radiation(
    albedo: np.ndarray,
    emissivity: np.ndarray,
    lst: np.ndarray,
    r_swd: np.ndarray,
    r_lwd: np.ndarray,
) -> np.ndarray:
    """
    Rn = (1 - α) Rswd + ε Rlwd - ε σ T0^4
    § energy balance net radiation.
    """
    r_ns = (1.0 - albedo) * r_swd
    r_nl = emissivity * r_lwd - emissivity * STEFAN_BOLTZMANN * lst ** 4
    return r_ns + r_nl


def soil_heat_flux(rn: np.ndarray, fc: np.ndarray, gamma_c: float = 0.05, gamma_s: float = 0.315) -> np.ndarray:
    """
    G0 = Rn * [Γc + (1 - fc) * (Γs - Γc)]
    Su (2002) parameterization.
    """
    return rn * (gamma_c + (1.0 - fc) * (gamma_s - gamma_c))


def roughness_lengths(
    ndvi: np.ndarray,
    ndvi_max: float = 0.95,
    h_canopy: Optional[np.ndarray] = None,
    fc: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Momentum and heat roughness lengths.
    Simplified Su-type model + displacement height.
    z0m ≈ 0.005 + 0.5 * (NDVI/NDVImax)^2.5   (empirical)
    z0h = z0m / exp(kB-1)
    """
    if h_canopy is None:
        # empirical canopy height from NDVI
        h_canopy = 0.1 + 2.5 * np.clip(ndvi, 0, 1) ** 2

    z0m = 0.005 + 0.5 * (np.clip(ndvi / ndvi_max, 0, 1) ** 2.5)
    z0m = np.minimum(z0m, 0.1 * h_canopy)  # physical bound

    # kB-1 simplified (full model uses Cd, Ct, etc.)
    # typical values 2–8; use vegetation-dependent
    if fc is None:
        fc = fractional_vegetation_cover(ndvi)
    kb_inv = 2.0 + 6.0 * (1.0 - fc)  # higher for bare soil
    z0h = z0m / np.exp(kb_inv)

    d0 = 0.66 * h_canopy  # zero-plane displacement
    return z0m, z0h, d0


def monin_obukhov_length(u_star: np.ndarray, h: np.ndarray, ta: np.ndarray, rho: np.ndarray) -> np.ndarray:
    """L = - (ρ Cp u*³ θv) / (k g H)   (θv ≈ ta for simplicity)"""
    # avoid division by zero
    h_safe = np.where(np.abs(h) < 1e-6, 1e-6, h)
    L = - (rho * CP_AIR * u_star ** 3 * ta) / (VON_KARMAN * GRAVITY * h_safe)
    return L


def stability_correction_momentum(zeta: np.ndarray) -> np.ndarray:
    """Ψm(ζ)  – Paulson / Högström form."""
    psi = np.zeros_like(zeta)
    # unstable
    mask_u = zeta < 0
    x = (1.0 - 16.0 * zeta[mask_u]) ** 0.25
    psi[mask_u] = (
        2.0 * np.log((1.0 + x) / 2.0)
        + np.log((1.0 + x ** 2) / 2.0)
        - 2.0 * np.arctan(x)
        + np.pi / 2.0
    )
    # stable
    mask_s = zeta >= 0
    psi[mask_s] = -5.0 * zeta[mask_s]
    return psi


def stability_correction_heat(zeta: np.ndarray) -> np.ndarray:
    """Ψh(ζ)"""
    psi = np.zeros_like(zeta)
    mask_u = zeta < 0
    x = (1.0 - 16.0 * zeta[mask_u]) ** 0.25
    psi[mask_u] = 2.0 * np.log((1.0 + x ** 2) / 2.0)
    mask_s = zeta >= 0
    psi[mask_s] = -5.0 * zeta[mask_s]
    return psi


def sensible_heat_flux(
    ta: np.ndarray,
    lst: np.ndarray,
    u: np.ndarray,
    z: float,
    z0m: np.ndarray,
    z0h: np.ndarray,
    d0: np.ndarray,
    p: float = 101.3,
    max_iter: int = 20,
    tol: float = 0.1,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Iterative solution for H and u* under Monin-Obukhov similarity.
    H = ρ Cp (θ0 - θa) / rah
    """
    # potential temperatures (approx, ignore pressure correction for simplicity)
    theta0 = lst
    theta_a = ta

    # air density
    rho = p * 1000.0 / (R_DRY * ta)  # kg m-3  (p in kPa)

    # initial guess neutral
    u_star = VON_KARMAN * u / np.log((z - d0) / z0m)
    u_star = np.maximum(u_star, 0.01)

    h = np.zeros_like(ta)

    for _ in range(max_iter):
        L = monin_obukhov_length(u_star, h, ta, rho)
        zeta = (z - d0) / L
        zeta0m = z0m / L
        zeta0h = z0h / L

        psi_m = stability_correction_momentum(zeta) - stability_correction_momentum(zeta0m)
        psi_h = stability_correction_heat(zeta) - stability_correction_heat(zeta0h)

        # friction velocity
        u_star_new = VON_KARMAN * u / (np.log((z - d0) / z0m) - psi_m)
        u_star_new = np.maximum(u_star_new, 0.01)

        # aerodynamic resistance
        rah = (np.log((z - d0) / z0h) - psi_h) / (VON_KARMAN * u_star_new)
        rah = np.maximum(rah, 1.0)

        h_new = rho * CP_AIR * (theta0 - theta_a) / rah

        if np.nanmax(np.abs(h_new - h)) < tol:
            u_star = u_star_new
            h = h_new
            break
        u_star = 0.5 * (u_star + u_star_new)  # under-relaxation
        h = 0.5 * (h + h_new)

    return h, u_star


def wet_limit_sensible_heat(
    rn: np.ndarray,
    g0: np.ndarray,
    ta: np.ndarray,
    ea: np.ndarray,
    rah: np.ndarray,
    p: float = 101.3,
) -> np.ndarray:
    """
    Hw from Penman-type combination equation at wet limit
    (internal resistance → 0).
    Classic SEBS form:
        Hw = [ (Rn-G0) - ρ Cp (es-ea) / (rah · γ) ] / (1 + Δ/γ)
    Clipped so that LE_wet ≥ 0 ⇒ Hw ≤ Rn-G0.
    """
    t_c = ta - 273.15
    es = 0.6108 * np.exp(17.27 * t_c / (t_c + 237.3))  # kPa
    delta = 4098.0 * es / (t_c + 237.3) ** 2          # kPa °C-1
    gamma = 0.665e-3 * p                              # kPa °C-1
    rho = p * 1000.0 / (R_DRY * ta)

    available = rn - g0
    hw = (available - (rho * CP_AIR * (es - ea)) / (rah * gamma)) / (1.0 + delta / gamma)
    # physical bounds
    hw = np.minimum(hw, available)   # LE_wet ≥ 0
    hw = np.maximum(hw, -0.5 * np.abs(available))  # mild negative allowed
    return hw


def dry_limit_sensible_heat(rn: np.ndarray, g0: np.ndarray) -> np.ndarray:
    """Hdry = Rn - G0   (λE = 0)"""
    return rn - g0


def evaporative_fraction(h: np.ndarray, h_dry: np.ndarray, h_wet: np.ndarray, le_wet: np.ndarray, rn: np.ndarray, g0: np.ndarray) -> np.ndarray:
    """
    Λr = 1 - (H - Hw) / (Hd - Hw)
    Λ  = Λr * λEw / (Rn - G0)
    """
    denom = h_dry - h_wet
    denom = np.where(np.abs(denom) < 1e-3, 1e-3, denom)
    lambda_r = 1.0 - (h - h_wet) / denom
    lambda_r = np.clip(lambda_r, 0.0, 1.0)

    available = rn - g0
    available = np.where(np.abs(available) < 1e-3, 1e-3, available)
    ef = lambda_r * le_wet / available
    return np.clip(ef, 0.0, 1.0)


def run_sebs(inputs: SEBSInputs) -> SEBSOutputs:
    """
    Full SEBS pipeline.
    Returns energy balance components and evaporative fraction.
    """
    fc = fractional_vegetation_cover(inputs.ndvi, inputs.ndvi_min, inputs.ndvi_max)

    rn = net_radiation(
        inputs.albedo,
        inputs.emissivity,
        inputs.lst,
        inputs.r_swd,
        inputs.r_lwd,
    )
    g0 = soil_heat_flux(rn, fc)

    z0m, z0h, d0 = roughness_lengths(
        inputs.ndvi, inputs.ndvi_max, inputs.h_canopy, fc
    )

    h, u_star = sensible_heat_flux(
        inputs.ta,
        inputs.lst,
        inputs.u,
        inputs.z,
        z0m,
        z0h,
        d0,
        inputs.p,
    )

    # aerodynamic resistance for wet limit (approx from last iteration)
    # recompute roughly
    L = monin_obukhov_length(u_star, h, inputs.ta, inputs.p * 1000 / (R_DRY * inputs.ta))
    zeta = (inputs.z - d0) / L
    psi_h = stability_correction_heat(zeta) - stability_correction_heat(z0h / L)
    rah = (np.log((inputs.z - d0) / z0h) - psi_h) / (VON_KARMAN * u_star)
    rah = np.maximum(rah, 1.0)

    h_dry = dry_limit_sensible_heat(rn, g0)
    h_wet = wet_limit_sensible_heat(rn, g0, inputs.ta, inputs.ea, rah, inputs.p)

    le_wet = rn - g0 - h_wet
    ef = evaporative_fraction(h, h_dry, h_wet, le_wet, rn, g0)

    le = ef * (rn - g0)
    # daily ET approx (assuming representative instantaneous flux → 24h)
    # more accurate methods use EF constancy assumption
    et_mm = le * 86400.0 / LATENT_HEAT_VAP  # mm d-1 if le is daily mean

    return SEBSOutputs(
        rn=rn,
        g0=g0,
        h=h,
        le=le,
        ef=ef,
        et_mm=et_mm,
        h_dry=h_dry,
        h_wet=h_wet,
        u_star=u_star,
        z0m=z0m,
        z0h=z0h,
    )


# ---------------------------------------------------------------------------
# Convenience vectorized / single-pixel helpers
# ---------------------------------------------------------------------------

def sebs_single_pixel(
    albedo: float,
    emissivity: float,
    lst: float,
    ndvi: float,
    r_swd: float,
    r_lwd: float,
    ta: float,
    ea: float,
    u: float,
    z: float = 2.0,
    p: float = 101.3,
) -> Dict[str, float]:
    """Run SEBS for a single pixel and return a dictionary of results."""
    inp = SEBSInputs(
        albedo=np.array([albedo]),
        emissivity=np.array([emissivity]),
        lst=np.array([lst]),
        ndvi=np.array([ndvi]),
        r_swd=np.array([r_swd]),
        r_lwd=np.array([r_lwd]),
        ta=np.array([ta]),
        ea=np.array([ea]),
        u=np.array([u]),
        z=z,
        p=p,
    )
    out = run_sebs(inp)
    return {
        "Rn": float(out.rn[0]),
        "G0": float(out.g0[0]),
        "H": float(out.h[0]),
        "LE": float(out.le[0]),
        "EF": float(out.ef[0]),
        "ET_mm": float(out.et_mm[0]),
        "H_dry": float(out.h_dry[0]),
        "H_wet": float(out.h_wet[0]),
        "u_star": float(out.u_star[0]),
    }


if __name__ == "__main__":
    # Quick self-test with typical midday values
    res = sebs_single_pixel(
        albedo=0.18,
        emissivity=0.97,
        lst=310.0,
        ndvi=0.55,
        r_swd=800.0,
        r_lwd=350.0,
        ta=300.0,
        ea=1.5,
        u=3.0,
    )
    print("SEBS single-pixel test:")
    for k, v in res.items():
        print(f"  {k:8s}: {v:8.2f}")
