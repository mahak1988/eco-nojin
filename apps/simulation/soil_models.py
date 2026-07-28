"""
Soil process models (open implementations).

1. RUSLE2-style annual soil loss: A = R·K·LS·C·P
2. Simple multi-layer moisture / SOC profile snapshot
3. Bulk density & available water capacity from texture (Saxton-style proxy)

Not official USDA RUSLE2 or EPIC binaries.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any


def run_rusle2(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    R = float(p.get("R", p.get("rainfall_erosivity", 150.0)))  # MJ·mm/(ha·h·y)
    K = float(p.get("K", p.get("soil_erodibility", 0.32)))  # t·ha·h/(ha·MJ·mm)
    L = float(p.get("slope_length_m", 50.0))
    S_pct = float(p.get("slope_pct", 5.0))
    # LS factor (Wischmeier-ish)
    theta = math.atan(S_pct / 100.0)
    m = 0.5 if S_pct >= 5 else 0.4 if S_pct >= 3 else 0.3
    LS = ((L / 22.1) ** m) * (65.41 * math.sin(theta) ** 2 + 4.56 * math.sin(theta) + 0.065)
    C = float(p.get("C", p.get("cover_factor", 0.2)))
    P = float(p.get("P", p.get("support_practice", 0.8)))
    A = R * K * LS * C * P  # t/ha/year

    # monthly distribution (erosivity seasonality)
    monthly = []
    for t in range(12):
        seasonal = 1.0 + 0.75 * math.sin(2 * math.pi * t / 12.0 - math.pi / 3.0)
        monthly.append(round(max(0.0, A / 12.0 * seasonal), 3))

    risk = "low" if A < 5 else "moderate" if A < 15 else "high" if A < 30 else "severe"

    return {
        "model": "rusle2_proxy",
        "citation": "RUSLE A=R·K·LS·C·P (USLE/RUSLE factors; not USDA RUSLE2 software)",
        "inputs": {
            "R": R,
            "K": K,
            "slope_length_m": L,
            "slope_pct": S_pct,
            "LS": round(LS, 4),
            "C": C,
            "P": P,
        },
        "outputs": {
            "A_t_ha_year": round(A, 3),
            "risk_class": risk,
            "monthly_t_ha": monthly,
        },
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }


def texture_hydrology(sand: float, silt: float, clay: float) -> dict[str, float]:
    """Saxton-like AWC / BD proxies from texture fractions (%)."""
    s, si, c = sand / 100.0, silt / 100.0, clay / 100.0
    # crude bulk density
    bd = 1.6 - 0.004 * clay  # g/cm3
    bd = max(1.1, min(1.7, bd))
    # field capacity / WP proxies
    fc = 0.1 + 0.004 * clay + 0.001 * silt
    wp = 0.04 + 0.0035 * clay
    awc = max(0.05, fc - wp)  # cm3/cm3
    return {
        "bulk_density_g_cm3": round(bd, 3),
        "fc_vol": round(fc, 3),
        "wp_vol": round(wp, 3),
        "awc_vol": round(awc, 3),
        "awc_mm_per_m": round(awc * 1000.0, 1),
    }


def run_soil_profile(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Layered soil profile: moisture + SOC density."""
    p = params or {}
    layers_cm = p.get("layers_cm") or [10, 20, 30, 40]
    sand = float(p.get("sand_pct", 40))
    silt = float(p.get("silt_pct", 35))
    clay = float(p.get("clay_pct", 25))
    hyd = texture_hydrology(sand, silt, clay)
    soc_surface = float(p.get("soc_surface_pct", 1.2))
    moisture_frac = float(p.get("moisture_frac", 0.55))  # fraction of AWC filled

    layers = []
    depth = 0.0
    for i, th in enumerate(layers_cm):
        th = float(th)
        depth += th
        # SOC declines with depth
        soc_pct = soc_surface * math.exp(-depth / 40.0)
        awc_mm = hyd["awc_vol"] * th * 10.0  # th in cm → mm water
        water_mm = awc_mm * moisture_frac * (0.9 + 0.1 * (1 if i == 0 else 0.85))
        layers.append(
            {
                "layer": i + 1,
                "thickness_cm": th,
                "depth_bottom_cm": depth,
                "soc_pct": round(soc_pct, 3),
                "water_mm": round(water_mm, 2),
                "awc_mm": round(awc_mm, 2),
            }
        )

    return {
        "model": "soil_profile_snapshot",
        "citation": "Texture→AWC proxy (Saxton-inspired) + exponential SOC depth",
        "texture": {"sand_pct": sand, "silt_pct": silt, "clay_pct": clay},
        "hydrology": hyd,
        "layers": layers,
        "total_awc_mm": round(sum(x["awc_mm"] for x in layers), 1),
        "total_water_mm": round(sum(x["water_mm"] for x in layers), 1),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
