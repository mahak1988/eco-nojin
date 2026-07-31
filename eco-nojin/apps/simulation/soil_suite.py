"""
Soil suite: nitrate leaching, profile properties, amendments, and indices.

At least 15 process models / indices for soil profile & amendment planning.
Units SI / agronomic (t/ha, mm, dS/m, %).
"""

from __future__ import annotations

import math
from datetime import UTC, datetime
from typing import Any

from apps.simulation.evaluation_metrics import evaluate_series, kge, pbias


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# ---------------------------------------------------------------------------
# 1. Nitrate leaching (multi-layer, drainage-driven)
# ---------------------------------------------------------------------------

def run_nitrate_leaching(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Layered soil NO3 leaching.
    Each layer: storage (mm water capacity), NO3 (kg N/ha).
    Drainage from layer i carries NO3 concentration to i+1 / out of root zone.
    """
    p = params or {}
    days = int(p.get("days", 120))
    n_layers = int(p.get("n_layers", 3))
    layer_mm = float(p.get("layer_thickness_mm", 300.0))
    # field capacity water storage per layer (mm)
    theta_fc = float(p.get("theta_fc", 0.32))
    theta_wp = float(p.get("theta_wp", 0.14))
    awc_mm = (theta_fc - theta_wp) * layer_mm
    stor0 = float(p.get("initial_water_frac", 0.7)) * awc_mm

    no3 = [float(p.get("no3_kg_ha_layer", 25.0)) for _ in range(n_layers)]
    if isinstance(p.get("no3_profile"), list) and len(p["no3_profile"]) >= n_layers:
        no3 = [float(x) for x in p["no3_profile"][:n_layers]]

    water = [stor0 for _ in range(n_layers)]
    rain = float(p.get("rain_mm_day", 1.5))
    et = float(p.get("et_mm_day", 2.0))
    irrig = float(p.get("irrigation_mm_day", 0.5))
    fert_events = p.get("fertilizer_events") or []  # [{day, kg_ha, layer}]

    leached_cum = 0.0
    series: list[dict[str, Any]] = []

    for d in range(days + 1):
        if d % max(1, days // 12) == 0 or d == days:
            series.append(
                {
                    "day": d,
                    "no3_layers": [round(x, 3) for x in no3],
                    "water_mm": [round(w, 2) for w in water],
                    "no3_rootzone": round(sum(no3), 3),
                    "leached_cum_kg_ha": round(leached_cum, 3),
                }
            )
        if d == days:
            break

        for ev in fert_events:
            if int(ev.get("day", -1)) == d:
                li = int(ev.get("layer", 0))
                if 0 <= li < n_layers:
                    no3[li] += float(ev.get("kg_ha", 0))

        # top layer receives rain+irrig, all layers lose ET share
        inflow = rain + irrig
        et_left = et
        drainage = [0.0] * n_layers

        for i in range(n_layers):
            add = inflow if i == 0 else drainage[i - 1]
            water[i] += add
            # ET from available water
            take = min(water[i], et_left * (1.0 if i == 0 else 0.4))
            water[i] -= take
            et_left = max(0.0, et_left - take)
            if water[i] > awc_mm:
                drainage[i] = water[i] - awc_mm
                water[i] = awc_mm
            else:
                drainage[i] = 0.0

            # mass of NO3 leaving with drainage (complete mixing)
            if drainage[i] > 0 and water[i] + drainage[i] > 1e-6:
                # concentration based on water before drainage event approx
                vol = max(water[i] + drainage[i], 1e-3)
                conc = no3[i] / vol  # kg/ha per mm
                move = conc * drainage[i]
                move = min(move, no3[i])
                no3[i] -= move
                if i + 1 < n_layers:
                    no3[i + 1] += move
                else:
                    leached_cum += move

    return {
        "model": "nitrate_leaching_layered",
        "citation": "Layered complete-mix NO3 transport with FC capacity",
        "days": days,
        "n_layers": n_layers,
        "awc_mm_layer": round(awc_mm, 2),
        "final_no3_kg_ha": [round(x, 3) for x in no3],
        "leached_total_kg_ha": round(leached_cum, 3),
        "leaching_risk": (
            "high" if leached_cum > 40 else "moderate" if leached_cum > 15 else "low"
        ),
        "series": series,
        "notes_fa": (
            "آبشویی نیترات با زهکش از لایه‌ها؛ واحد kg N/ha. "
            "برای مزرعه واقعی با EC و بافت کالیبره کنید."
        ),
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 2–4. Texture → FC, WP, AWC, bulk density, porosity
# ---------------------------------------------------------------------------

def texture_hydrology(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Saxton-style simplified FC/WP from sand/clay %."""
    p = params or {}
    sand = _clamp(float(p.get("sand_pct", 40)), 0, 100)
    clay = _clamp(float(p.get("clay_pct", 25)), 0, 100)
    silt = _clamp(100.0 - sand - clay, 0, 100)
    # empirical (very simplified Saxton/Rawls)
    theta_fc = _clamp(0.2576 - 0.002 * sand + 0.0036 * clay + 0.0299 * math.log(max(clay, 1)), 0.08, 0.5)
    theta_wp = _clamp(0.026 + 0.005 * clay + 0.0158 * (clay ** 0.5) * 0.1, 0.03, 0.35)
    if theta_wp >= theta_fc:
        theta_wp = theta_fc * 0.45
    bd = _clamp(1.65 - 0.004 * clay - 0.001 * silt, 1.1, 1.7)  # Mg/m3
    porosity = 1.0 - bd / 2.65
    depth_cm = float(p.get("depth_cm", 30))
    awc_mm = (theta_fc - theta_wp) * depth_cm * 10.0  # cm → mm for depth in cm: *10
    return {
        "model": "texture_hydrology",
        "sand_pct": sand,
        "silt_pct": round(silt, 2),
        "clay_pct": clay,
        "theta_fc": round(theta_fc, 4),
        "theta_wp": round(theta_wp, 4),
        "awc_mm": round(awc_mm, 2),
        "bulk_density_mg_m3": round(bd, 3),
        "porosity": round(porosity, 4),
        "depth_cm": depth_cm,
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 5. SOC stock by depth
# ---------------------------------------------------------------------------

def soc_stock(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    soc_pct = float(p.get("soc_pct", 1.2))
    bd = float(p.get("bulk_density_mg_m3", 1.35))
    depth_cm = float(p.get("depth_cm", 30))
    stone = float(p.get("stone_frac", 0.0))
    # t C/ha = %C/100 * BD * depth_cm * 100 (standard)
    stock = soc_pct / 100.0 * bd * depth_cm * 100.0 * (1.0 - stone)
    return {
        "model": "soc_stock",
        "soc_pct": soc_pct,
        "stock_t_c_ha": round(stock, 3),
        "depth_cm": depth_cm,
        "bulk_density_mg_m3": bd,
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 6. Liming requirement (Adams-Evans simplified)
# ---------------------------------------------------------------------------

def liming_requirement(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    ph = float(p.get("ph", 5.5))
    target = float(p.get("target_ph", 6.5))
    cec = float(p.get("cec_cmol_kg", 15))
    depth_cm = float(p.get("depth_cm", 20))
    if ph >= target:
        lime = 0.0
    else:
        # rough: 1 cmol_c/kg ≈ needs ~1 t CaCO3/ha per 15 cm for ΔpH related
        delta = target - ph
        lime = delta * cec * 0.15 * (depth_cm / 15.0)
    return {
        "model": "liming_requirement",
        "ph": ph,
        "target_ph": target,
        "lime_t_ha_caco3": round(max(0.0, lime), 2),
        "cec_cmol_kg": cec,
        "notes_fa": "تخمین غربالگری؛ با بافر pH آزمایشگاه کالیبره شود.",
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 7. CEC estimate from clay + OM
# ---------------------------------------------------------------------------

def cec_estimate(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    clay = float(p.get("clay_pct", 25))
    om = float(p.get("om_pct", 2.0))
    # cmol/kg rough: clay 0.5 per % + OM 2 per %
    cec = 0.5 * clay + 2.0 * om
    return {
        "model": "cec_estimate",
        "cec_cmol_kg": round(cec, 2),
        "clay_pct": clay,
        "om_pct": om,
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 8. Salinity leaching requirement
# ---------------------------------------------------------------------------

def salinity_leaching(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    ec_e = float(p.get("ec_extract_ds_m", 4.0))
    ec_w = float(p.get("ec_water_ds_m", 1.0))
    # Rhoades: LR = ECw / (5*ECe - ECw) approximate for leaching fraction
    den = 5.0 * ec_e - ec_w
    lr = (ec_w / den) if den > 0.1 else 0.5
    lr = _clamp(lr, 0.05, 0.5)
    et = float(p.get("et_mm_season", 600))
    water_need = et / (1.0 - lr)
    return {
        "model": "salinity_leaching_requirement",
        "leaching_fraction": round(lr, 4),
        "irrigation_mm_season": round(water_need, 1),
        "extra_leach_mm": round(water_need - et, 1),
        "ec_extract_ds_m": ec_e,
        "ec_water_ds_m": ec_w,
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 9. Sodicity ESP / gypsum
# ---------------------------------------------------------------------------

def sodicity_gypsum(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    esp = float(p.get("esp_pct", 18))
    target_esp = float(p.get("target_esp_pct", 10))
    cec = float(p.get("cec_cmol_kg", 20))
    depth_cm = float(p.get("depth_cm", 30))
    bd = float(p.get("bulk_density_mg_m3", 1.4))
    if esp <= target_esp:
        gypsum = 0.0
    else:
        # meq exchangeable Na to replace
        na_meq = (esp - target_esp) / 100.0 * cec
        # gypsum t/ha ≈ na_meq * depth * bd * 0.086
        gypsum = na_meq * depth_cm * bd * 0.086
    risk = "high" if esp >= 15 else "moderate" if esp >= 10 else "low"
    return {
        "model": "sodicity_gypsum",
        "esp_pct": esp,
        "gypsum_t_ha": round(max(0.0, gypsum), 2),
        "risk": risk,
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 10. Compaction / porosity stress
# ---------------------------------------------------------------------------

def compaction_index(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    bd = float(p.get("bulk_density_mg_m3", 1.55))
    clay = float(p.get("clay_pct", 25))
    # critical BD higher for sandy soils
    crit = 1.75 - 0.005 * clay
    ratio = bd / crit
    status = "severe" if ratio > 1.05 else "moderate" if ratio > 0.95 else "ok"
    return {
        "model": "compaction_index",
        "bulk_density": bd,
        "critical_bd": round(crit, 3),
        "ratio": round(ratio, 3),
        "status": status,
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 11. RUSLE-lite soil loss
# ---------------------------------------------------------------------------

def rusle_lite(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    R = float(p.get("R", 100))
    K = float(p.get("K", 0.3))
    LS = float(p.get("LS", 1.0))
    C = float(p.get("C", 0.2))
    P = float(p.get("P", 1.0))
    a = R * K * LS * C * P  # t/ha/y order
    return {
        "model": "rusle_lite",
        "soil_loss_t_ha_y": round(a, 3),
        "factors": {"R": R, "K": K, "LS": LS, "C": C, "P": P},
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 12. Compost / biochar amendment C input
# ---------------------------------------------------------------------------

def amendment_carbon(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    rate = float(p.get("rate_t_ha", 10))
    kind = str(p.get("kind", "compost")).lower()
    c_frac = {"compost": 0.25, "manure": 0.20, "biochar": 0.70, "straw": 0.42}.get(kind, 0.25)
    stable = {"compost": 0.35, "manure": 0.25, "biochar": 0.85, "straw": 0.15}.get(kind, 0.3)
    c_in = rate * c_frac
    stable_c = c_in * stable
    return {
        "model": "amendment_carbon",
        "kind": kind,
        "rate_t_ha": rate,
        "c_input_t_ha": round(c_in, 3),
        "stable_c_t_ha": round(stable_c, 3),
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 13. N leaching index (simple climatic)
# ---------------------------------------------------------------------------

def n_leaching_index(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    precip = float(p.get("precip_mm_y", 400))
    et = float(p.get("et_mm_y", 1200))
    surplus = max(0.0, precip - 0.7 * et)
    n_rate = float(p.get("n_fert_kg_ha", 120))
    # index 0–100
    idx = _clamp(0.15 * surplus + 0.2 * n_rate, 0, 100)
    risk = "high" if idx > 50 else "moderate" if idx > 25 else "low"
    return {
        "model": "n_leaching_index",
        "index": round(idx, 1),
        "water_surplus_mm": round(surplus, 1),
        "risk": risk,
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 14. Profile available N (kg/ha)
# ---------------------------------------------------------------------------

def profile_available_n(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    layers = p.get("layers") or [
        {"depth_cm": 30, "no3_mg_kg": 15, "nh4_mg_kg": 5, "bd": 1.35},
        {"depth_cm": 30, "no3_mg_kg": 8, "nh4_mg_kg": 3, "bd": 1.4},
        {"depth_cm": 40, "no3_mg_kg": 4, "nh4_mg_kg": 2, "bd": 1.45},
    ]
    total = 0.0
    detail = []
    for L in layers:
        d = float(L.get("depth_cm", 30))
        bd = float(L.get("bd", 1.4))
        no3 = float(L.get("no3_mg_kg", 0))
        nh4 = float(L.get("nh4_mg_kg", 0))
        # kg/ha = mg/kg * bd * depth_cm / 10
        kg = (no3 + nh4) * bd * d / 10.0
        total += kg
        detail.append({"depth_cm": d, "n_kg_ha": round(kg, 2)})
    return {
        "model": "profile_available_n",
        "total_n_kg_ha": round(total, 2),
        "layers": detail,
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 15. Green-Ampt infiltration lite
# ---------------------------------------------------------------------------

def infiltration_green_ampt(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    Ks = float(p.get("ks_mm_h", 10))
    psi = float(p.get("suction_mm", 100))
    dtheta = float(p.get("delta_theta", 0.2))
    hours = float(p.get("hours", 2))
    # cumulative F ≈ Ks*t + psi*dtheta*ln(1+F/(psi*dtheta)) iterative
    F = 0.0
    dt = 0.1
    t = 0.0
    series = []
    while t < hours:
        denom = psi * dtheta
        f = Ks * (1.0 + denom / max(F, 1e-3))
        F += f * dt
        t += dt
        if abs(t * 10 - round(t * 10)) < 1e-6:
            series.append({"hour": round(t, 2), "F_mm": round(F, 2), "f_mm_h": round(f, 2)})
    return {
        "model": "green_ampt_lite",
        "cumulative_infiltration_mm": round(F, 2),
        "hours": hours,
        "series": series[:30],
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 16. Soil temperature simple profile
# ---------------------------------------------------------------------------

def soil_temperature_profile(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    t_air = float(p.get("t_air_c", 25))
    t_mean = float(p.get("t_annual_mean_c", 15))
    depths = p.get("depths_cm") or [5, 10, 20, 50, 100]
    damping = float(p.get("damping_cm", 40))
    out = []
    for z in depths:
        z = float(z)
        t = t_mean + (t_air - t_mean) * math.exp(-z / damping)
        out.append({"depth_cm": z, "t_c": round(t, 2)})
    return {
        "model": "soil_temperature_profile",
        "profile": out,
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 17. Soil health composite score
# ---------------------------------------------------------------------------

def soil_health_score(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    soc = float(p.get("soc_pct", 1.2))
    ph = float(p.get("ph", 7.0))
    bd = float(p.get("bulk_density_mg_m3", 1.35))
    ec = float(p.get("ec_ds_m", 1.0))
    # scores 0–100
    s_soc = _clamp(soc / 3.0 * 100, 0, 100)
    s_ph = 100 - abs(ph - 6.8) * 25
    s_ph = _clamp(s_ph, 0, 100)
    s_bd = _clamp((1.7 - bd) / 0.5 * 100, 0, 100)
    s_ec = _clamp(100 - (ec - 0.5) * 20, 0, 100)
    total = 0.35 * s_soc + 0.25 * s_ph + 0.2 * s_bd + 0.2 * s_ec
    grade = "A" if total >= 80 else "B" if total >= 65 else "C" if total >= 50 else "D"
    return {
        "model": "soil_health_score",
        "score": round(total, 1),
        "grade": grade,
        "components": {
            "soc": round(s_soc, 1),
            "ph": round(s_ph, 1),
            "bulk_density": round(s_bd, 1),
            "salinity": round(s_ec, 1),
        },
        "completed_at": _now(),
    }


# ---------------------------------------------------------------------------
# 18. KGE / PBIAS evaluate helper (soil series)
# ---------------------------------------------------------------------------

def evaluate_soil_series(
    observed: list[float],
    simulated: list[float],
    variable: str = "soil",
) -> dict[str, Any]:
    pack = evaluate_series(observed, simulated, variable=variable)
    pack["kge_standalone"] = None if math.isnan(kge(observed, simulated)) else round(
        kge(observed, simulated), 5
    )
    pack["pbias_standalone"] = None if math.isnan(pbias(observed, simulated)) else round(
        pbias(observed, simulated), 5
    )
    pack["kge_notes_fa"] = (
        "KGE=1 ایده‌آل؛ کاهش به‌خاطر همبستگی، نسبت انحراف‌معیار یا بایاس."
    )
    pack["pbias_notes_fa"] = (
        "PBIAS مثبت = بیش‌برآورد مدل؛ |PBIAS|<10% معمولاً خوب برای جریان/نیتروژن."
    )
    return pack


CATALOG: list[dict[str, str]] = [
    {"id": "nitrate_leaching", "endpoint": "POST /api/v1/science/soil/nitrate-leaching", "fa": "آبشویی لایه‌ای نیترات"},
    {"id": "texture_hydrology", "endpoint": "POST /api/v1/science/soil/texture-hydrology", "fa": "FC/WP/AWC از بافت"},
    {"id": "soc_stock", "endpoint": "POST /api/v1/science/soil/soc-stock", "fa": "ذخیره کربن آلی"},
    {"id": "liming", "endpoint": "POST /api/v1/science/soil/liming", "fa": "نیاز آهک"},
    {"id": "cec", "endpoint": "POST /api/v1/science/soil/cec", "fa": "تخمین CEC"},
    {"id": "salinity_lr", "endpoint": "POST /api/v1/science/soil/salinity-leaching", "fa": "نیاز آبشویی شوری"},
    {"id": "gypsum", "endpoint": "POST /api/v1/science/soil/gypsum", "fa": "گچ برای سدیمی"},
    {"id": "compaction", "endpoint": "POST /api/v1/science/soil/compaction", "fa": "شاخص تراکم"},
    {"id": "rusle", "endpoint": "POST /api/v1/science/soil/rusle", "fa": "فرسایش RUSLE-lite"},
    {"id": "amendment_c", "endpoint": "POST /api/v1/science/soil/amendment-carbon", "fa": "کربن اصلاح‌کننده"},
    {"id": "n_leach_index", "endpoint": "POST /api/v1/science/soil/n-leaching-index", "fa": "شاخص آبشویی N"},
    {"id": "profile_n", "endpoint": "POST /api/v1/science/soil/profile-n", "fa": "N قابل دسترس پروفیل"},
    {"id": "infiltration", "endpoint": "POST /api/v1/science/soil/infiltration", "fa": "نفوذ Green-Ampt"},
    {"id": "soil_temp", "endpoint": "POST /api/v1/science/soil/temperature", "fa": "دمای پروفیل"},
    {"id": "health", "endpoint": "POST /api/v1/science/soil/health-score", "fa": "امتیاز سلامت خاک"},
    {"id": "metrics", "endpoint": "POST /api/v1/science/soil/evaluate", "fa": "KGE/PBIAS/NSE"},
]


def soil_catalog() -> dict[str, Any]:
    return {"count": len(CATALOG), "items": CATALOG}
