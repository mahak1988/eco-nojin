"""User-facing explanations (fa/en) for science model outputs."""

from __future__ import annotations

from typing import Any


def analyze_scs_cn(result: dict[str, Any]) -> dict[str, Any]:
    inp = result.get("inputs") or {}
    out = result.get("outputs") or {}
    cn = float(inp.get("curve_number", 75))
    s = float(inp.get("S_mm", 0))
    runoff = float(out.get("runoff_mm_year", 0))
    et = float(out.get("et_actual_mm_year", 0))
    wy = float(out.get("water_yield_mm_year", 0))
    sed = float(out.get("sediment_t_km2_year", 0))
    precip = float(inp.get("precip_mm_year", 0))

    fa = []
    en = []
    fa.append(
        f"ظرفیت نگهداشت خاک (S) حدود {s:.0f} میلی‌متر است (از شماره منحنی CN={cn:.0f}). "
        f"هرچه CN بالاتر، رواناب محتمل‌تر است."
    )
    en.append(
        f"Soil retention S≈{s:.0f} mm from Curve Number CN={cn:.0f}. Higher CN → more runoff potential."
    )
    if runoff < 1:
        fa.append(
            f"با بارش سالانه {precip:.0f} mm و پخش روی روزهای مرطوب، آستانه 0.2·S برای رواناب سطحی اغلب رد نشده؛ "
            f"رواناب محاسبه‌شده نزدیک صفر است. آب بیشتر به نفوذ و تبخیر می‌رود."
        )
        en.append(
            f"With {precip:.0f} mm/year split over wet days, events rarely exceed 0.2·S; surface runoff≈0. "
            f"Water partitions mainly to infiltration and ET."
        )
    else:
        fa.append(f"رواناب سطحی سالانه حدود {runoff:.1f} mm برآورد شد.")
        en.append(f"Estimated annual surface runoff ≈ {runoff:.1f} mm.")
    fa.append(
        f"تبخیر-تعرق واقعی ≈ {et:.0f} mm و آبدهی حوضه (رواناب+پایه) ≈ {wy:.0f} mm/سال. "
        f"شاخص رسوب تقریبی ≈ {sed:.2f} t/km²/year (پروکسی ساده، نه MUSLE کامل)."
    )
    en.append(
        f"Actual ET≈{et:.0f} mm; basin water yield≈{wy:.0f} mm/year. "
        f"Sediment proxy≈{sed:.2f} t/km²/year (not full MUSLE)."
    )
    fa.append(
        "فرمول SCS-CN: Q=(P−0.2S)²/(P+0.8S) وقتی P>0.2S و S=25.4·(1000/CN−10). "
        "این مدل تصمیم‌یار است نه نرم‌افزار رسمی SWAT+."
    )
    en.append(
        "SCS-CN: Q=(P−0.2S)²/(P+0.8S) if P>0.2S; S=25.4·(1000/CN−10). Decision-support only, not SWAT+."
    )
    return {
        "summary_fa": " ".join(fa),
        "summary_en": " ".join(en),
        "formulas": [
            "S = 25.4 × (1000/CN − 10)  [mm]",
            "Q = (P − 0.2S)² / (P + 0.8S)  if P > 0.2S else 0",
            "Water yield ≈ runoff + baseflow",
        ],
        "advice_fa": "برای کاهش رواناب: پوشش گیاهی، مالچ، کاهش شیب مؤثر، و CN مدیریت‌شده (خاک‌ورزی حفاظتی).",
        "advice_en": "To cut runoff: cover crops, mulch, conservation tillage (lower effective CN).",
    }


