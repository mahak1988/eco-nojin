"""Heuristic agri risk models: pest, drought, flood, erosion, heat, frost.

These are transparent rule+score models suitable for MVP decision support.
Not ML substitutes for calibrated regional models; document as advisory.
"""

from __future__ import annotations

import math

from pydantic import BaseModel, Field


class RiskInput(BaseModel):
    lat: float = Field(32.6, description="Latitude")
    lon: float = Field(51.7, description="Longitude")
    soil_moisture_pct: float = Field(40.0, ge=0, le=100)
    precip_7d_mm: float = Field(10.0, ge=0)
    precip_30d_mm: float = Field(40.0, ge=0)
    et0_7d_mm: float = Field(28.0, ge=0)
    temp_max_c: float = Field(32.0)
    temp_min_c: float = Field(12.0)
    humidity_pct: float = Field(45.0, ge=0, le=100)
    wind_m_s: float = Field(3.0, ge=0)
    slope_pct: float = Field(5.0, ge=0, le=100)
    vegetation_cover_pct: float = Field(50.0, ge=0, le=100)
    crop_category: str = Field("cereal")
    days_since_rain: int = Field(5, ge=0)


class RiskItem(BaseModel):
    code: str
    name: str
    score: float  # 0-100
    level: str  # low|moderate|high|critical
    drivers: list[str]
    actions: list[str]


class RiskReport(BaseModel):
    overall_score: float
    overall_level: str
    items: list[RiskItem]
    notes: str


def _level(score: float) -> str:
    if score >= 75:
        return "critical"
    if score >= 55:
        return "high"
    if score >= 35:
        return "moderate"
    return "low"


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def score_drought(inp: RiskInput) -> RiskItem:
    # SPEI-like proxy: deficit = ET - rain
    deficit = inp.et0_7d_mm - inp.precip_7d_mm
    sm_stress = max(0.0, 45 - inp.soil_moisture_pct) * 1.5
    rain_gap = min(40.0, inp.days_since_rain * 3.0)
    score = _clamp(deficit * 1.8 + sm_stress + rain_gap)
    drivers = []
    if deficit > 10:
        drivers.append(f"7d ET0−rain deficit {deficit:.1f} mm")
    if inp.soil_moisture_pct < 35:
        drivers.append(f"low soil moisture {inp.soil_moisture_pct:.0f}%")
    if inp.days_since_rain > 7:
        drivers.append(f"{inp.days_since_rain} days since rain")
    actions = [
        "Prioritize deficit irrigation on high-value blocks",
        "Mulch / reduce canopy evaporative loss",
        "Check well yield and reservoir buffer",
    ]
    return RiskItem(
        code="drought",
        name="Drought / water stress",
        score=round(score, 1),
        level=_level(score),
        drivers=drivers or ["balanced moisture regime"],
        actions=actions,
    )


def score_flood(inp: RiskInput) -> RiskItem:
    intense = max(0.0, inp.precip_7d_mm - 40) * 1.2
    sat = max(0.0, inp.soil_moisture_pct - 70) * 1.5
    slope_factor = max(0.0, 15 - inp.slope_pct) * 0.8  # flat = more ponding
    score = _clamp(intense + sat + slope_factor)
    drivers = []
    if inp.precip_7d_mm > 40:
        drivers.append(f"heavy 7d rain {inp.precip_7d_mm:.0f} mm")
    if inp.soil_moisture_pct > 75:
        drivers.append("near-saturated soil")
    actions = [
        "Clear drainage ditches before next storm",
        "Avoid field traffic on wet soils",
        "Protect seedbeds on low-lying parcels",
    ]
    return RiskItem(
        code="flood",
        name="Flood / waterlogging",
        score=round(score, 1),
        level=_level(score),
        drivers=drivers or ["no acute flood signal"],
        actions=actions,
    )


def score_erosion(inp: RiskInput) -> RiskItem:
    # RUSLE-inspired qualitative: R (rain) * S (slope) * C (cover inverse)
    r = min(40.0, inp.precip_7d_mm * 0.5 + inp.wind_m_s * 2)
    s = min(40.0, inp.slope_pct * 1.5)
    c = max(0.0, 60 - inp.vegetation_cover_pct) * 0.7
    score = _clamp(r + s + c)
    drivers = []
    if inp.slope_pct > 8:
        drivers.append(f"slope {inp.slope_pct:.0f}%")
    if inp.vegetation_cover_pct < 40:
        drivers.append("sparse cover")
    if inp.precip_7d_mm > 25:
        drivers.append("erosive rainfall")
    actions = [
        "Contour farming / strip cropping",
        "Increase residue cover",
        "Install check dams on rills",
    ]
    return RiskItem(
        code="erosion",
        name="Soil erosion",
        score=round(score, 1),
        level=_level(score),
        drivers=drivers or ["stable surface"],
        actions=actions,
    )


