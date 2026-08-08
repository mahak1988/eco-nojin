# Simulation Formulas Reference
## Econojin / Hydroma-Nojin Platform

Comprehensive reference of all scientific formulas used across simulator engines.
All formulas are implemented via Clean Room methodology from public domain literature.

---

## 1. Evapotranspiration

### Hargreaves ET0 (Simplified Penman-Monteith)
**Source:** Hargreaves G.H. & Samani Z.A. (1985). Reference crop evapotranspiration from temperature.

```
ET0 = 0.0023 * Ra * (Tmean + 17.8) * sqrt(Tmax - Tmin)

Where:
  ET0   = Reference evapotranspiration (mm/day)
  Ra    = Extraterrestrial radiation (MJ/m^2/day)
  Tmean = Mean daily temperature (C)
  Tmax  = Maximum daily temperature (C)
  Tmin  = Minimum daily temperature (C)
```

### Extraterrestrial Radiation (Ra)
**Source:** Allen R.G. et al. (1998). FAO Irrigation and Drainage Paper 56.

```
Ra = (24*60/pi) * Gsc * Dr * (ws*sin(phi)*sin(delta) + cos(phi)*cos(delta)*sin(ws))

Where:
  Gsc   = Solar constant = 0.0820 MJ/m^2/min
  Dr    = 1 + 0.033 * cos(2*pi*J/365)          (inverse relative distance Earth-Sun)
  delta = 0.409 * sin(2*pi*J/365 - 1.39)       (solar declination, rad)
  ws    = arccos(-tan(phi)*tan(delta))          (sunset hour angle, rad)
  phi   = latitude (rad)
  J     = day of year (1-366)
```

### FAO-56 Water Balance
**Source:** Steduto P. et al. (2009). AquaCrop - FAO crop model. Agronomy Journal 101(3).

```
ETc = Kc * ET0                     (crop evapotranspiration)
Ks  = (TAW - Dr) / (TAW - RAW)     (water stress coefficient, when Dr > RAW)
ETa = Ks * ETc                     (actual evapotranspiration)

Where:
  Kc   = Crop coefficient
  TAW  = Total available water (mm)
  RAW  = Readily available water (mm)
  Dr   = Root zone depletion (mm)
```

### FAO-33 Yield Response to Water
```
1 - Ya/Yx = Ky * (1 - ETa/ETc)

Where:
  Ya  = Actual yield
  Yx  = Maximum/potential yield
  Ky  = Yield response factor (crop-specific)
```

---

## 2. Soil Carbon Dynamics (RothC)

### Carbon Decomposition Rate
**Source:** Coleman K. & Jenkinson D.S. (2014). RothC-26.3 Model.

```
dC_i/dt = I_i - k_i * C_i * a * b * c

Where:
  C_i  = Carbon in pool i (t/ha)
  I_i  = Carbon input to pool i (t/ha/yr)
  k_i  = Decomposition rate constant (yr^-1)
  a    = Temperature modifier
  b    = Moisture modifier
  c    = Plant cover modifier
```

### Temperature Modifier
```
f_temp = max(0.1, min(2.0, 0.5 + T_mean/30))
```

### Clay Protection Factor
```
f_clay = 1.0 / (1.0 + 0.015 * clay_pct)
```

### Net SOC Change
```
SOC_change = Carbon_input * (1 - e^(-k * t))

Where:
  k = Effective decomposition rate (yr^-1)
  t = Time (years)
```

---

## 3. Runoff (SCS-CN Method)

**Source:** USDA Soil Conservation Service (1985). National Engineering Handbook, Section 4.

```
Q = (P - 0.2*S)^2 / (P - 0.2*S + S)    for P > 0.2*S
Q = 0                                    for P <= 0.2*S

S = 25400/CN - 254

Where:
  Q  = Runoff depth (mm)
  P  = Precipitation (mm)
  S  = Potential maximum retention (mm)
  CN = Curve number (30-100)
  Ia = 0.2*S = Initial abstraction (mm)
```

---

## 4. Nitrogen Balance (DSSAT)

**Source:** Jones J.W. et al. (2003). DSSAT Cropping System Model.

```
N_available = N_soil + N_fertilizer + N_fixation - N_uptake - N_leaching - N_volatilization

Nitrogen stress:
  N_stress = 1.0 - N_uptake_actual / N_uptake_potential

Nitrogen efficiency:
  N_efficiency = N_uptake_actual / N_applied_total
```

---

## 5. Soil Erosion (RUSLE2)

**Source:** Renard K.G. et al. (1997). Predicting Soil Erosion by Water. USDA Handbook 703.

```
A = R * K * LS * C * P

Where:
  A = Average annual soil loss (t/ha/yr)
  R = Rainfall-runoff erosivity factor
  K = Soil erodibility factor
  LS = Slope length-steepness factor
  C = Cover-management factor
  P = Support practice factor
```

---

## 6. Biological Nitrogen Fixation (Milpa TEK)

**Source:** Peoples M.B. et al. (1995). Enhancing legume N2 fixation.

```
N_fixed = Bean_biomass * N_content * Rhizobia_efficiency

Where:
  Bean_biomass       = Legume dry biomass (kg/ha)
  N_content          = 0.025 (2.5% N in legume dry matter)
  Rhizobia_efficiency = 0.4-0.8 (nodulation efficiency factor)
```

---

## 7. Qanat Flow (Darcy''s Law)

**Source:** Darcy H. (1856). Les fontaines publiques de la ville de Dijon.

```
Q = T * i * W

Where:
  Q = Flow rate (m^3/day)
  T = Aquifer transmissivity (m^2/day)
  i = Hydraulic gradient = slope_pct / 100
  W = Channel width (m)
```

---

## 8. Waru Waru Thermal Buffer

**Source:** Erickson C.L. (1992). Prehistoric landscape management in Andean highlands.

```
delta_T = (C_water * V_water * delta_T_stored) / (V_soil * rho_soil * c_soil)

Where:
  C_water    = 4.18 kJ/(kg*K)  - specific heat of water
  V_water    = Water volume in channels (m^3)
  V_soil     = Soil volume in beds (m^3)
  rho_soil   = 1.3 t/m^3       - soil bulk density
  c_soil     = 0.8 kJ/(kg*K)   - specific heat of dry soil
  delta_T    = Night temperature increase (C)
```

---

## 9. Subak Water Allocation

**Source:** Lansing J.S. (2006). Perfect Order: Recognizing Complexity in Bali.

```
Q_field = Q_total * (A_field / A_total) * P_field

Where:
  Q_field  = Water allocation per field (m^3/s)
  Q_total  = Total available flow (m^3/s)
  A_field  = Field area (ha)
  A_total  = Total irrigated area (ha)
  P_field  = Priority factor (based on crop growth stage)
```

---

## References

1. Allen R.G. et al. (1998). FAO Irrigation and Drainage Paper 56. Rome.
2. Steduto P. et al. (2009). AquaCrop. Agronomy Journal 101(3):426-437.
3. Coleman K. & Jenkinson D.S. (2014). RothC-26.3. Rothamsted Research.
4. USDA SCS (1985). National Engineering Handbook, Section 4: Hydrology.
5. Jones J.W. et al. (2003). DSSAT. European Journal of Agronomy 18(3-4).
6. Renard K.G. et al. (1997). RUSLE. USDA Agriculture Handbook 703.
7. Hargreaves G.H. & Samani Z.A. (1985). Applied Engineering in Agriculture 1(2):96-99.
8. NASA POWER (2024). https://power.larc.nasa.gov/