def analyze_aquacrop(result: dict[str, Any]) -> dict[str, Any]:
    y_rel = float(result.get("yield_relative", 0))
    irr = float(result.get("irrigation_need_mm", 0))
    etc = float(result.get("etc_mm", 0))
    ky = float(result.get("ky", 1.15))
    crop = str(result.get("crop", "crop"))
    fa = [
        f"برای {crop}: نسبت تعرق واقعی به بالقوه (Ta/Tc) به عملکرد نسبی {y_rel:.0%} رسیده (Ky={ky}).",
        f"نیاز آبی فصل (ETc) ≈ {etc:.0f} mm؛ آبیاری تجمعی شبیه‌سازی ≈ {irr:.0f} mm.",
        "معادله عملکرد FAO-33: Y/Yx = 1 − Ky·(1 − Ta/Tc). تنش آبی وقتی تخلیه ریشه از RAW بیشتر شود Ks را کم می‌کند.",
        "مدل مفهومی AquaCrop است؛ باینری رسمی FAO نیست.",
    ]
    en = [
        f"For {crop}: relative yield {y_rel:.0%} from Ta/Tc with Ky={ky}.",
        f"Seasonal ETc≈{etc:.0f} mm; simulated irrigation≈{irr:.0f} mm.",
        "FAO-33: Y/Yx = 1 − Ky·(1 − Ta/Tc). Ks drops when root-zone depletion exceeds RAW.",
        "Conceptual AquaCrop-style balance — not the FAO binary.",
    ]
    if y_rel < 0.7:
        fa.append("عملکرد نسبی زیر ۷۰٪ است؛ آبیاری به‌موقع یا کاهش ET0 مؤثر (مالچ/تاریخ کاشت) را بررسی کنید.")
        en.append("Relative yield <70%: review irrigation timing or ET demand (mulch, planting date).")
    return {
        "summary_fa": " ".join(fa),
        "summary_en": " ".join(en),
        "formulas": [
            "ETc = Kc × ET0",
            "Ks = 1 if Dr ≤ RAW else (TAW−Dr)/(TAW−RAW)",
            "Y/Yx = 1 − Ky × (1 − Ta/Tc)",
        ],
        "advice_fa": "آستانه آبیاری و TAW را با بافت خاک مزرعه تنظیم کنید؛ NDVI برای کالیبره پوشش تاج مفید است.",
        "advice_en": "Tune irrigation threshold and TAW to soil texture; NDVI helps calibrate canopy cover.",
    }


def analyze_rothc(result: dict[str, Any]) -> dict[str, Any]:
    d0 = float(result.get("soc_initial", 0))
    d1 = float(result.get("soc_final", 0))
    delta = float(result.get("delta", d1 - d0))
    mods = result.get("rate_modifiers") or {}
    fa = [
        f"کربن آلی خاک از {d0:.1f} به {d1:.1f} t C/ha تغییر کرد (Δ={delta:+.2f}).",
        "استخرها: DPM (سریع)، RPM (کند)، BIO، HUM، IOM (خنثی). نرخ‌ها با دما (a)، رطوبت (b) و پوشش (c) تعدیل می‌شوند.",
        f"ضرایب نرخ: a≈{mods.get('a_temp', '—')}، b≈{mods.get('b_moisture', '—')}، c={mods.get('c_cover', '—')}.",
        "مرجع: Coleman & Jenkinson RothC-26.3 (پیاده‌سازی باز).",
    ]
    en = [
        f"SOC {d0:.1f} → {d1:.1f} t C/ha (Δ={delta:+.2f}).",
        "Pools: DPM, RPM, BIO, HUM, IOM; rates modified by temperature, moisture, plant cover.",
        f"Rate modifiers a≈{mods.get('a_temp')}, b≈{mods.get('b_moisture')}, c={mods.get('c_cover')}.",
        "Ref: Coleman & Jenkinson RothC-26.3 (open reimplementation).",
    ]
    return {
        "summary_fa": " ".join(fa),
        "summary_en": " ".join(en),
        "formulas": [
            "a(T) = 47.91 / (1 + exp(106.06/(T+18.27)))",
            "decomposed = pool × (1 − exp(−k·a·b·c))",
            "BIO+HUM fraction from clay factor x",
        ],
        "advice_fa": "برای افزایش SOC: بقایای بیشتر، کود آلی، کاهش آیش برهنه. حساسیت جهانی: معمولاً c_input و اقلیم.",
        "advice_en": "To raise SOC: more residues, manure, less bare fallow. Global SA often highlights C input and climate.",
    }


