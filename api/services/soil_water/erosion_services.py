"""
Erosion services based on the RUSLE model (Revised Universal Soil Loss Equation).

A = R * K * LS * C * P

where:
    A  = average annual soil loss (t/ha/year)
    R  = rainfall-runoff erosivity factor
    K  = soil erodibility factor
    LS = slope length and steepness factor
    C  = cover-management factor
    P  = support practice factor
"""

from dataclasses import dataclass
from typing import Literal, TypedDict, Dict

# کلاس‌های ریسک بر اساس رنج‌های متداول RUSLE (t/ha/year)
# منطق: الهام‌گرفته از طبقه‌بندی‌های tolerable / low / moderate / high / severe در RUSLE2 و راهنماهای ملی. [web:86]
ErosionRiskClass = Literal["very_low", "low", "moderate", "high", "severe"]


@dataclass
class RUSLEFactors:
    R: float   # rainfall erosivity
    K: float   # soil erodibility
    LS: float  # slope length & steepness
    C: float   # cover-management
    P: float   # support practice


class RUSLEResult(TypedDict):
    annual_soil_loss: float         # t/ha/year
    risk_class: ErosionRiskClass
    factors: Dict[str, float]


def compute_rusle(factors: RUSLEFactors) -> RUSLEResult:
    """
    Compute annual soil loss using the RUSLE equation. [web:69][web:74][web:82][web:85]

    A = R * K * LS * C * P
    """
    A = factors.R * factors.K * factors.LS * factors.C * factors.P

    # طبقه‌بندی ریسک، مقادیر پیشنهادی (t/ha/year):
    # very_low:   < 2
    # low:        2 - 6
    # moderate:   6 - 12
    # high:       12 - 25
    # severe:     > 25
    if A < 2:
        risk: ErosionRiskClass = "very_low"
    elif A < 6:
        risk = "low"
    elif A < 12:
        risk = "moderate"
    elif A < 25:
        risk = "high"
    else:
        risk = "severe"

    return {
        "annual_soil_loss": round(A, 3),
        "risk_class": risk,
        "factors": {
            "R": factors.R,
            "K": factors.K,
            "LS": factors.LS,
            "C": factors.C,
            "P": factors.P,
        },
    }