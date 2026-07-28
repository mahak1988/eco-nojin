"""
Hydrological / biogeochemical skill metrics.

NSE (Nash–Sutcliffe Efficiency) and companions used for SOC/N series evaluation.

NSE = 1 − Σ(O−S)² / Σ(O−Ō)²
  1.0 = perfect
  0.0 = as good as mean of observations
  <0  = worse than mean

Common thresholds (Moriasi et al. 2007, adapted):
  NSE > 0.75  very good
  0.65–0.75   good
  0.50–0.65   satisfactory
  < 0.50      unsatisfactory
"""

from __future__ import annotations

import math
from typing import Any, Sequence


def _align(obs: Sequence[float], sim: Sequence[float]) -> tuple[list[float], list[float]]:
    n = min(len(obs), len(sim))
    if n == 0:
        return [], []
    return [float(obs[i]) for i in range(n)], [float(sim[i]) for i in range(n)]


def rmse(obs: Sequence[float], sim: Sequence[float]) -> float:
    o, s = _align(obs, sim)
    if not o:
        return float("nan")
    return math.sqrt(sum((o[i] - s[i]) ** 2 for i in range(len(o))) / len(o))


def mae(obs: Sequence[float], sim: Sequence[float]) -> float:
    o, s = _align(obs, sim)
    if not o:
        return float("nan")
    return sum(abs(o[i] - s[i]) for i in range(len(o))) / len(o)


def bias(obs: Sequence[float], sim: Sequence[float]) -> float:
    """Mean error sim − obs."""
    o, s = _align(obs, sim)
    if not o:
        return float("nan")
    return sum(s[i] - o[i] for i in range(len(o))) / len(o)


def pbias(obs: Sequence[float], sim: Sequence[float]) -> float:
    """Percent bias (%): 100 * Σ(S−O) / Σ(O). Negative → underestimation."""
    o, s = _align(obs, sim)
    if not o:
        return float("nan")
    den = sum(o)
    if abs(den) < 1e-15:
        return float("nan")
    return 100.0 * sum(s[i] - o[i] for i in range(len(o))) / den


def nse(obs: Sequence[float], sim: Sequence[float]) -> float:
    """Nash–Sutcliffe Efficiency."""
    o, s = _align(obs, sim)
    if len(o) < 2:
        return float("nan")
    mean_o = sum(o) / len(o)
    num = sum((o[i] - s[i]) ** 2 for i in range(len(o)))
    den = sum((o[i] - mean_o) ** 2 for i in range(len(o)))
    if den < 1e-15:
        return float("nan")
    return 1.0 - num / den


def r2_coeff(obs: Sequence[float], sim: Sequence[float]) -> float:
    """Coefficient of determination (Pearson r squared)."""
    o, s = _align(obs, sim)
    n = len(o)
    if n < 2:
        return float("nan")
    mo, ms = sum(o) / n, sum(s) / n
    cov = sum((o[i] - mo) * (s[i] - ms) for i in range(n))
    vo = sum((o[i] - mo) ** 2 for i in range(n))
    vs = sum((s[i] - ms) ** 2 for i in range(n))
    if vo < 1e-15 or vs < 1e-15:
        return float("nan")
    r = cov / math.sqrt(vo * vs)
    return r * r


def kge(obs: Sequence[float], sim: Sequence[float]) -> float:
    """
    Kling–Gupta Efficiency (2009).
    KGE = 1 − sqrt( (r−1)² + (α−1)² + (β−1)² )
    α = σ_s/σ_o, β = μ_s/μ_o
    """
    o, s = _align(obs, sim)
    n = len(o)
    if n < 2:
        return float("nan")
    mo, ms = sum(o) / n, sum(s) / n
    so = math.sqrt(sum((x - mo) ** 2 for x in o) / n)
    ss = math.sqrt(sum((x - ms) ** 2 for x in s) / n)
    if so < 1e-15 or abs(mo) < 1e-15:
        return float("nan")
    cov = sum((o[i] - mo) * (s[i] - ms) for i in range(n)) / n
    r = cov / (so * ss) if ss > 1e-15 else 0.0
    alpha = ss / so
    beta = ms / mo
    return 1.0 - math.sqrt((r - 1.0) ** 2 + (alpha - 1.0) ** 2 + (beta - 1.0) ** 2)


