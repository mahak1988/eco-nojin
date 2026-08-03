"""SCS Curve Number runoff (USDA NRCS TR-55).

Reference: USDA Natural Resources Conservation Service, Technical Release 55.
"""
from __future__ import annotations


def potential_retention(cn: float) -> float:
    """Maximum potential retention S [mm]."""
    cn = max(1.0, min(100.0, float(cn)))
    return 25400.0 / cn - 254.0


def adjust_cn_amc(cn_ii: float, amc: str = "II") -> float:
    """Adjust CN from AMC-II to AMC-I or AMC-III."""
    cn = max(1.0, min(100.0, float(cn_ii)))
    amc = (amc or "II").upper()
    if amc == "I":
        return cn / (2.281 - 0.01281 * cn)
    if amc == "III":
        return cn / (0.427 + 0.00573 * cn)
    return cn


def calculate_runoff(rainfall_mm: float, cn: float, amc: str = "II") -> float:
    """Direct runoff Q [mm]. Zero when P ≤ Ia (Ia = 0.2·S)."""
    p = max(0.0, float(rainfall_mm))
    cn_eff = adjust_cn_amc(cn, amc)
    s = potential_retention(cn_eff)
    ia = 0.2 * s
    if p <= ia:
        return 0.0
    return float((p - ia) ** 2 / (p - ia + s))
