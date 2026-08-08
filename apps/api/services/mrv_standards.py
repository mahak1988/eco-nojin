"""
Hydroma MRV standards engine — assurance levels L1/L2/L3 aligned with:
- IPCC inventory tiers (default / country-specific / measurement-based)
- Hybrid protocols (Verra VM0042, Gold Standard SOC, FAO GSOC MRV, CAR SEP)
- dMRV evidence packaging (satellite + field + model)

Pure functions; no I/O.
"""

from __future__ import annotations

from typing import Any, Literal

AssuranceLevel = Literal["L1", "L2", "L3"]

# Buffer pool style permanence hold (AFOLU non-permanence risk tool spirit)
PERMANENCE_BUFFER: dict[str, float] = {
    "L1": 0.20,  # model-heavy → higher buffer
    "L2": 0.12,
    "L3": 0.08,  # multi-source → lower buffer
}

# Uncertainty multiplier applied as discount on quality (1 - u)
UNCERTAINTY_FLOOR: dict[str, float] = {
    "L1": 0.25,
    "L2": 0.15,
    "L3": 0.08,
}

# Max quality score by level (caps over-optimism)
Q_CAP: dict[str, float] = {
    "L1": 1.00,
    "L2": 1.10,
    "L3": 1.20,
}

STANDARDS_REF = {
    "ipcc_tiers": "IPCC GHG Inventory Guidelines — Tier 1/2/3",
    "fao_gsoc": "FAO GSOC MRV Protocol",
    "verra_vm0042": "Verra VM0042 Improved Agricultural Land Management",
    "gold_standard_soc": "Gold Standard Soil Organic Carbon Framework",
    "car_sep": "Climate Action Reserve Soil Enrichment Protocol",
    "icvcm_ccp": "ICVCM Core Carbon Principles",
    "iso_14064": "ISO 14064-2 project-level GHG",
    "iso_14065": "ISO 14065 VVB accreditation context",
}


def classify_assurance(
    *,
    satellite_available: bool = False,
    field_data_present: bool = False,
    model_present: bool = False,
    lab_measurement: bool = False,
) -> AssuranceLevel:
    """
    L3: satellite + field/lab + model (triple)
    L2: any two of {satellite, field/lab, model}
    L1: single source or defaults only
    """
    field = field_data_present or lab_measurement
    sources = sum([satellite_available, field, model_present])
    if sources >= 3:
        return "L3"
    if sources >= 2:
        return "L2"
    return "L1"