def nse_class(value: float) -> str:
    if value != value:  # NaN
        return "undefined"
    if value > 0.75:
        return "very_good"
    if value >= 0.65:
        return "good"
    if value >= 0.50:
        return "satisfactory"
    if value >= 0.0:
        return "unsatisfactory"
    return "poor"


def evaluate_series(
    observed: Sequence[float],
    simulated: Sequence[float],
    variable: str = "value",
) -> dict[str, Any]:
    """Full metric pack for one observed vs simulated series."""
    o, s = _align(observed, simulated)
    nse_v = nse(o, s)
    return {
        "variable": variable,
        "n": len(o),
        "rmse": _round(rmse(o, s)),
        "mae": _round(mae(o, s)),
        "bias": _round(bias(o, s)),
        "pbias_pct": _round(pbias(o, s)),
        "nse": _round(nse_v),
        "nse_class": nse_class(nse_v),
        "r2": _round(r2_coeff(o, s)),
        "kge": _round(kge(o, s)),
        "observed_mean": _round(sum(o) / len(o)) if o else None,
        "simulated_mean": _round(sum(s) / len(s)) if s else None,
        "interpretation_fa": _nse_fa(nse_v),
        "interpretation_en": _nse_en(nse_v),
    }


def _round(x: float, nd: int = 5) -> float | None:
    if x != x or math.isinf(x):
        return None
    return round(x, nd)


def _nse_fa(v: float) -> str:
    if v != v:
        return "NSE قابل محاسبه نیست (واریانس مشاهده صفر یا داده ناکافی)."
    if v > 0.75:
        return "NSE خیلی خوب (>۰.۷۵): مدل بخش عمدهٔ واریانس را توضیح می‌دهد."
    if v >= 0.65:
        return "NSE خوب (۰.۶۵–۰.۷۵)."
    if v >= 0.50:
        return "NSE قابل قبول (۰.۵۰–۰.۶۵)؛ برای غربالگری مناسب است."
    if v >= 0.0:
        return "NSE ضعیف (<۰.۵۰): مدل بهتر از میانگین نیست یا کمی بهتر است."
    return "NSE منفی: مدل بدتر از میانگین سادهٔ مشاهدات است."


def _nse_en(v: float) -> str:
    if v != v:
        return "NSE undefined (zero obs variance or insufficient data)."
    if v > 0.75:
        return "Very good NSE (>0.75)."
    if v >= 0.65:
        return "Good NSE (0.65–0.75)."
    if v >= 0.50:
        return "Satisfactory NSE (0.50–0.65)."
    if v >= 0.0:
        return "Unsatisfactory NSE (<0.50)."
    return "Negative NSE: worse than observed mean."


def metrics_catalog() -> dict[str, Any]:
    return {
        "metrics": [
            {
                "id": "nse",
                "name": "Nash–Sutcliffe Efficiency",
                "formula": "1 − Σ(O−S)² / Σ(O−Ō)²",
                "range": "(−∞, 1]",
                "optimal": 1.0,
                "notes_fa": "حساس به قله‌ها؛ برای سری‌های هموار SOC/N محتاطانه تفسیر شود.",
            },
            {
                "id": "kge",
                "name": "Kling–Gupta Efficiency",
                "formula": "1 − sqrt((r−1)²+(α−1)²+(β−1)²)",
                "range": "(−∞, 1]",
                "optimal": 1.0,
                "notes_fa": "همبستگی، نوسان و بایاس را جداگانه جریمه می‌کند.",
            },
            {
                "id": "rmse",
                "name": "Root Mean Square Error",
                "formula": "sqrt(mean((O−S)²))",
                "optimal": 0.0,
                "notes_fa": "واحد همان متغیر (مثلاً t N/ha).",
            },
            {
                "id": "pbias",
                "name": "Percent Bias",
                "formula": "100·Σ(S−O)/Σ(O)",
                "optimal": 0.0,
                "notes_fa": "مثبت = بیش‌برآورد مدل.",
            },
            {
                "id": "r2",
                "name": "Coefficient of determination",
                "formula": "(corr(O,S))²",
                "range": "[0, 1]",
                "notes_fa": "شکل روند را می‌سنجد نه بایاس مطلق را.",
            },
        ],
        "nse_thresholds_moriasi2007": {
            "very_good": ">0.75",
            "good": "0.65–0.75",
            "satisfactory": "0.50–0.65",
            "unsatisfactory": "<0.50",
        },
    }