def analyze_rusle(result: dict[str, Any]) -> dict[str, Any]:
    inp = result.get("inputs") or {}
    out = result.get("outputs") or {}
    A = float(out.get("A_t_ha_year", 0))
    risk = str(out.get("risk_class", "—"))
    fa = [
        f"تلفات خاک سالانه A≈{A:.2f} t/ha/year با کلاس ریسک «{risk}».",
        f"عوامل: R={inp.get('R')}، K={inp.get('K')}، LS={inp.get('LS')}، C={inp.get('C')}، P={inp.get('P')}.",
        "A = R·K·LS·C·P (USLE/RUSLE). نرم‌افزار رسمی USDA RUSLE2 نیست.",
    ]
    en = [
        f"Annual soil loss A≈{A:.2f} t/ha/year (risk «{risk}»).",
        f"Factors R={inp.get('R')}, K={inp.get('K')}, LS={inp.get('LS')}, C={inp.get('C')}, P={inp.get('P')}.",
        "A = R·K·LS·C·P — not USDA RUSLE2 software.",
    ]
    advice_fa = "کاهش C (پوشش) و P (تراس/کشت روی خطوط تراز) و مدیریت شیب مؤثرترین اهرم‌ها هستند."
    if A >= 15:
        advice_fa = "فرسایش بالا: فوری پوشش دائمی، بانکت/تراس، و کاهش طول شیب را در اولویت بگذارید."
    return {
        "summary_fa": " ".join(fa),
        "summary_en": " ".join(en),
        "formulas": ["A = R · K · LS · C · P", "LS from slope length & steepness"],
        "advice_fa": advice_fa,
        "advice_en": "Lower C (cover) and improve support practice P; manage slope length.",
    }


def analyze_ndvi_canopy(result: dict[str, Any]) -> dict[str, Any]:
    n = int(result.get("count") or 0)
    provider = str(result.get("provider", "unknown"))
    ndvi = result.get("ndvi") or []
    avg = sum(ndvi) / len(ndvi) if ndvi else 0.0
    fa = [
        f"{n} نمونه NDVI از منبع «{provider}». میانگین NDVI≈{avg:.2f}.",
        "تبدیل به پوشش تاج: CC = clip((NDVI−0.15)/(0.85−0.15)) بین ۰.۰۵ و ۰.۹۸ — برای مقیاس Kc در بیلان آب.",
        "NDVI=(NIR−Red)/(NIR+Red). بدون GEE ممکن است سری synthetic باشد.",
    ]
    en = [
        f"{n} NDVI samples from «{provider}»; mean NDVI≈{avg:.2f}.",
        "Canopy CC = clip((NDVI−0.15)/(0.85−0.15)) used to scale Kc in water balance.",
        "NDVI=(NIR−Red)/(NIR+Red). Without GEE credentials series may be synthetic.",
    ]
    return {
        "summary_fa": " ".join(fa),
        "summary_en": " ".join(en),
        "formulas": [
            "NDVI = (NIR − Red) / (NIR + Red)",
            "CC = clamp((NDVI − 0.15) / 0.70, 0.05, 0.98)",
        ],
        "advice_fa": "برای NDVI واقعی، Service Account جیمیل‌ارث را طبق docs/GEE_SETUP.md تنظیم کنید.",
        "advice_en": "For live NDVI, configure GEE service account (docs/GEE_SETUP.md).",
    }


def attach_analysis(model_key: str, result: dict[str, Any]) -> dict[str, Any]:
    out = dict(result)
    if model_key in ("scs", "swat", "scs_cn_basin_balance"):
        out["analysis"] = analyze_scs_cn(result)
    elif model_key in ("aquacrop", "aquacrop_fao_conceptual", "aquacrop_advanced"):
        out["analysis"] = analyze_aquacrop(result)
    elif model_key in ("rothc", "rothc_26_3"):
        out["analysis"] = analyze_rothc(result)
    elif model_key in ("rusle", "rusle2", "rusle2_proxy"):
        out["analysis"] = analyze_rusle(result)
    elif model_key in ("ndvi", "ndvi_canopy"):
        out["analysis"] = analyze_ndvi_canopy(result)
    return out
