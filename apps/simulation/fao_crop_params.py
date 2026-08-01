"""
Reference crop / water-productivity parameters for Eco Nojin science models.

Sources (order-of-magnitude, published guidance — not a FAO software dump):
  - FAO Irrigation and Drainage Paper 56 (Allen et al.): crop coefficients Kc
  - FAO Irrigation and Drainage Paper 33 (Doorenbos & Kassam): yield response Ky
  - FAO AquaCrop concepts (Paper 66 family): TAW/RAW framing, water productivity
  - Typical irrigated potential yields from regional agronomy tables (indicative)

These values are embedded so the API works offline and every run can cite
``source`` / ``reference`` fields. They are decision-support defaults, not
a substitute for local calibration or the official FAO AquaCrop binary.
"""

from __future__ import annotations

from typing import Any

# FAO-56 mid-season Kc (typical), FAO-33 Ky (seasonal), indicative Yx
FAO_CROP_LIBRARY: dict[str, dict[str, Any]] = {
    "wheat": {
        "label_en": "Wheat",
        "label_fa": "گندم",
        "kc_mid": 1.15,
        "kc_ini": 0.40,
        "kc_end": 0.40,
        "ky": 1.15,
        "yx_t_ha": 6.0,
        "cycle_days": 120,
        "raw_fraction": 0.55,
        "taw_mm_typical": 120.0,
        "wp_g_m2": 15.0,
        "references": [
            "FAO56 Table 12 (Kc mid wheat ≈ 1.15)",
            "FAO33 Ky wheat ≈ 1.15",
        ],
    },
    "maize": {
        "label_en": "Maize",
        "label_fa": "ذرت",
        "kc_mid": 1.20,
        "kc_ini": 0.30,
        "kc_end": 0.60,
        "ky": 1.25,
        "yx_t_ha": 10.0,
        "cycle_days": 125,
        "raw_fraction": 0.55,
        "taw_mm_typical": 140.0,
        "wp_g_m2": 33.0,
        "references": [
            "FAO56 Kc mid maize ≈ 1.20",
            "FAO33 Ky maize ≈ 1.25",
        ],
    },
    "corn": {
        "label_en": "Maize (alias)",
        "label_fa": "ذرت",
        "kc_mid": 1.20,
        "kc_ini": 0.30,
        "kc_end": 0.60,
        "ky": 1.25,
        "yx_t_ha": 10.0,
        "cycle_days": 125,
        "raw_fraction": 0.55,
        "taw_mm_typical": 140.0,
        "wp_g_m2": 33.0,
        "references": ["Alias of maize — FAO56/FAO33"],
    },
    "rice": {
        "label_en": "Paddy rice",
        "label_fa": "برنج",
        "kc_mid": 1.20,
        "kc_ini": 1.05,
        "kc_end": 0.90,
        "ky": 1.10,
        "yx_t_ha": 7.0,
        "cycle_days": 120,
        "raw_fraction": 0.20,
        "taw_mm_typical": 80.0,
        "wp_g_m2": 19.0,
        "references": [
            "FAO56 Kc mid rice ≈ 1.05–1.20",
            "FAO33 Ky rice ≈ 1.10",
        ],
    },
    "barley": {
        "label_en": "Barley",
        "label_fa": "جو",
        "kc_mid": 1.10,
        "kc_ini": 0.30,
        "kc_end": 0.25,
        "ky": 1.10,
        "yx_t_ha": 5.0,
        "cycle_days": 110,
        "raw_fraction": 0.55,
        "taw_mm_typical": 110.0,
        "wp_g_m2": 15.0,
        "references": ["FAO56 barley Kc mid ≈ 1.10", "FAO33 Ky barley ≈ 1.10"],
    },
    "tomato": {
        "label_en": "Tomato",
        "label_fa": "گوجه‌فرنگی",
        "kc_mid": 1.15,
        "kc_ini": 0.60,
        "kc_end": 0.80,
        "ky": 1.15,
        "yx_t_ha": 60.0,
        "cycle_days": 135,
        "raw_fraction": 0.40,
        "taw_mm_typical": 100.0,
        "wp_g_m2": 18.0,
        "references": ["FAO56 tomato Kc mid ≈ 1.15", "FAO33 Ky tomato ≈ 1.05–1.15"],
    },
    "potato": {
        "label_en": "Potato",
        "label_fa": "سیب‌زمینی",
        "kc_mid": 1.15,
        "kc_ini": 0.50,
        "kc_end": 0.75,
        "ky": 1.10,
        "yx_t_ha": 35.0,
        "cycle_days": 130,
        "raw_fraction": 0.35,
        "taw_mm_typical": 100.0,
        "wp_g_m2": 18.0,
        "references": ["FAO56 potato Kc mid ≈ 1.15", "FAO33 Ky potato ≈ 1.10"],
    },
}

DEFAULT_CROP = "wheat"


def get_crop_params(crop: str | None) -> dict[str, Any]:
    key = str(crop or DEFAULT_CROP).lower().strip().split()[0]
    if key not in FAO_CROP_LIBRARY:
        key = DEFAULT_CROP
    base = dict(FAO_CROP_LIBRARY[key])
    base["crop_key"] = key
    base["library_version"] = "1.0.0"
    base["library_note"] = (
        "Embedded FAO56/FAO33 indicative defaults for offline DSS; calibrate locally."
    )
    return base


def list_crops() -> list[dict[str, Any]]:
    out = []
    for key, meta in FAO_CROP_LIBRARY.items():
        if key == "corn":
            continue
        out.append(
            {
                "id": key,
                "label_en": meta["label_en"],
                "label_fa": meta["label_fa"],
                "kc_mid": meta["kc_mid"],
                "ky": meta["ky"],
                "yx_t_ha": meta["yx_t_ha"],
                "references": meta["references"],
            }
        )
    return out
