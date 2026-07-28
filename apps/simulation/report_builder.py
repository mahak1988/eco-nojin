"""
Structured final reports for science / soil runs.
Sections: executive summary, metrics table, formulas, sensitivity (optional), risks, actions.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional


def _sev(level: str) -> str:
    return {"info": "info", "low": "low", "moderate": "moderate", "high": "high", "critical": "critical"}.get(
        level, "info"
    )


def build_final_report(
    *,
    title_fa: str,
    title_en: str,
    model_id: str,
    result: dict[str, Any],
    sensitivity: Optional[dict[str, Any]] = None,
    extra_sections: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    analysis = result.get("analysis") or {}
    metrics: list[dict[str, Any]] = []

    # harvest common metrics
    for key in (
        "soc_initial",
        "soc_final",
        "delta",
        "yield_relative",
        "irrigation_need_mm",
        "etc_mm",
        "yield_t_ha",
    ):
        if key in result and isinstance(result[key], (int, float)):
            metrics.append({"id": key, "value": result[key]})

    outs = result.get("outputs") or {}
    if isinstance(outs, dict):
        for k, v in outs.items():
            if isinstance(v, (int, float)):
                metrics.append({"id": k, "value": v})
            elif k == "risk_class":
                metrics.append({"id": k, "value": v})

    risks: list[dict[str, str]] = []
    if "yield_relative" in result:
        yr = float(result["yield_relative"])
        if yr < 0.5:
            risks.append({"severity": "high", "fa": "عملکرد نسبی بسیار پایین — تنش آبی جدی.", "en": "Very low relative yield — severe water stress."})
        elif yr < 0.75:
            risks.append({"severity": "moderate", "fa": "عملکرد نسبی متوسط؛ زمان‌بندی آبیاری را بررسی کنید.", "en": "Moderate relative yield."})
    if outs.get("risk_class") in ("high", "severe"):
        risks.append(
            {
                "severity": "high" if outs["risk_class"] == "high" else "critical",
                "fa": f"ریسک فرسایش: {outs['risk_class']}",
                "en": f"Erosion risk: {outs['risk_class']}",
            }
        )
    if "delta" in result and float(result["delta"]) < -1:
        risks.append({"severity": "moderate", "fa": "کاهش SOC بیش از ۱ t C/ha در افق شبیه‌سازی.", "en": "SOC decline >1 t C/ha over simulation."})

    sa_block = None
    if sensitivity:
        sobol = sensitivity.get("sobol") or {}
        top = (sobol.get("indices") or [])[:3]
        sa_block = {
            "top_ST": top,
            "src_r2": (sensitivity.get("src") or {}).get("r_squared"),
            "notes_fa": sensitivity.get("notes_fa"),
            "notes_en": sensitivity.get("notes_en"),
        }

    report = {
        "report_version": "1.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_id": model_id,
        "title_fa": title_fa,
        "title_en": title_en,
        "executive_summary_fa": analysis.get("summary_fa") or result.get("citation") or title_fa,
        "executive_summary_en": analysis.get("summary_en") or title_en,
        "formulas": analysis.get("formulas") or [],
        "metrics": metrics,
        "risks": risks,
        "recommendations_fa": analysis.get("advice_fa") or "",
        "recommendations_en": analysis.get("advice_en") or "",
        "sensitivity": sa_block,
        "sections": extra_sections or [],
        "raw_ref": {"model": result.get("model"), "citation": result.get("citation")},
        "disclaimer_fa": "گزارش تصمیم‌یار است؛ جایگزین نقشه‌برداری میدانی یا باینری‌های رسمی USDA/FAO نیست.",
        "disclaimer_en": "Decision-support only; not a substitute for field survey or official model binaries.",
    }
    return report


def report_rothc(result: dict[str, Any], sensitivity: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    series = result.get("series") or []
    extra = [
        {
            "id": "pools",
            "title_fa": "استخرهای کربن",
            "title_en": "Carbon pools",
            "body_fa": "DPM سریع، RPM کند، BIO زیست‌توده میکروبی، HUM هوموس، IOM خنثی.",
            "body_en": "DPM fast, RPM slow, BIO microbial, HUM humus, IOM inert.",
            "table": series[-1] if series else {},
        }
    ]
    return build_final_report(
        title_fa="گزارش نهایی کربن خاک (RothC-26.3)",
        title_en="Final soil carbon report (RothC-26.3)",
        model_id="rothc_26_3",
        result=result,
        sensitivity=sensitivity,
        extra_sections=extra,
    )


def report_rusle(result: dict[str, Any], sensitivity: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return build_final_report(
        title_fa="گزارش نهایی فرسایش خاک (RUSLE)",
        title_en="Final soil erosion report (RUSLE)",
        model_id="rusle2_proxy",
        result=result,
        sensitivity=sensitivity,
    )


def report_aquacrop(result: dict[str, Any], sensitivity: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return build_final_report(
        title_fa="گزارش نهایی آب-محصول (AquaCrop مفهومی)",
        title_en="Final crop-water report (conceptual AquaCrop)",
        model_id="aquacrop_advanced",
        result=result,
        sensitivity=sensitivity,
    )


def report_scs(result: dict[str, Any], sensitivity: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return build_final_report(
        title_fa="گزارش نهایی بیلان حوضه (SCS-CN)",
        title_en="Final basin water balance report (SCS-CN)",
        model_id="scs_cn_basin_balance",
        result=result,
        sensitivity=sensitivity,
    )