def score_pest(inp: RiskInput) -> RiskItem:
    # Degree-day + humidity + crop soft factors
    heat = max(0.0, inp.temp_max_c - 28) * 2.5
    humid = max(0.0, inp.humidity_pct - 55) * 0.9
    dry_hot = max(0.0, inp.temp_max_c - 34) * (1 if inp.humidity_pct < 40 else 0.3)
    cat_boost = {"vegetable": 12, "fruit": 10, "cereal": 6, "legume": 8}.get(inp.crop_category, 5)
    score = _clamp(heat + humid + dry_hot + cat_boost)
    drivers = []
    if inp.temp_max_c >= 30:
        drivers.append(f"warm max {inp.temp_max_c:.0f}°C")
    if inp.humidity_pct >= 60:
        drivers.append(f"humidity {inp.humidity_pct:.0f}%")
    drivers.append(f"crop class {inp.crop_category}")
    actions = [
        "Scout field edges twice weekly",
        "Deploy pheromone / sticky traps",
        "Prefer selective IPM products at threshold",
    ]
    return RiskItem(
        code="pest",
        name="Pest pressure",
        score=round(score, 1),
        level=_level(score),
        drivers=drivers,
        actions=actions,
    )


def score_disease(inp: RiskInput) -> RiskItem:
    # Leaf wetness proxy: high RH + moderate temp
    leaf = 0.0
    if 15 <= inp.temp_max_c <= 28 and inp.humidity_pct >= 70:
        leaf = 35 + (inp.humidity_pct - 70)
    if inp.precip_7d_mm > 20:
        leaf += 15
    score = _clamp(leaf + max(0, inp.humidity_pct - 65) * 0.5)
    drivers = []
    if inp.humidity_pct >= 70:
        drivers.append("high humidity canopy")
    if inp.precip_7d_mm > 20:
        drivers.append("frequent wetting")
    actions = [
        "Improve airflow / prune dense canopy",
        "Avoid overhead irrigation at dusk",
        "Consider preventive biofungicide if history of blight",
    ]
    return RiskItem(
        code="disease",
        name="Disease (fungal) risk",
        score=round(score, 1),
        level=_level(score),
        drivers=drivers or ["unfavorable for infection"],
        actions=actions,
    )


def score_heat(inp: RiskInput) -> RiskItem:
    score = _clamp(max(0.0, inp.temp_max_c - 35) * 8)
    return RiskItem(
        code="heat",
        name="Heat stress",
        score=round(score, 1),
        level=_level(score),
        drivers=[f"Tmax {inp.temp_max_c:.1f}°C"] if score > 10 else ["within tolerance"],
        actions=["Shade nets for sensitive crops", "Irrigate early morning", "Avoid mid-day sprays"],
    )


def score_frost(inp: RiskInput) -> RiskItem:
    score = _clamp(max(0.0, 2 - inp.temp_min_c) * 20)
    return RiskItem(
        code="frost",
        name="Frost risk",
        score=round(score, 1),
        level=_level(score),
        drivers=[f"Tmin {inp.temp_min_c:.1f}°C"] if score > 10 else ["no frost signal"],
        actions=["Row covers / wind machines", "Delay sensitive transplanting", "Monitor pre-dawn temps"],
    )


def evaluate_risks(inp: RiskInput) -> RiskReport:
    items = [
        score_drought(inp),
        score_flood(inp),
        score_erosion(inp),
        score_pest(inp),
        score_disease(inp),
        score_heat(inp),
        score_frost(inp),
    ]
    # overall = soft-max emphasis on highest risks
    weights = [math.exp(i.score / 40) for i in items]
    overall = sum(i.score * w for i, w in zip(items, weights)) / sum(weights)
    overall = round(_clamp(overall), 1)
    return RiskReport(
        overall_score=overall,
        overall_level=_level(overall),
        items=sorted(items, key=lambda x: -x.score),
        notes=(
            "Advisory heuristic model for decision support. "
            "Calibrate thresholds with local agronomy extension data before operational use."
        ),
    )