def quality_from_mrv_v2(
    *,
    ndvi_observed: float | None = None,
    ndvi_expected: float | None = None,
    model_yield_t_ha: float | None = None,
    field_yield_t_ha: float | None = None,
    model_soc_t_ha: float | None = None,
    lab_soc_t_ha: float | None = None,
    field_data_present: bool = False,
    satellite_available: bool = False,
    model_present: bool = False,
    additionality_score: float = 1.0,
    leakage_risk: float = 0.0,
) -> dict[str, Any]:
    """
    Enhanced Q with explicit L1/L2/L3, uncertainty, additionality, leakage.
    Backward-compatible keys: quality_score, components, inputs.
    """
    components: dict[str, float] = {}
    base = 0.80

    if model_soc_t_ha is not None or model_yield_t_ha is not None:
        model_present = True

    if ndvi_observed is not None and ndvi_expected is not None and ndvi_expected != 0:
        rel_err = abs(ndvi_observed - ndvi_expected) / max(abs(ndvi_expected), 1e-6)
        ndvi_score = max(0.0, 1.0 - rel_err)
        components["ndvi_agreement"] = round(ndvi_score, 4)
        base = 0.85 + 0.2 * ndvi_score
        satellite_available = True

    # Yield agreement
    if model_yield_t_ha is not None and field_yield_t_ha is not None and model_yield_t_ha > 0:
        rel_err = abs(model_yield_t_ha - field_yield_t_ha) / max(model_yield_t_ha, 1e-6)
        model_score = max(0.0, 1.0 - rel_err)
        components["model_field_yield_agreement"] = round(model_score, 4)
        base = (base + (0.88 + 0.25 * model_score)) / 2.0
        field_data_present = True
        model_present = True

    # SOC lab vs model (soil carbon pathway)
    if model_soc_t_ha is not None and lab_soc_t_ha is not None and model_soc_t_ha > 0:
        rel_err = abs(model_soc_t_ha - lab_soc_t_ha) / max(model_soc_t_ha, 1e-6)
        soc_score = max(0.0, 1.0 - rel_err)
        components["model_lab_soc_agreement"] = round(soc_score, 4)
        base = (base + (0.90 + 0.25 * soc_score)) / 2.0
        field_data_present = True
        model_present = True

    level = classify_assurance(
        satellite_available=satellite_available,
        field_data_present=field_data_present,
        model_present=model_present,
        lab_measurement=lab_soc_t_ha is not None,
    )

    bonus = 0.0
    if satellite_available:
        bonus += 0.04
        components["satellite_bonus"] = 0.04
    if field_data_present:
        bonus += 0.06
        components["field_bonus"] = 0.06
    if model_present:
        bonus += 0.03
        components["model_bonus"] = 0.03
    if satellite_available and field_data_present and model_present:
        bonus += 0.05
        components["triple_source_bonus"] = 0.05

    q_raw = base + bonus
    u = UNCERTAINTY_FLOOR[level]
    # higher agreement → slightly lower effective uncertainty
    if "ndvi_agreement" in components:
        u *= max(0.7, 1.0 - 0.3 * components["ndvi_agreement"])
    if "model_lab_soc_agreement" in components:
        u *= max(0.7, 1.0 - 0.3 * components["model_lab_soc_agreement"])

    q_after_u = q_raw * (1.0 - u)
    q_capped = min(Q_CAP[level], max(0.45, q_after_u))

    add = max(0.0, min(1.0, additionality_score))
    leak = max(0.0, min(0.5, leakage_risk))
    buffer = PERMANENCE_BUFFER[level]

    # Effective mint factor relative to raw V*Fc*R*S
    effective_factor = q_capped * add * (1.0 - leak) * (1.0 - buffer)

    return {
        "quality_score": round(q_capped, 4),
        "assurance_level": level,
        "uncertainty": round(u, 4),
        "permanence_buffer": buffer,
        "additionality_score": round(add, 4),
        "leakage_risk": round(leak, 4),
        "effective_mint_factor": round(effective_factor, 4),
        "components": components,
        "standards_refs": list(STANDARDS_REF.keys()),
        "inputs": {
            "ndvi_observed": ndvi_observed,
            "ndvi_expected": ndvi_expected,
            "model_yield_t_ha": model_yield_t_ha,
            "field_yield_t_ha": field_yield_t_ha,
            "model_soc_t_ha": model_soc_t_ha,
            "lab_soc_t_ha": lab_soc_t_ha,
            "field_data_present": field_data_present,
            "satellite_available": satellite_available,
            "model_present": model_present,
        },
        "level_policy": {
            "L1": "Model or single remote source; conservative buffer 20%",
            "L2": "Two independent evidence classes; buffer 12%",
            "L3": "Satellite + field/lab + model; buffer 8%; preferred for issuance",
        },
    }


def compute_issuable(
    measured_value: float,
    credit_factor: float,
    mrv: dict[str, Any],
    region_multiplier: float = 1.0,
    scarcity: float = 1.0,
) -> dict[str, Any]:
    """
    Issuable = V * Fc * effective_mint_factor * R * S
    where effective already embeds Q, additionality, leakage, permanence buffer.
    """
    if measured_value <= 0:
        return {"ok": False, "error": "measured_value_must_be_positive", "issuable": 0.0}
    R = max(0.8, min(1.3, region_multiplier))
    S = max(0.2, min(1.0, scarcity))
    eff = float(mrv.get("effective_mint_factor", mrv.get("quality_score", 0.8)))
    raw = measured_value * credit_factor * eff * R * S
    return {
        "ok": True,
        "issuable": round(raw, 6),
        "assurance_level": mrv.get("assurance_level"),
        "formula": "V * Fc * Q_eff * R * S  (Q_eff includes buffer, additionality, leakage)",
        "inputs": {
            "V": measured_value,
            "Fc": credit_factor,
            "Q_eff": eff,
            "R": R,
            "S": S,
        },
    }
