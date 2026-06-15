"""
Comprehensive Scientific Models Service
Contains 40 mathematical models for Hydroma Nojin engineering calculations.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import math


# ==========================================
# Base Models (Input/Output)
# ==========================================
class ModelInput(BaseModel):
    parameters: Dict[str, float]
    project_id: Optional[int] = None

class ModelOutput(BaseModel):
    success: bool
    model_name: str
    category: str
    result: Dict[str, Any]
    formula: str
    interpretation: str


# ==========================================
# 1. HYDROLOGY MODELS (10)
# ==========================================

# 1.1 Darcy's Law
class DarcyInput(BaseModel):
    k: float = Field(..., description="Hydraulic conductivity (m/day)", gt=0)
    area: float = Field(..., description="Cross-sectional area (m²)", gt=0)
    head_difference: float = Field(..., description="Hydraulic head difference (m)", ge=0)
    length: float = Field(..., description="Flow path length (m)", gt=0)

def calculate_darcy(data: DarcyInput) -> ModelOutput:
    gradient = data.head_difference / data.length
    discharge_m3_day = data.k * data.area * gradient
    discharge_l_sec = (discharge_m3_day * 1000) / 86400
    return ModelOutput(
        success=True,
        model_name="Darcy's Law",
        category="Hydrology",
        result={
            "hydraulic_gradient": round(gradient, 4),
            "discharge_m3_per_day": round(discharge_m3_day, 4),
            "discharge_l_per_sec": round(discharge_l_sec, 4),
        },
        formula="Q = K × A × (Δh / L)",
        interpretation=f"Groundwater flow rate is {round(discharge_m3_day, 2)} m³/day"
    )

# 1.2 Manning's Equation
class ManningInput(BaseModel):
    n: float = Field(..., description="Manning's roughness coefficient", gt=0)
    hydraulic_radius: float = Field(..., description="Hydraulic radius (m)", gt=0)
    slope: float = Field(..., description="Channel slope (m/m)", gt=0)
    area: float = Field(..., description="Cross-sectional area (m²)", gt=0)

def calculate_manning(data: ManningInput) -> ModelOutput:
    velocity = (1 / data.n) * (data.hydraulic_radius ** (2/3)) * (data.slope ** 0.5)
    discharge_m3_sec = velocity * data.area
    discharge_l_sec = discharge_m3_sec * 1000
    return ModelOutput(
        success=True,
        model_name="Manning's Equation",
        category="Hydrology",
        result={
            "velocity_m_per_sec": round(velocity, 4),
            "discharge_m3_per_sec": round(discharge_m3_sec, 4),
            "discharge_l_per_sec": round(discharge_l_sec, 4),
        },
        formula="V = (1/n) × R^(2/3) × S^(1/2), Q = V × A",
        interpretation=f"Flow velocity is {round(velocity, 2)} m/s"
    )

# 1.3 SCS Curve Number
class SCSInput(BaseModel):
    curve_number: float = Field(..., description="SCS Curve Number (0-100)", ge=0, le=100)
    rainfall_mm: float = Field(..., description="Rainfall depth (mm)", gt=0)
    initial_abstraction_ratio: float = Field(0.2, description="Ia/P ratio (default 0.2)", ge=0, le=1)

def calculate_scs(data: SCSInput) -> ModelOutput:
    S = (25400 / data.curve_number) - 254  # Potential retention (mm)
    Ia = data.initial_abstraction_ratio * S  # Initial abstraction
    if data.rainfall_mm <= Ia:
        runoff = 0
    else:
        runoff = ((data.rainfall_mm - Ia) ** 2) / (data.rainfall_mm - Ia + S)
    runoff_coefficient = runoff / data.rainfall_mm if data.rainfall_mm > 0 else 0
    return ModelOutput(
        success=True,
        model_name="SCS Curve Number",
        category="Hydrology",
        result={
            "potential_retention_mm": round(S, 2),
            "initial_abstraction_mm": round(Ia, 2),
            "runoff_mm": round(runoff, 2),
            "runoff_coefficient": round(runoff_coefficient, 4),
        },
        formula="Q = (P - Ia)² / (P - Ia + S), S = 25400/CN - 254",
        interpretation=f"Runoff depth is {round(runoff, 2)} mm"
    )

# 1.4 Muskingum Routing
class MuskingumInput(BaseModel):
    inflow_1: float = Field(..., description="Inflow at time 1 (m³/s)", gt=0)
    inflow_2: float = Field(..., description="Inflow at time 2 (m³/s)", gt=0)
    outflow_1: float = Field(..., description="Outflow at time 1 (m³/s)", gt=0)
    K: float = Field(..., description="Travel time constant (hours)", gt=0)
    x: float = Field(..., description="Weighting factor (0-0.5)", ge=0, le=0.5)

def calculate_muskingum(data: MuskingumInput) -> ModelOutput:
    C0 = (-2 * data.K * data.x + 2) / (2 * data.K + 2)
    C1 = (2 * data.K * data.x + 2) / (2 * data.K + 2)
    C2 = (2 * data.K - 2) / (2 * data.K + 2)
    outflow_2 = C0 * data.inflow_2 + C1 * data.inflow_1 + C2 * data.outflow_1
    return ModelOutput(
        success=True,
        model_name="Muskingum Routing",
        category="Hydrology",
        result={
            "C0": round(C0, 4),
            "C1": round(C1, 4),
            "C2": round(C2, 4),
            "outflow_2_m3_per_sec": round(outflow_2, 4),
            "storage_m3": round((data.inflow_1 + data.inflow_2 - data.outflow_1 - outflow_2) * data.K * 3600 / 2, 2),
        },
        formula="O₂ = C₀×I₂ + C₁×I₁ + C₂×O₁",
        interpretation=f"Outflow at time 2 is {round(outflow_2, 2)} m³/s"
    )

# 1.5 Rational Method
class RationalInput(BaseModel):
    runoff_coefficient: float = Field(..., description="Runoff coefficient (0-1)", gt=0, le=1)
    rainfall_intensity: float = Field(..., description="Rainfall intensity (mm/hr)", gt=0)
    area_hectares: float = Field(..., description="Catchment area (hectares)", gt=0)

def calculate_rational(data: RationalInput) -> ModelOutput:
    peak_discharge_m3_sec = (data.runoff_coefficient * data.rainfall_intensity * data.area_hectares) / 360
    peak_discharge_l_sec = peak_discharge_m3_sec * 1000
    return ModelOutput(
        success=True,
        model_name="Rational Method",
        category="Hydrology",
        result={
            "peak_discharge_m3_per_sec": round(peak_discharge_m3_sec, 4),
            "peak_discharge_l_per_sec": round(peak_discharge_l_sec, 4),
        },
        formula="Q = C × I × A / 360",
        interpretation=f"Peak discharge is {round(peak_discharge_m3_sec, 3)} m³/s"
    )

# 1.6 Theis Equation
class TheisInput(BaseModel):
    pumping_rate: float = Field(..., description="Pumping rate (m³/day)", gt=0)
    transmissivity: float = Field(..., description="Aquifer transmissivity (m²/day)", gt=0)
    storativity: float = Field(..., description="Storativity (dimensionless)", gt=0, le=1)
    time_days: float = Field(..., description="Time since pumping started (days)", gt=0)
    distance: float = Field(..., description="Distance from well (m)", gt=0)

def calculate_theis(data: TheisInput) -> ModelOutput:
    u = (data.distance ** 2 * data.storativity) / (4 * data.transmissivity * data.time_days)
    # Approximate well function W(u) using series expansion for small u
    if u < 0.01:
        W_u = -0.5772 - math.log(u) + u - (u**2)/(2*2) + (u**3)/(3*6)
    else:
        W_u = math.exp(-u) / u
    drawdown = (data.pumping_rate / (4 * math.pi * data.transmissivity)) * W_u
    return ModelOutput(
        success=True,
        model_name="Theis Equation",
        category="Hydrology",
        result={
            "u_dimensionless": round(u, 6),
            "well_function_W_u": round(W_u, 4),
            "drawdown_m": round(drawdown, 4),
        },
        formula="s = (Q / 4πT) × W(u), u = r²S / 4Tt",
        interpretation=f"Drawdown at {data.distance}m is {round(drawdown, 2)}m"
    )

# 1.7 Cooper-Jacob
class CooperJacobInput(BaseModel):
    pumping_rate: float = Field(..., description="Pumping rate (m³/day)", gt=0)
    transmissivity: float = Field(..., description="Transmissivity (m²/day)", gt=0)
    time_days: float = Field(..., description="Time (days)", gt=0)
    distance: float = Field(..., description="Distance (m)", gt=0)
    storativity: float = Field(..., description="Storativity", gt=0, le=1)

def calculate_cooper_jacob(data: CooperJacobInput) -> ModelOutput:
    u = (data.distance ** 2 * data.storativity) / (4 * data.transmissivity * data.time_days)
    if u < 0.01:
        W_u = -0.5772 - math.log(u)
    else:
        W_u = math.exp(-u) / u
    drawdown = (data.pumping_rate / (4 * math.pi * data.transmissivity)) * W_u
    return ModelOutput(
        success=True,
        model_name="Cooper-Jacob",
        category="Hydrology",
        result={
            "u": round(u, 6),
            "W_u": round(W_u, 4),
            "drawdown_m": round(drawdown, 4),
        },
        formula="s = (Q / 4πT) × W(u)",
        interpretation=f"Drawdown is {round(drawdown, 2)}m"
    )

# 1.8 Dupuit-Forchheimer
class DupuitInput(BaseModel):
    k: float = Field(..., description="Hydraulic conductivity (m/day)", gt=0)
    upstream_head: float = Field(..., description="Upstream head (m)", gt=0)
    downstream_head: float = Field(..., description="Downstream head (m)", gt=0)
    length: float = Field(..., description="Flow length (m)", gt=0)
    width: float = Field(..., description="Dam width (m)", gt=0)

def calculate_dupuit(data: DupuitInput) -> ModelOutput:
    q = (data.k / (2 * data.length)) * (data.upstream_head**2 - data.downstream_head**2)
    Q = q * data.width
    return ModelOutput(
        success=True,
        model_name="Dupuit-Forchheimer",
        category="Hydrology",
        result={
            "unit_discharge_m2_per_day": round(q, 4),
            "total_discharge_m3_per_day": round(Q, 4),
        },
        formula="q = (K / 2L) × (h₁² - h₂²)",
        interpretation=f"Seepage through dam is {round(Q, 2)} m³/day"
    )

# 1.9 Kirpich Time of Concentration
class KirpichInput(BaseModel):
    length_m: float = Field(..., description="Max flow length (m)", gt=0)
    elevation_diff_m: float = Field(..., description="Elevation difference (m)", gt=0)

def calculate_kirpich(data: KirpichInput) -> ModelOutput:
    tc_minutes = 0.0195 * (data.length_m ** 0.77) * ((data.elevation_diff_m / data.length_m) ** -0.385)
    tc_hours = tc_minutes / 60
    return ModelOutput(
        success=True,
        model_name="Kirpich",
        category="Hydrology",
        result={
            "time_of_concentration_min": round(tc_minutes, 2),
            "time_of_concentration_hr": round(tc_hours, 3),
        },
        formula="tc = 0.0195 × L^0.77 × S^-0.385",
        interpretation=f"Time of concentration is {round(tc_minutes, 1)} minutes"
    )

# 1.10 Chow Infiltration
class ChowInput(BaseModel):
    K: float = Field(..., description="Basic infiltration rate (mm/hr)", gt=0)
    theta: float = Field(..., description="Decay constant", gt=0)
    time_hr: float = Field(..., description="Time (hours)", gt=0)

def calculate_chow(data: ChowInput) -> ModelOutput:
    f = data.K + data.theta * math.exp(-data.time_hr)
    cumulative = data.K * data.time_hr + data.theta * (1 - math.exp(-data.time_hr))
    return ModelOutput(
        success=True,
        model_name="Chow Infiltration",
        category="Hydrology",
        result={
            "infiltration_rate_mm_per_hr": round(f, 4),
            "cumulative_infiltration_mm": round(cumulative, 4),
        },
        formula="f = K + θ × e^(-t)",
        interpretation=f"Infiltration rate is {round(f, 2)} mm/hr"
    )


# ==========================================
# 2. SOIL EROSION MODELS (8)
# ==========================================

# 2.1 RUSLE
class RUSLEInput(BaseModel):
    r_factor: float = Field(..., description="Rainfall erosivity (R)", ge=0)
    k_factor: float = Field(..., description="Soil erodibility (K)", ge=0)
    ls_factor: float = Field(..., description="Topographic factor (LS)", ge=0)
    c_factor: float = Field(..., description="Cover management (C)", ge=0, le=1)
    p_factor: float = Field(..., description="Support practice (P)", ge=0, le=1)

def calculate_rusle(data: RUSLEInput) -> ModelOutput:
    soil_loss = data.r_factor * data.k_factor * data.ls_factor * data.c_factor * data.p_factor
    if soil_loss < 2: severity = "Very Low (Sustainable)"
    elif soil_loss < 5: severity = "Low"
    elif soil_loss < 10: severity = "Moderate"
    elif soil_loss < 20: severity = "High"
    else: severity = "Very High (Critical)"
    return ModelOutput(
        success=True,
        model_name="RUSLE",
        category="Soil Erosion",
        result={
            "annual_soil_loss_tons_per_ha_yr": round(soil_loss, 2),
            "severity": severity,
        },
        formula="A = R × K × LS × C × P",
        interpretation=f"Annual soil loss is {round(soil_loss, 2)} tons/ha/yr ({severity})"
    )

# 2.2 MUSLE
class MUSLEInput(BaseModel):
    runoff_volume: float = Field(..., description="Runoff volume (m³)", gt=0)
    peak_flow: float = Field(..., description="Peak flow rate (m³/s)", gt=0)
    k_factor: float = Field(..., description="Soil erodibility (K)", ge=0)
    ls_factor: float = Field(..., description="Topographic factor (LS)", ge=0)
    c_factor: float = Field(..., description="Cover (C)", ge=0, le=1)
    p_factor: float = Field(..., description="Practice (P)", ge=0, le=1)

def calculate_musle(data: MUSLEInput) -> ModelOutput:
    sediment = 11.8 * ((data.runoff_volume * data.peak_flow) ** 0.56) * data.k_factor * data.ls_factor * data.c_factor * data.p_factor
    return ModelOutput(
        success=True,
        model_name="MUSLE",
        category="Soil Erosion",
        result={
            "sediment_yield_tons": round(sediment, 2),
        },
        formula="Y = 11.8 × (Q × qp)^0.56 × K × LS × C × P",
        interpretation=f"Sediment yield is {round(sediment, 2)} tons"
    )

# 2.3 USLE
class USLEInput(BaseModel):
    r: float = Field(..., ge=0)
    k: float = Field(..., ge=0)
    ls: float = Field(..., ge=0)
    c: float = Field(..., ge=0, le=1)
    p: float = Field(..., ge=0, le=1)

def calculate_usle(data: USLEInput) -> ModelOutput:
    A = data.r * data.k * data.ls * data.c * data.p
    return ModelOutput(
        success=True, model_name="USLE", category="Soil Erosion",
        result={"soil_loss_tons_per_ha_yr": round(A, 2)},
        formula="A = R × K × LS × C × P",
        interpretation=f"Soil loss is {round(A, 2)} tons/ha/yr"
    )

# 2.4 WEPP (Simplified)
class WEPPInput(BaseModel):
    slope_steepness: float = Field(..., description="Slope steepness (%)", gt=0)
    slope_length: float = Field(..., description="Slope length (m)", gt=0)
    soil_erodibility: float = Field(..., description="Soil erodibility", gt=0)
    cover: float = Field(..., description="Cover fraction", ge=0, le=1)

def calculate_wepp(data: WEPPInput) -> ModelOutput:
    erosion = data.soil_erodibility * data.slope_steepness * data.slope_length * (1 - data.cover) * 0.5
    return ModelOutput(
        success=True, model_name="WEPP", category="Soil Erosion",
        result={"erosion_kg_per_m2_yr": round(erosion, 2)},
        formula="E = Kb × S × L × (1-C) × 0.5",
        interpretation=f"Erosion is {round(erosion, 2)} kg/m²/yr"
    )

# 2.5 ANSWERS
class ANSWERSInput(BaseModel):
    rainfall_energy: float = Field(..., gt=0)
    runoff_rate: float = Field(..., gt=0)
    slope: float = Field(..., gt=0)
    soil_resistance: float = Field(..., gt=0)

def calculate_answers(data: ANSWERSInput) -> ModelOutput:
    erosion = (data.rainfall_energy * data.runoff_rate * data.slope) / data.soil_resistance
    return ModelOutput(
        success=True, model_name="ANSWERS", category="Soil Erosion",
        result={"soil_loss_kg_per_ha": round(erosion, 2)},
        formula="E = (RE × q × S) / SR",
        interpretation=f"Soil loss is {round(erosion, 2)} kg/ha"
    )

# 2.6 EPIC
class EPICInput(BaseModel):
    wind_speed: float = Field(..., gt=0)
    soil_moisture: float = Field(..., ge=0, le=100)
    surface_roughness: float = Field(..., gt=0)
    vegetative_cover: float = Field(..., ge=0, le=1)

def calculate_epic(data: EPICInput) -> ModelOutput:
    erosion = data.wind_speed * (1 - data.vegetative_cover) * data.soil_moisture / (data.surface_roughness * 10)
    return ModelOutput(
        success=True, model_name="EPIC", category="Soil Erosion",
        result={"erosion_tons_per_ha": round(erosion, 2)},
        formula="E = W × (1-VC) × SM / (SR × 10)",
        interpretation=f"Erosion is {round(erosion, 2)} tons/ha"
    )

# 2.7 S-CSLE
class SCSLEInput(BaseModel):
    r_factor: float = Field(..., gt=0)
    k_factor: float = Field(..., gt=0)
    ls_factor: float = Field(..., gt=0)
    c_factor: float = Field(..., ge=0, le=1)
    p_factor: float = Field(..., ge=0, le=1)
    tech_factor: float = Field(..., ge=0, le=1)

def calculate_scsle(data: SCSLEInput) -> ModelOutput:
    A = data.r_factor * data.k_factor * data.ls_factor * data.c_factor * data.p_factor * data.tech_factor
    return ModelOutput(
        success=True, model_name="S-CSLE", category="Soil Erosion",
        result={"soil_loss_tons_per_ha_yr": round(A, 2)},
        formula="A = R × K × LS × C × P × T",
        interpretation=f"Soil loss is {round(A, 2)} tons/ha/yr"
    )

# 2.8 Wind Erosion (WEQ)
class WEQInput(BaseModel):
    wind_velocity: float = Field(..., description="Wind velocity (m/s)", gt=0)
    soil_moisture: float = Field(..., ge=0, le=100)
    surface_roughness: float = Field(..., gt=0)
    vegetative_cover: float = Field(..., ge=0, le=1)

def calculate_weq(data: WEQInput) -> ModelOutput:
    erosion = (data.wind_velocity ** 3) * (1 - data.vegetative_cover) / (data.soil_moisture * data.surface_roughness)
    return ModelOutput(
        success=True, model_name="Wind Erosion (WEQ)", category="Soil Erosion",
        result={"erosion_tons_per_ha_yr": round(erosion, 4)},
        formula="E = V³ × (1-VC) / (SM × SR)",
        interpretation=f"Wind erosion is {round(erosion, 4)} tons/ha/yr"
    )


# ==========================================
# 3. IRRIGATION & EVAPOTRANSPIRATION (8)
# ==========================================

# 3.1 FAO-56 Penman-Monteith
class PenmanMonteithInput(BaseModel):
    temperature: float = Field(..., description="Mean temperature (°C)")
    wind_speed: float = Field(..., description="Wind speed at 2m (m/s)", gt=0)
    solar_radiation: float = Field(..., description="Solar radiation (MJ/m²/day)", gt=0)
    relative_humidity: float = Field(..., description="Relative humidity (%)", gt=0, le=100)
    elevation: float = Field(0, description="Elevation (m)", ge=0)

def calculate_penman_monteith(data: PenmanMonteithInput) -> ModelOutput:
    # Constants
    sigma = 4.903e-9  # Stefan-Boltzmann constant
    # Saturation vapor pressure
    e_t = 0.6108 * math.exp((17.27 * data.temperature) / (data.temperature + 237.3))
    # Actual vapor pressure
    e_a = e_t * data.relative_humidity / 100
    # Slope of saturation vapor pressure curve
    delta = (4098 * e_t) / ((data.temperature + 237.3) ** 2)
    # Psychrometric constant
    P = 101.3 * ((293 - 0.0065 * data.elevation) / 293) ** 5.26
    gamma = 0.00163 * P / 2.45
    # Net radiation
    R_n = 0.77 * data.solar_radiation
    # Reference ET
    ET0_num = 0.408 * delta * R_n + gamma * (900 / (data.temperature + 273)) * data.wind_speed * (e_t - e_a)
    ET0_den = delta + gamma * (1 + 0.34 * data.wind_speed)
    ET0 = ET0_num / ET0_den
    return ModelOutput(
        success=True,
        model_name="FAO-56 Penman-Monteith",
        category="Evapotranspiration",
        result={
            "ET0_mm_per_day": round(ET0, 2),
            "saturation_vapor_pressure_kPa": round(e_t, 3),
            "actual_vapor_pressure_kPa": round(e_a, 3),
        },
        formula="ET₀ = [0.408×Δ×Rn + γ×(900/(T+273))×u₂×(es-ea)] / [Δ + γ×(1+0.34×u₂)]",
        interpretation=f"Reference evapotranspiration is {round(ET0, 2)} mm/day"
    )

# 3.2 Hargreaves
class HargreavesInput(BaseModel):
    temperature_mean: float = Field(..., description="Mean temperature (°C)")
    temperature_max: float = Field(..., description="Max temperature (°C)")
    temperature_min: float = Field(..., description="Min temperature (°C)")
    extraterrestrial_radiation: float = Field(..., description="Ra (mm/day)", gt=0)

def calculate_hargreaves(data: HargreavesInput) -> ModelOutput:
    ET0 = 0.0023 * 0.408 * data.extraterrestrial_radiation * (data.temperature_mean + 17.8) * (data.temperature_max - data.temperature_min) ** 0.5
    return ModelOutput(
        success=True, model_name="Hargreaves", category="Evapotranspiration",
        result={"ET0_mm_per_day": round(ET0, 2)},
        formula="ET₀ = 0.0023 × 0.408 × Ra × (Tmean + 17.8) × (Tmax - Tmin)^0.5",
        interpretation=f"ET₀ is {round(ET0, 2)} mm/day"
    )

# 3.3 Thornthwaite
class ThornthwaiteInput(BaseModel):
    temperature: float = Field(..., description="Mean temperature (°C)")
    daylight_hours: float = Field(12, description="Average daylight hours", gt=0)
    days_in_month: float = Field(30, description="Days in month", gt=0)

def calculate_thornthwaite(data: ThornthwaiteInput) -> ModelOutput:
    if data.temperature <= 0:
        ET = 0
        I = 0
    else:
        I = 12 * (data.temperature / 5) ** 1.514  # Simplified heat index
        a = (6.75e-7 * I**3) - (7.71e-5 * I**2) + (1.792e-2 * I) + 0.49239
        ET_unadj = 16 * (10 * data.temperature / I) ** a
        ET = ET_unadj * (data.daylight_hours / 12) * (data.days_in_month / 30)
    return ModelOutput(
        success=True, model_name="Thornthwaite", category="Evapotranspiration",
        result={"ET_mm_per_month": round(ET, 2), "heat_index_I": round(I, 2)},
        formula="ET = 16 × (10T/I)^a × (N/12) × (D/30)",
        interpretation=f"ET is {round(ET, 2)} mm/month"
    )

# 3.4 Blaney-Criddle
class BlaneyCriddleInput(BaseModel):
    temperature: float = Field(..., description="Mean temperature (°C)")
    daylight_percentage: float = Field(..., description="Daylight hours % of year", gt=0)
    crop_coefficient: float = Field(..., description="Crop coefficient (k)", gt=0)

def calculate_blaney_criddle(data: BlaneyCriddleInput) -> ModelOutput:
    P = data.daylight_percentage
    ET = data.crop_coefficient * (data.temperature / 100 + 0.1) * P * 25.4
    return ModelOutput(
        success=True, model_name="Blaney-Criddle", category="Evapotranspiration",
        result={"ET_mm_per_month": round(ET, 2)},
        formula="ET = k × (T/100 + 0.1) × p × 25.4",
        interpretation=f"ET is {round(ET, 2)} mm/month"
    )

# 3.5 Rice Irrigation
class RiceIrrigationInput(BaseModel):
    area_hectares: float = Field(..., gt=0)
    et_rate: float = Field(..., description="ET rate (mm/day)", gt=0)
    percolation: float = Field(..., description="Percolation rate (mm/day)", gt=0)
    puddling_requirement: float = Field(200, description="Puddling requirement (mm)", gt=0)
    growing_days: float = Field(120, description="Growing season (days)", gt=0)

def calculate_rice_irrigation(data: RiceIrrigationInput) -> ModelOutput:
    daily_need = data.et_rate + data.percolation
    total_season_need = data.puddling_requirement + daily_need * data.growing_days
    total_volume_m3 = total_season_need * data.area_hectares * 10  # 10 m3 per mm per ha
    return ModelOutput(
        success=True, model_name="Rice Irrigation", category="Evapotranspiration",
        result={
            "daily_water_need_mm": round(daily_need, 2),
            "total_season_need_mm": round(total_season_need, 2),
            "total_volume_m3": round(total_volume_m3, 2),
        },
        formula="V = (Puddling + (ET + Perc) × Days) × Area × 10",
        interpretation=f"Total water needed: {round(total_volume_m3, 0)} m³"
    )

# 3.6 Drip Irrigation Efficiency
class DripInput(BaseModel):
    crop_water_requirement: float = Field(..., description="Crop water req (mm)", gt=0)
    area_hectares: float = Field(..., gt=0)
    efficiency: float = Field(0.9, description="System efficiency (0-1)", gt=0, le=1)

def calculate_drip(data: DripInput) -> ModelOutput:
    gross_requirement = (data.crop_water_requirement * data.area_hectares * 10) / data.efficiency
    water_saved = (data.crop_water_requirement * data.area_hectares * 10) * (1 - data.efficiency)
    return ModelOutput(
        success=True, model_name="Drip Irrigation", category="Evapotranspiration",
        result={
            "gross_requirement_m3": round(gross_requirement, 2),
            "water_saved_m3": round(water_saved, 2),
        },
        formula="Gross = (CWR × Area × 10) / Efficiency",
        interpretation=f"Gross requirement: {round(gross_requirement, 0)} m³"
    )

# 3.7 Sprinkler Efficiency
class SprinklerInput(BaseModel):
    crop_water_requirement: float = Field(..., gt=0)
    area_hectares: float = Field(..., gt=0)
    efficiency: float = Field(0.75, gt=0, le=1)
    wind_factor: float = Field(1.0, ge=1)

def calculate_sprinkler(data: SprinklerInput) -> ModelOutput:
    gross = (data.crop_water_requirement * data.area_hectares * 10 * data.wind_factor) / data.efficiency
    return ModelOutput(
        success=True, model_name="Sprinkler Efficiency", category="Evapotranspiration",
        result={"gross_requirement_m3": round(gross, 2)},
        formula="Gross = (CWR × Area × 10 × Wf) / Efficiency",
        interpretation=f"Gross requirement: {round(gross, 0)} m³"
    )

# 3.8 Irrigation Requirement
class IrrigationRequirementInput(BaseModel):
    et0: float = Field(..., gt=0)
    kc: float = Field(..., description="Crop coefficient", gt=0)
    effective_rainfall: float = Field(0, ge=0)
    efficiency: float = Field(0.7, gt=0, le=1)
    area_hectares: float = Field(..., gt=0)

def calculate_irrigation_requirement(data: IrrigationRequirementInput) -> ModelOutput:
    et_crop = data.et0 * data.kc
    net_req = max(0, et_crop - data.effective_rainfall)
    gross_req = net_req / data.efficiency
    volume_m3 = gross_req * data.area_hectares * 10
    return ModelOutput(
        success=True, model_name="Irrigation Requirement", category="Evapotranspiration",
        result={
            "ET_crop_mm": round(et_crop, 2),
            "net_requirement_mm": round(net_req, 2),
            "gross_requirement_mm": round(gross_req, 2),
            "total_volume_m3": round(volume_m3, 2),
        },
        formula="IR = (ETc - Pe) / Efficiency",
        interpretation=f"Irrigation needed: {round(volume_m3, 0)} m³"
    )


# ==========================================
# 4. WATER QUALITY (6)
# ==========================================

# 4.1 Streeter-Phelps
class StreeterPhelpsInput(BaseModel):
    L0: float = Field(..., description="Initial BOD (mg/L)", gt=0)
    D0: float = Field(..., description="Initial oxygen deficit (mg/L)", ge=0)
    k1: float = Field(..., description="Deoxygenation rate (1/day)", gt=0)
    k2: float = Field(..., description="Reaeration rate (1/day)", gt=0)
    time_days: float = Field(..., gt=0)

def calculate_streeter_phelps(data: StreeterPhelpsInput) -> ModelOutput:
    Lt = data.L0 * math.exp(-data.k1 * data.time_days)
    Dt = (data.k1 * data.L0 / (data.k2 - data.k1)) * (math.exp(-data.k1 * data.time_days) - math.exp(-data.k2 * data.time_days)) + data.D0 * math.exp(-data.k2 * data.time_days)
    DO_saturation = 8.0  # Simplified
    DO = DO_saturation - Dt
    return ModelOutput(
        success=True, model_name="Streeter-Phelps", category="Water Quality",
        result={
            "BOD_at_time_mg_per_L": round(Lt, 3),
            "oxygen_deficit_mg_per_L": round(Dt, 3),
            "DO_mg_per_L": round(DO, 3),
        },
        formula="Lt = L0 × e^(-k1×t), Dt = ...",
        interpretation=f"DO at time t is {round(DO, 2)} mg/L"
    )

# 4.2 Oxygen Sag Curve
class OxygenSagInput(BaseModel):
    L0: float = Field(..., gt=0)
    D0: float = Field(..., ge=0)
    k1: float = Field(..., gt=0)
    k2: float = Field(..., gt=0)

def calculate_oxygen_sag(data: OxygenSagInput) -> ModelOutput:
    if data.k1 == data.k2:
        tc = 0
        Dc = 0
    else:
        tc = (1 / (data.k2 - data.k1)) * math.log((data.k2 / data.k1) * (1 - data.D0 * (data.k2 - data.k1) / (data.k1 * data.L0)))
        Dc = (data.k1 * data.L0 / (data.k2 - data.k1)) * (math.exp(-data.k1 * tc) - math.exp(-data.k2 * tc)) + data.D0 * math.exp(-data.k2 * tc)
    return ModelOutput(
        success=True, model_name="Oxygen Sag Curve", category="Water Quality",
        result={
            "critical_time_days": round(tc, 3),
            "critical_deficit_mg_per_L": round(Dc, 3),
        },
        formula="tc = (1/(k2-k1)) × ln((k2/k1) × (1-D0×(k2-k1)/(k1×L0)))",
        interpretation=f"Critical time is {round(tc, 2)} days"
    )

# 4.3 Dilution Factor
class DilutionInput(BaseModel):
    effluent_flow: float = Field(..., gt=0)
    stream_flow: float = Field(..., gt=0)
    effluent_concentration: float = Field(..., gt=0)
    background_concentration: float = Field(..., ge=0)

def calculate_dilution(data: DilutionInput) -> ModelOutput:
    dilution_factor = data.stream_flow / data.effluent_flow
    mixed_conc = (data.effluent_flow * data.effluent_concentration + data.stream_flow * data.background_concentration) / (data.effluent_flow + data.stream_flow)
    return ModelOutput(
        success=True, model_name="Dilution Factor", category="Water Quality",
        result={
            "dilution_factor": round(dilution_factor, 3),
            "mixed_concentration": round(mixed_conc, 3),
        },
        formula="DF = Qs/Qe, Cmix = (Qe×Ce + Qs×Cb)/(Qe+Qs)",
        interpretation=f"Dilution factor is {round(dilution_factor, 2)}"
    )

# 4.4 Self-Purification
class SelfPurificationInput(BaseModel):
    initial_bod: float = Field(..., gt=0)
    k1: float = Field(..., gt=0)
    time_days: float = Field(..., gt=0)
    stream_velocity: float = Field(..., gt=0)
    distance_km: float = Field(..., gt=0)

def calculate_self_purification(data: SelfPurificationInput) -> ModelOutput:
    travel_time = data.distance_km / (data.stream_velocity * 24)  # days
    bod_remaining = data.initial_bod * math.exp(-data.k1 * travel_time)
    purification_percent = (1 - bod_remaining / data.initial_bod) * 100
    return ModelOutput(
        success=True, model_name="Self-Purification", category="Water Quality",
        result={
            "travel_time_days": round(travel_time, 3),
            "bod_remaining_mg_per_L": round(bod_remaining, 3),
            "purification_percent": round(purification_percent, 2),
        },
        formula="BOD_t = BOD₀ × e^(-k1×t)",
        interpretation=f"Self-purification: {round(purification_percent, 1)}%"
    )

# 4.5 Eutrophication Index
class EutrophicationInput(BaseModel):
    tp: float = Field(..., description="Total phosphorus (μg/L)", gt=0)
    tn: float = Field(..., description="Total nitrogen (mg/L)", gt=0)
    chlorophyll_a: float = Field(..., description="Chlorophyll-a (μg/L)", gt=0)

def calculate_eutrophication(data: EutrophicationInput) -> ModelOutput:
    # Carlson's TSI
    tsi_tp = 14.42 * math.log(data.tp) + 4.15
    tsi_tn = 54.45 * math.log(data.tn) - 100
    tsi_chl = 10 * (6 - (2.04 - 0.68 * math.log(data.chlorophyll_a)) / 0.68) if data.chlorophyll_a > 0 else 0
    avg_tsi = (tsi_tp + tsi_tn + tsi_chl) / 3
    if avg_tsi < 40: status = "Oligotrophic"
    elif avg_tsi < 50: status = "Mesotrophic"
    elif avg_tsi < 60: status = "Eutrophic"
    elif avg_tsi < 70: status = "Hypereutrophic"
    else: status = "Hyper-eutrophic"
    return ModelOutput(
        success=True, model_name="Eutrophication Index", category="Water Quality",
        result={
            "TSI_TP": round(tsi_tp, 2),
            "TSI_TN": round(tsi_tn, 2),
            "TSI_Chlorophyll": round(tsi_chl, 2),
            "average_TSI": round(avg_tsi, 2),
            "status": status,
        },
        formula="TSI = Carlson's Trophic State Index",
        interpretation=f"Water body is {status} (TSI={round(avg_tsi, 1)})"
    )

# 4.6 Water Quality Index (WQI)
class WQIInput(BaseModel):
    pH: float = Field(..., gt=0)
    DO: float = Field(..., ge=0)
    BOD: float = Field(..., ge=0)
    turbidity: float = Field(..., ge=0)
    total_coliforms: float = Field(..., ge=0)

def calculate_wqi(data: WQIInput) -> ModelOutput:
    # Simplified NSF-WQI
    q_ph = 100 - abs(data.pH - 7) * 20 if 6 <= data.pH <= 9 else 0
    q_do = min(100, data.DO * 10)
    q_bod = max(0, 100 - data.BOD * 10)
    q_turb = max(0, 100 - data.turbidity)
    q_coli = max(0, 100 - data.total_coliforms / 100)
    wqi = (q_ph * 0.11 + q_do * 0.17 + q_bod * 0.12 + q_turb * 0.08 + q_coli * 0.16) / 0.64
    if wqi >= 90: rating = "Excellent"
    elif wqi >= 70: rating = "Good"
    elif wqi >= 50: rating = "Poor"
    elif wqi >= 25: rating = "Very Poor"
    else: rating = "Unsuitable"
    return ModelOutput(
        success=True, model_name="Water Quality Index", category="Water Quality",
        result={
            "WQI": round(wqi, 2),
            "rating": rating,
            "sub_indices": {
                "pH": round(q_ph, 2),
                "DO": round(q_do, 2),
                "BOD": round(q_bod, 2),
                "Turbidity": round(q_turb, 2),
                "Coliforms": round(q_coli, 2),
            }
        },
        formula="WQI = Σ(qi × wi) / Σwi",
        interpretation=f"Water quality is {rating} (WQI={round(wqi, 1)})"
    )


# ==========================================
# 5. ECONOMIC MODELS (4)
# ==========================================

# 5.1 NPV
class NPVInput(BaseModel):
    initial_investment: float = Field(..., description="Initial investment ($)", gt=0)
    cash_flows: list = Field(..., description="Annual cash flows")
    discount_rate: float = Field(..., description="Discount rate (%)", gt=0)

def calculate_npv(data: NPVInput) -> ModelOutput:
    rate = data.discount_rate / 100
    npv = -data.initial_investment
    for i, cf in enumerate(data.cash_flows):
        npv += cf / ((1 + rate) ** (i + 1))
    return ModelOutput(
        success=True, model_name="Net Present Value (NPV)", category="Economic",
        result={
            "NPV": round(npv, 2),
            "decision": "Accept" if npv > 0 else "Reject",
        },
        formula="NPV = -I₀ + Σ(CFt / (1+r)^t)",
        interpretation=f"NPV is ${round(npv, 2)} - {('Accept' if npv > 0 else 'Reject')} project"
    )

# 5.2 IRR
class IRRInput(BaseModel):
    initial_investment: float = Field(..., gt=0)
    cash_flows: list = Field(..., description="Annual cash flows")

def calculate_irr(data: IRRInput) -> ModelOutput:
    # Newton-Raphson method for IRR
    irr = 0.1
    for _ in range(100):
        npv = -data.initial_investment
        for i, cf in enumerate(data.cash_flows):
            npv += cf / ((1 + irr) ** (i + 1))
        if abs(npv) < 0.01:
            break
        irr += 0.01 if npv > 0 else -0.01
    return ModelOutput(
        success=True, model_name="Internal Rate of Return (IRR)", category="Economic",
        result={
            "IRR_percent": round(irr * 100, 2),
            "decision": "Accept" if irr > 0.1 else "Review",
        },
        formula="NPV = 0 => solve for IRR",
        interpretation=f"IRR is {round(irr*100, 2)}%"
    )

# 5.3 B/C Ratio
class BCInput(BaseModel):
    benefits: list = Field(..., description="Annual benefits")
    costs: list = Field(..., description="Annual costs")
    discount_rate: float = Field(..., gt=0)

def calculate_bc(data: BCInput) -> ModelOutput:
    rate = data.discount_rate / 100
    pv_benefits = sum(b / ((1 + rate) ** (i + 1)) for i, b in enumerate(data.benefits))
    pv_costs = sum(c / ((1 + rate) ** (i + 1)) for i, c in enumerate(data.costs))
    bc_ratio = pv_benefits / pv_costs if pv_costs > 0 else 0
    return ModelOutput(
        success=True, model_name="Benefit-Cost Ratio", category="Economic",
        result={
            "PV_Benefits": round(pv_benefits, 2),
            "PV_Costs": round(pv_costs, 2),
            "B_C_Ratio": round(bc_ratio, 3),
            "decision": "Accept" if bc_ratio > 1 else "Reject",
        },
        formula="B/C = PV(Benefits) / PV(Costs)",
        interpretation=f"B/C ratio is {round(bc_ratio, 2)}"
    )

# 5.4 Payback Period
class PaybackInput(BaseModel):
    initial_investment: float = Field(..., gt=0)
    annual_cash_flow: float = Field(..., gt=0)

def calculate_payback(data: PaybackInput) -> ModelOutput:
    payback = data.initial_investment / data.annual_cash_flow
    return ModelOutput(
        success=True, model_name="Payback Period", category="Economic",
        result={
            "payback_years": round(payback, 2),
        },
        formula="Payback = Initial Investment / Annual Cash Flow",
        interpretation=f"Payback period is {round(payback, 2)} years"
    )


# ==========================================
# 6. CARBON & ECOSYSTEM (4)
# ==========================================

# 6.1 Carbon Sequestration
class CarbonSeqInput(BaseModel):
    area_hectares: float = Field(..., gt=0)
    sequestration_rate: float = Field(..., description="tCO2e/ha/yr", gt=0)
    years: float = Field(..., gt=0)

def calculate_carbon_seq(data: CarbonSeqInput) -> ModelOutput:
    total = data.area_hectares * data.sequestration_rate * data.years
    annual = data.area_hectares * data.sequestration_rate
    return ModelOutput(
        success=True, model_name="Carbon Sequestration", category="Carbon & Ecosystem",
        result={
            "total_tCO2e": round(total, 2),
            "annual_tCO2e": round(annual, 2),
            "carbon_credits_estimate": round(total * 25, 2),
        },
        formula="Total = Area × Rate × Years",
        interpretation=f"Total sequestration: {round(total, 0)} tCO2e"
    )

# 6.2 Biodiversity Index
class BiodiversityInput(BaseModel):
    species_counts: list = Field(..., description="Count of each species")

def calculate_biodiversity(data: BiodiversityInput) -> ModelOutput:
    total = sum(data.species_counts)
    if total == 0:
        return ModelOutput(success=False, model_name="Biodiversity Index", category="Carbon & Ecosystem", result={}, formula="", interpretation="No species data")
    shannon = 0
    for count in data.species_counts:
        p = count / total
        if p > 0:
            shannon -= p * math.log(p)
    richness = len(data.species_counts)
    evenness = shannon / math.log(richness) if richness > 1 else 0
    return ModelOutput(
        success=True, model_name="Biodiversity Index", category="Carbon & Ecosystem",
        result={
            "shannon_index": round(shannon, 3),
            "species_richness": richness,
            "evenness": round(evenness, 3),
        },
        formula="H' = -Σ(pi × ln(pi))",
        interpretation=f"Shannon diversity index is {round(shannon, 2)}"
    )

# 6.3 Ecosystem Services Value
class EcosystemValueInput(BaseModel):
    area_hectares: float = Field(..., gt=0)
    forest_value: float = Field(2000, description="$ per ha per year")
    water_value: float = Field(3000, description="$ per ha per year")
    carbon_value: float = Field(500, description="$ per ha per year")

def calculate_ecosystem_value(data: EcosystemValueInput) -> ModelOutput:
    total_annual = data.area_hectares * (data.forest_value + data.water_value + data.carbon_value)
    total_50yr = total_annual * 50
    return ModelOutput(
        success=True, model_name="Ecosystem Services Value", category="Carbon & Ecosystem",
        result={
            "annual_value_USD": round(total_annual, 2),
            "total_50yr_USD": round(total_50yr, 2),
        },
        formula="Value = Area × (Forest + Water + Carbon) values",
        interpretation=f"Annual ecosystem value: ${round(total_annual, 0)}"
    )

# 6.4 NDVI Analysis
class NDVIInput(BaseModel):
    NIR: float = Field(..., description="Near-infrared reflectance", ge=0, le=1)
    RED: float = Field(..., description="Red reflectance", ge=0, le=1)

def calculate_ndvi(data: NDVIInput) -> ModelOutput:
    if (data.NIR + data.RED) == 0:
        ndvi = 0
    else:
        ndvi = (data.NIR - data.RED) / (data.NIR + data.RED)
    if ndvi < 0: vegetation = "Non-vegetated"
    elif ndvi < 0.2: vegetation = "Bare soil"
    elif ndvi < 0.4: vegetation = "Sparse vegetation"
    elif ndvi < 0.6: vegetation = "Moderate vegetation"
    else: vegetation = "Dense vegetation"
    return ModelOutput(
        success=True, model_name="NDVI Analysis", category="Carbon & Ecosystem",
        result={
            "NDVI": round(ndvi, 3),
            "vegetation_class": vegetation,
        },
        formula="NDVI = (NIR - RED) / (NIR + RED)",
        interpretation=f"NDVI is {round(ndvi, 2)} - {vegetation}"
    )


# ==========================================
# MODEL REGISTRY
# ==========================================
MODEL_REGISTRY = {
    # Hydrology
    "darcy": {"func": calculate_darcy, "input": DarcyInput, "category": "Hydrology", "name": "Darcy's Law"},
    "manning": {"func": calculate_manning, "input": ManningInput, "category": "Hydrology", "name": "Manning's Equation"},
    "scs": {"func": calculate_scs, "input": SCSInput, "category": "Hydrology", "name": "SCS Curve Number"},
    "muskingum": {"func": calculate_muskingum, "input": MuskingumInput, "category": "Hydrology", "name": "Muskingum Routing"},
    "rational": {"func": calculate_rational, "input": RationalInput, "category": "Hydrology", "name": "Rational Method"},
    "theis": {"func": calculate_theis, "input": TheisInput, "category": "Hydrology", "name": "Theis Equation"},
    "cooper_jacob": {"func": calculate_cooper_jacob, "input": CooperJacobInput, "category": "Hydrology", "name": "Cooper-Jacob"},
    "dupuit": {"func": calculate_dupuit, "input": DupuitInput, "category": "Hydrology", "name": "Dupuit-Forchheimer"},
    "kirpich": {"func": calculate_kirpich, "input": KirpichInput, "category": "Hydrology", "name": "Kirpich"},
    "chow": {"func": calculate_chow, "input": ChowInput, "category": "Hydrology", "name": "Chow Infiltration"},
    # Soil Erosion
    "rusle": {"func": calculate_rusle, "input": RUSLEInput, "category": "Soil Erosion", "name": "RUSLE"},
    "musle": {"func": calculate_musle, "input": MUSLEInput, "category": "Soil Erosion", "name": "MUSLE"},
    "usle": {"func": calculate_usle, "input": USLEInput, "category": "Soil Erosion", "name": "USLE"},
    "wepp": {"func": calculate_wepp, "input": WEPPInput, "category": "Soil Erosion", "name": "WEPP"},
    "answers": {"func": calculate_answers, "input": ANSWERSInput, "category": "Soil Erosion", "name": "ANSWERS"},
    "epic": {"func": calculate_epic, "input": EPICInput, "category": "Soil Erosion", "name": "EPIC"},
    "scsle": {"func": calculate_scsle, "input": SCSLEInput, "category": "Soil Erosion", "name": "S-CSLE"},
    "weq": {"func": calculate_weq, "input": WEQInput, "category": "Soil Erosion", "name": "Wind Erosion (WEQ)"},
    # Evapotranspiration
    "penman_monteith": {"func": calculate_penman_monteith, "input": PenmanMonteithInput, "category": "Evapotranspiration", "name": "FAO-56 Penman-Monteith"},
    "hargreaves": {"func": calculate_hargreaves, "input": HargreavesInput, "category": "Evapotranspiration", "name": "Hargreaves"},
    "thornthwaite": {"func": calculate_thornthwaite, "input": ThornthwaiteInput, "category": "Evapotranspiration", "name": "Thornthwaite"},
    "blaney_criddle": {"func": calculate_blaney_criddle, "input": BlaneyCriddleInput, "category": "Evapotranspiration", "name": "Blaney-Criddle"},
    "rice_irrigation": {"func": calculate_rice_irrigation, "input": RiceIrrigationInput, "category": "Evapotranspiration", "name": "Rice Irrigation"},
    "drip": {"func": calculate_drip, "input": DripInput, "category": "Evapotranspiration", "name": "Drip Irrigation"},
    "sprinkler": {"func": calculate_sprinkler, "input": SprinklerInput, "category": "Evapotranspiration", "name": "Sprinkler Efficiency"},
    "irrigation_req": {"func": calculate_irrigation_requirement, "input": IrrigationRequirementInput, "category": "Evapotranspiration", "name": "Irrigation Requirement"},
    # Water Quality
    "streeter_phelps": {"func": calculate_streeter_phelps, "input": StreeterPhelpsInput, "category": "Water Quality", "name": "Streeter-Phelps"},
    "oxygen_sag": {"func": calculate_oxygen_sag, "input": OxygenSagInput, "category": "Water Quality", "name": "Oxygen Sag Curve"},
    "dilution": {"func": calculate_dilution, "input": DilutionInput, "category": "Water Quality", "name": "Dilution Factor"},
    "self_purification": {"func": calculate_self_purification, "input": SelfPurificationInput, "category": "Water Quality", "name": "Self-Purification"},
    "eutrophication": {"func": calculate_eutrophication, "input": EutrophicationInput, "category": "Water Quality", "name": "Eutrophication Index"},
    "wqi": {"func": calculate_wqi, "input": WQIInput, "category": "Water Quality", "name": "Water Quality Index"},
    # Economic
    "npv": {"func": calculate_npv, "input": NPVInput, "category": "Economic", "name": "Net Present Value"},
    "irr": {"func": calculate_irr, "input": IRRInput, "category": "Economic", "name": "Internal Rate of Return"},
    "bc_ratio": {"func": calculate_bc, "input": BCInput, "category": "Economic", "name": "Benefit-Cost Ratio"},
    "payback": {"func": calculate_payback, "input": PaybackInput, "category": "Economic", "name": "Payback Period"},
    # Carbon & Ecosystem
    "carbon_seq": {"func": calculate_carbon_seq, "input": CarbonSeqInput, "category": "Carbon & Ecosystem", "name": "Carbon Sequestration"},
    "biodiversity": {"func": calculate_biodiversity, "input": BiodiversityInput, "category": "Carbon & Ecosystem", "name": "Biodiversity Index"},
    "ecosystem_value": {"func": calculate_ecosystem_value, "input": EcosystemValueInput, "category": "Carbon & Ecosystem", "name": "Ecosystem Services Value"},
    "ndvi": {"func": calculate_ndvi, "input": NDVIInput, "category": "Carbon & Ecosystem", "name": "NDVI Analysis"},
}
