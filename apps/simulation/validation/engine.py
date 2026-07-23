"""
Validation & Uncertainty Engine.
- Goodness-of-fit: RMSE, NSE (Nash-Sutcliffe), R²  (ASCE guidelines)
- Uncertainty: Monte Carlo 95% confidence interval
- Sensitivity: Morris elementary effects
"""
import math
import random
from typing import Any, Callable, Awaitable


# کلیدهای محتمل برای عملکرد/خروجی اصلی هر شبیه‌ساز
_METRIC_CANDIDATES = ["yield_t_ha", "yield", "grain_yield", "biomass_t_ha",
                      "total_biomass", "streamflow", "runoff_mm", "soc_t_ha",
                      "soil_loss_t_ha", "npv", "unmet_demand", "generation_kwh"]


def _find_metric(result: dict, preferred: str = "yield_t_ha") -> float:
    """Find the primary metric value, trying preferred key then common candidates."""
    metrics = result.get("metrics", {}) if isinstance(result, dict) else {}
    outputs = result.get("outputs", {}) if isinstance(result, dict) else {}
    # ۱. کلید ترجیحی
    for src in (metrics, outputs):
        if isinstance(src, dict) and preferred in src:
            v = src[preferred]
            if isinstance(v, (int, float)):
                return float(v)
    # ۲. جستجوی کلیدهای محتمل
    for key in _METRIC_CANDIDATES:
        for src in (metrics, outputs):
            if isinstance(src, dict) and key in src:
                v = src[key]
                if isinstance(v, (int, float)):
                    return float(v)
    # ۳. اولین مقدار عددی در metrics
    if isinstance(metrics, dict):
        for v in metrics.values():
            if isinstance(v, (int, float)):
                return float(v)
    return 0.0


# ── Goodness-of-fit metrics ──
def rmse(observed: list[float], simulated: list[float]) -> float:
    if not observed:
        return 0.0
    n = min(len(observed), len(simulated))
    return math.sqrt(sum((observed[i] - simulated[i]) ** 2 for i in range(n)) / n)


def nse(observed: list[float], simulated: list[float]) -> float:
    """Nash-Sutcliffe Efficiency: 1=perfect, 0=mean baseline, <0=worse than mean."""
    if len(observed) < 2:
        return 0.0
    n = min(len(observed), len(simulated))
    mean_obs = sum(observed[:n]) / n
    num = sum((observed[i] - simulated[i]) ** 2 for i in range(n))
    den = sum((observed[i] - mean_obs) ** 2 for i in range(n))
    return round(1 - num / den, 4) if den else 0.0


def r_squared(observed: list[float], simulated: list[float]) -> float:
    if len(observed) < 2:
        return 0.0
    n = min(len(observed), len(simulated))
    mo = sum(observed[:n]) / n
    ms = sum(simulated[:n]) / n
    num = sum((observed[i] - mo) * (simulated[i] - ms) for i in range(n))
    do = math.sqrt(sum((observed[i] - mo) ** 2 for i in range(n)))
    ds = math.sqrt(sum((simulated[i] - ms) ** 2 for i in range(n)))
    return round((num / (do * ds)) ** 2, 4) if do and ds else 0.0


def goodness_of_fit(observed: list[float], simulated: list[float]) -> dict:
    return {
        "rmse": round(rmse(observed, simulated), 3),
        "nse": nse(observed, simulated),
        "r2": r_squared(observed, simulated),
        "n": min(len(observed), len(simulated)),
        "rating": _rate_nse(nse(observed, simulated)),
    }


def _rate_nse(v: float) -> str:
    if v >= 0.75:
        return "خیلی خوب (Very Good)"
    if v >= 0.65:
        return "خوب (Good)"
    if v >= 0.50:
        return "قابل قبول (Satisfactory)"
    return "ضعیف (Poor) — نیاز به کالیبراسیون"


# ── Monte Carlo uncertainty ──
async def monte_carlo(
    run_fn: Callable[[dict], Awaitable[dict]],
    base_params: dict,
    metric_key: str = "yield_t_ha",
    n: int = 150,
    uncertainty: float = 0.15,
) -> dict:
    """Run simulator n times with Gaussian-perturbed numeric params; return 95% CI."""
    results = []
    for _ in range(n):
        perturbed = {}
        for k, v in base_params.items():
            if isinstance(v, (int, float)) and v != 0 and not isinstance(v, bool):
                perturbed[k] = v * (1 + random.gauss(0, uncertainty))
            else:
                perturbed[k] = v
        try:
            r = await run_fn(perturbed)
            val = _find_metric(r, metric_key)
            results.append(val)  # _find_metric always returns float
        except Exception:
            pass
    if len(results) < 5:
        return {"error": "دادهٔ کافی برای تحلیل عدم قطعیت تولید نشد", "n": len(results)}
    results.sort()
    lo = results[int(0.025 * len(results))]
    hi = results[min(int(0.975 * len(results)), len(results) - 1)]
    mean = sum(results) / len(results)
    std = math.sqrt(sum((x - mean) ** 2 for x in results) / len(results))
    return {
        "mean": round(mean, 3), "std": round(std, 3),
        "ci_95_low": round(lo, 3), "ci_95_high": round(hi, 3),
        "cv_pct": round(std / mean * 100, 1) if mean else 0,
        "n": len(results),
    }


# ── Morris sensitivity (elementary effects) ──
async def morris_sensitivity(
    run_fn: Callable[[dict], Awaitable[dict]],
    base_params: dict,
    metric_key: str = "yield_t_ha",
    n: int = 30,
    delta: float = 0.10,
) -> dict:
    """Morris elementary effects: mean absolute change per parameter (higher = more influential)."""
    async def get_metric(p):
        try:
            r = await run_fn(p)
            return _find_metric(r, metric_key)
        except Exception:
            return 0.0

    base_y = await get_metric(base_params)
    effects = {}
    for k, v in base_params.items():
        if not isinstance(v, (int, float)) or v == 0 or isinstance(v, bool):
            continue
        ees = []
        for _ in range(n):
            perturbed = dict(base_params)
            perturbed[k] = v * (1 + delta)
            y = await get_metric(perturbed)
            ees.append(abs(y - base_y) / abs(base_y) if base_y else 0)
        if ees:
            effects[k] = round(sum(ees) / len(ees), 4)
    ranked = dict(sorted(effects.items(), key=lambda x: -x[1]))
    return {"base_value": round(base_y, 3), "effects": ranked,
            "most_influential": next(iter(ranked), None)}
