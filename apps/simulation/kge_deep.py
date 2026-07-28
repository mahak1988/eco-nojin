"""
Deep Kling–Gupta Efficiency family.

KGE (Gupta et al. 2009):
  KGE = 1 − sqrt( (r−1)² + (α−1)² + (β−1)² )
  r   = linear correlation
  α   = σ_s / σ_o   (variability ratio)
  β   = μ_s / μ_o   (bias ratio)

KGE' (Kling et al. 2012) — β uses CV ratio:
  β' = (μ_s/μ_o) / (σ_s/σ_o)  wait — standard KGE' uses:
  α = (σ_s/μ_s) / (σ_o/μ_o)   = CV_s / CV_o
  β = μ_s / μ_o
  KGE' = 1 − sqrt( (r−1)² + (α−1)² + (β−1)² )

KGEnsp (non-parametric / Spearman) optional via rank correlation.

Decomposition helps diagnose: correlation skill vs bias vs variability.
"""

from __future__ import annotations

import math
from typing import Any, Sequence


def _align(obs: Sequence[float], sim: Sequence[float]) -> tuple[list[float], list[float]]:
    n = min(len(obs), len(sim))
    return [float(obs[i]) for i in range(n)], [float(sim[i]) for i in range(n)]


def _stats(x: list[float]) -> tuple[float, float]:
    n = len(x)
    mu = sum(x) / n
    var = sum((v - mu) ** 2 for v in x) / n
    return mu, math.sqrt(var)


def _pearson(o: list[float], s: list[float]) -> float:
    n = len(o)
    mo, so = _stats(o)
    ms, ss = _stats(s)
    if so < 1e-15 or ss < 1e-15:
        return float("nan")
    cov = sum((o[i] - mo) * (s[i] - ms) for i in range(n)) / n
    return cov / (so * ss)


def _spearman(o: list[float], s: list[float]) -> float:
    def ranks(a: list[float]) -> list[float]:
        order = sorted(range(len(a)), key=lambda i: a[i])
        r = [0.0] * len(a)
        i = 0
        while i < len(a):
            j = i
            while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    return _pearson(ranks(o), ranks(s))


def kge_components(obs: Sequence[float], sim: Sequence[float]) -> dict[str, Any]:
    o, s = _align(obs, sim)
    n = len(o)
    if n < 2:
        return {"error": "need n>=2", "n": n}

    mo, so = _stats(o)
    ms, ss = _stats(s)
    r = _pearson(o, s)

    # Classic KGE (Gupta 2009)
    alpha = ss / so if so > 1e-15 else float("nan")
    beta = ms / mo if abs(mo) > 1e-15 else float("nan")
    if any(math.isnan(x) for x in (r, alpha, beta)):
        kge = float("nan")
        ed = float("nan")
    else:
        ed = math.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
        kge = 1.0 - ed

    # KGE' (Kling 2012): α on CV ratio
    cv_o = so / mo if abs(mo) > 1e-15 else float("nan")
    cv_s = ss / ms if abs(ms) > 1e-15 else float("nan")
    if cv_o == cv_o and cv_o > 1e-15 and cv_s == cv_s:
        alpha_p = cv_s / cv_o
    else:
        alpha_p = float("nan")
    beta_p = beta
    if any(math.isnan(x) for x in (r, alpha_p, beta_p)):
        kge_p = float("nan")
    else:
        kge_p = 1.0 - math.sqrt((r - 1) ** 2 + (alpha_p - 1) ** 2 + (beta_p - 1) ** 2)

    r_sp = _spearman(o, s)
    if any(math.isnan(x) for x in (r_sp, alpha, beta)):
        kge_np = float("nan")
    else:
        kge_np = 1.0 - math.sqrt((r_sp - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)

    # Contribution of each term to squared distance (diagnosis)
    if ed == ed and ed > 1e-15:
        term_r = (r - 1) ** 2
        term_a = (alpha - 1) ** 2
        term_b = (beta - 1) ** 2
        sum_t = term_r + term_a + term_b
        share = {
            "correlation": round(term_r / sum_t, 4),
            "variability": round(term_a / sum_t, 4),
            "bias": round(term_b / sum_t, 4),
        }
    else:
        share = {}

    def _r(x: float) -> float | None:
        if x != x or math.isinf(x):
            return None
        return round(x, 6)

    return {
        "n": n,
        "mu_obs": _r(mo),
        "mu_sim": _r(ms),
        "sigma_obs": _r(so),
        "sigma_sim": _r(ss),
        "r_pearson": _r(r),
        "r_spearman": _r(r_sp),
        "kge_gupta2009": {
            "value": _r(kge),
            "alpha_sigma_ratio": _r(alpha),
            "beta_mean_ratio": _r(beta),
            "euclidean_distance": _r(ed),
            "error_share": share,
            "formula": "1 - sqrt((r-1)^2 + (σs/σo-1)^2 + (μs/μo-1)^2)",
        },
        "kge_prime_kling2012": {
            "value": _r(kge_p),
            "alpha_cv_ratio": _r(alpha_p),
            "beta_mean_ratio": _r(beta_p),
            "formula": "1 - sqrt((r-1)^2 + (CVs/CVo-1)^2 + (μs/μo-1)^2)",
        },
        "kge_nonparametric": {
            "value": _r(kge_np),
            "r_spearman": _r(r_sp),
            "notes": "Spearman r instead of Pearson",
        },
        "interpretation_fa": _interp_fa(kge),
        "interpretation_en": _interp_en(kge),
        "benchmarks": {
            "perfect": 1.0,
            "mean_flow_benchmark_approx": "KGE≈-0.41 for sim=mean(obs) under common conditions",
            "good_rule_of_thumb": ">0.5 often acceptable for monthly; >0.7 strong",
        },
    }


def _interp_fa(v: float) -> str:
    if v != v:
        return "KGE تعریف‌نشده (واریانس یا میانگین مشاهده نزدیک صفر)."
    if v > 0.75:
        return "KGE عالی؛ همبستگی، نوسان و بایاس نزدیک ایده‌آل."
    if v > 0.5:
        return "KGE خوب تا قابل قبول؛ جزء غالب خطا را از error_share ببینید."
    if v > 0.0:
        return "KGE ضعیف؛ مدل هنوز از معیار تصادفی ساده بهتر است."
    return "KGE پایین/منفی؛ بایاس یا نوسان یا همبستگی مشکل جدی دارد."


def _interp_en(v: float) -> str:
    if v != v:
        return "KGE undefined."
    if v > 0.75:
        return "Excellent KGE."
    if v > 0.5:
        return "Good/acceptable KGE; inspect error_share."
    if v > 0.0:
        return "Weak KGE."
    return "Poor/negative KGE."
