"""
Global sensitivity methods (pure Python, no SALib/numpy required).

1. Standardized Regression Coefficients (SRC) — global linear slopes
2. Morris elementary effects (μ*, σ)
3. Saltelli–Sobol first-order (S1) and total-order (ST) indices

References:
- Saltelli et al. (2008) Global Sensitivity Analysis. The Primer.
- Morris (1991) Factorial sampling plans for preliminary computational experiments.
- Sobol (2001) Global sensitivity indices for nonlinear mathematical models.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable
from typing import Any

from apps.ml.features import FEATURE_NAMES
from apps.ml.sensitivity import FEATURE_RANGES
from apps.ml.service import predict_bundle


# Default operational bounds (same as FEATURE_RANGES)
def _bounds() -> list[tuple[float, float]]:
    return [FEATURE_RANGES[n] for n in FEATURE_NAMES]


def _sample_uniform(rng: random.Random, lo: float, hi: float) -> float:
    return lo + (hi - lo) * rng.random()


def _dict_from_vec(vec: list[float]) -> dict[str, float]:
    return {n: float(v) for n, v in zip(FEATURE_NAMES, vec)}


def _yield_model(vec: list[float]) -> float:
    pred = predict_bundle(_dict_from_vec(vec))
    return float(pred["yield_relative_pred"])


def _risk_high_model(vec: list[float]) -> float:
    pred = predict_bundle(_dict_from_vec(vec))
    return float(pred["risk_proba"].get("high", 0.0))


def _mean(xs: list[float]) -> float:
    return sum(xs) / max(len(xs), 1)


def _var(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def _std(xs: list[float]) -> float:
    return math.sqrt(max(_var(xs), 0.0))


# ─── Standardized Regression Coefficients (global slopes) ───────────────────


def standardized_regression_coefficients(
    n_samples: int = 200,
    seed: int = 42,
    target: str = "yield",
) -> dict[str, Any]:
    """
    Monte-Carlo sample → multiple linear regression on standardized X,y.
    SRC_i ≈ partial slope of standardized output w.r.t. standardized X_i.
    |SRC| ranks global linear influence; R² shows linearity of response.
    """
    rng = random.Random(seed)
    bounds = _bounds()
    model: Callable[[list[float]], float] = _yield_model if target == "yield" else _risk_high_model

    X: list[list[float]] = []
    y: list[float] = []
    for _ in range(n_samples):
        row = [_sample_uniform(rng, lo, hi) for lo, hi in bounds]
        X.append(row)
        y.append(model(row))

    d = len(FEATURE_NAMES)
    # feature means / stds
    means = [_mean([X[i][j] for i in range(n_samples)]) for j in range(d)]
    stds = [_std([X[i][j] for i in range(n_samples)]) or 1.0 for j in range(d)]
    y_m = _mean(y)
    y_s = _std(y) or 1.0

    # standardized design
    Z = [[(X[i][j] - means[j]) / stds[j] for j in range(d)] for i in range(n_samples)]
    yz = [(yi - y_m) / y_s for yi in y]

    # normal equations Z^T Z β = Z^T y  (d x d) via Gauss-Jordan
    g = [[0.0] * (d + 1) for _ in range(d)]
    for i in range(n_samples):
        for a in range(d):
            for b in range(d):
                g[a][b] += Z[i][a] * Z[i][b]
            g[a][d] += Z[i][a] * yz[i]
    # ridge for stability
    for a in range(d):
        g[a][a] += 1e-6

    beta = _solve_linear(g, d)
    # R²
    y_hat = [sum(beta[j] * Z[i][j] for j in range(d)) for i in range(n_samples)]
    ss_res = sum((yz[i] - y_hat[i]) ** 2 for i in range(n_samples))
    ss_tot = sum(v ** 2 for v in yz) or 1.0
    r2 = 1.0 - ss_res / ss_tot

    rows = [
        {
            "feature": FEATURE_NAMES[j],
            "src": round(beta[j], 5),
            "abs_src": round(abs(beta[j]), 5),
        }
        for j in range(d)
    ]
    rows.sort(key=lambda r: r["abs_src"], reverse=True)

    return {
        "method": "standardized_regression_coefficients",
        "target": target,
        "n_samples": n_samples,
        "r_squared": round(r2, 4),
        "coefficients": rows,
        "notes_fa": "SRC = شیب جهانی خطی روی متغیرهای استاندارد؛ |SRC| رتبه اثر خطی. R² کم یعنی پاسخ غیرخطی (Sobol مفیدتر است).",
        "notes_en": "SRC global linear slopes on standardized vars; low R² ⇒ nonlinear response (prefer Sobol).",
    }


def _solve_linear(aug: list[list[float]], n: int) -> list[float]:
    """Gauss-Jordan on n x (n+1) augmented matrix."""
    a = [row[:] for row in aug]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        a[col], a[pivot] = a[pivot], a[col]
        div = a[col][col] or 1e-12
        for j in range(col, n + 1):
            a[col][j] /= div
        for r in range(n):
            if r == col:
                continue
            fac = a[r][col]
            for j in range(col, n + 1):
                a[r][j] -= fac * a[col][j]
    return [a[i][n] for i in range(n)]


# ─── Morris elementary effects ───────────────────────────────────────────────


def morris_elementary_effects(
    n_trajectories: int = 20,
    levels: int = 6,
    seed: int = 42,
    target: str = "yield",
) -> dict[str, Any]:
    """
    Morris screening: r trajectories on a p-level grid.
    μ* = mean |EE|, σ = std(EE). High μ* ⇒ influential; high σ ⇒ nonlinear/interactions.
    Cost ≈ r * (d + 1) evaluations.
    """
    rng = random.Random(seed)
    bounds = _bounds()
    d = len(FEATURE_NAMES)
    model: Callable[[list[float]], float] = _yield_model if target == "yield" else _risk_high_model
    p = max(levels, 4)
    delta = p / (2 * (p - 1))  # standard Morris step in [0,1] space

    ees: list[list[float]] = [[] for _ in range(d)]

    for _ in range(n_trajectories):
        # base point on grid in unit cube
        x_unit = [rng.randrange(p) / (p - 1) for _ in range(d)]
        order = list(range(d))
        rng.shuffle(order)
        x = [_unit_to_bound(x_unit[j], bounds[j]) for j in range(d)]
        y0 = model(x)

        for j in order:
            # step in unit space
            step_dir = 1.0 if x_unit[j] + delta <= 1.0 else -1.0
            x_unit[j] = min(1.0, max(0.0, x_unit[j] + step_dir * delta))
            x_new = x[:]
            x_new[j] = _unit_to_bound(x_unit[j], bounds[j])
            y1 = model(x_new)
            # scale EE by factor range
            span = bounds[j][1] - bounds[j][0]
            ee = (y1 - y0) / (step_dir * delta) if abs(delta) > 1e-12 else 0.0
            # dimensionless EE (Morris classic uses unit cube)
            ees[j].append(ee)
            x, y0 = x_new, y1

    rows = []
    for j, name in enumerate(FEATURE_NAMES):
        vals = ees[j]
        mu = _mean(vals)
        mu_star = _mean([abs(v) for v in vals])
        sigma = _std(vals)
        rows.append(
            {
                "feature": name,
                "mu": round(mu, 5),
                "mu_star": round(mu_star, 5),
                "sigma": round(sigma, 5),
                "n_ee": len(vals),
            }
        )
    rows.sort(key=lambda r: r["mu_star"], reverse=True)

    return {
        "method": "morris",
        "target": target,
        "n_trajectories": n_trajectories,
        "levels": p,
        "delta_unit": round(delta, 4),
        "effects": rows,
        "notes_fa": "μ* بالا = اثر قوی؛ σ بالا = غیرخطی یا برهم‌کنش. غربالگری ارزان قبل از Sobol.",
        "notes_en": "High μ* = strong effect; high σ = nonlinearity/interactions. Cheap screening before Sobol.",
    }


def _unit_to_bound(u: float, bound: tuple[float, float]) -> float:
    lo, hi = bound
    return lo + u * (hi - lo)


# ─── Saltelli–Sobol ──────────────────────────────────────────────────────────


def saltelli_sobol(
    n_base: int = 64,
    seed: int = 42,
    target: str = "yield",
    calc_second_order: bool = False,
) -> dict[str, Any]:
    """
    Variance-based Sobol indices via Saltelli sampling.

    Sample size: N * (2 + D) if first+total only (calc_second_order=False),
    or N * (2D + 2) with second-order (more expensive; not fully estimated here).

    Estimators (Jansen / Saltelli):
      ST_i = (1/(2N)) Σ (Y_A − Y_ABi)² / Var(Y)
      S1_i = Var(Y) − (1/(2N)) Σ (Y_B − Y_ABi)²  all over Var(Y)
            equivalently S1_i ≈ (1/N) Σ Y_B (Y_ABi − Y_A) / Var  (Saltelli 2008 form)

    We use:
      S1_i = mean(Y_A * (Y_ABi - Y_B)) / Var(Y)   (can be slightly negative numerically)
      ST_i = mean((Y_A - Y_ABi)²) / (2 * Var(Y))
    """
    rng = random.Random(seed)
    bounds = _bounds()
    d = len(FEATURE_NAMES)
    n = max(16, min(n_base, 256))  # cap for pure-Python cost
    model: Callable[[list[float]], float] = _yield_model if target == "yield" else _risk_high_model

    def sample_matrix() -> list[list[float]]:
        return [[_sample_uniform(rng, lo, hi) for lo, hi in bounds] for _ in range(n)]

    A = sample_matrix()
    B = sample_matrix()

    y_a = [model(row) for row in A]
    y_b = [model(row) for row in B]

    # AB_i: A with column i from B
    y_ab: list[list[float]] = []
    for i in range(d):
        matrix = []
        for r in range(n):
            row = A[r][:]
            row[i] = B[r][i]
            matrix.append(row)
        y_ab.append([model(row) for row in matrix])

    all_y = y_a + y_b
    for col in y_ab:
        all_y.extend(col)
    vy = _var(all_y)
    if vy < 1e-12:
        vy = 1e-12

    indices = []
    for i, name in enumerate(FEATURE_NAMES):
        # Saltelli first-order
        s1 = sum(y_a[r] * (y_ab[i][r] - y_b[r]) for r in range(n)) / (n * vy)
        # Jansen total-order
        st = sum((y_a[r] - y_ab[i][r]) ** 2 for r in range(n)) / (2 * n * vy)
        # clip numerical noise
        s1 = max(-0.05, min(1.2, s1))
        st = max(0.0, min(1.5, st))
        indices.append(
            {
                "feature": name,
                "S1": round(s1, 5),
                "ST": round(st, 5),
                "ST_minus_S1": round(max(0.0, st - max(0.0, s1)), 5),
            }
        )

    indices.sort(key=lambda r: r["ST"], reverse=True)
    n_model_runs = n * (2 + d)

    return {
        "method": "saltelli_sobol",
        "target": target,
        "n_base": n,
        "n_model_runs": n_model_runs,
        "output_variance": round(vy, 6),
        "indices": indices,
        "calc_second_order": calc_second_order,
        "notes_fa": (
            "S1 = اثر مرتبه اول (سهم واریانس مستقیم). "
            "ST = اثر کل شامل برهم‌کنش‌ها. "
            "ST−S1 بزرگ ⇒ تعامل با سایر ورودی‌ها. "
            "تخمین Monte-Carlo با N کوچک نویز دارد؛ برای دقت N≥512 و SALib توصیه می‌شود."
        ),
        "notes_en": (
            "S1 first-order variance share; ST total-order including interactions. "
            "Large ST−S1 ⇒ interactions. Small N is noisy; use N≥512 / SALib for production."
        ),
        "citation": "Saltelli et al. 2008; Sobol 2001; Jansen estimator for ST",
    }


def full_global_sensitivity(
    *,
    n_src: int = 180,
    n_morris: int = 16,
    n_sobol: int = 48,
    seed: int = 42,
    target: str = "yield",
) -> dict[str, Any]:
    """Combined global sensitivity report for API."""
    # ensure models trained
    from apps.ml.service import get_bundle

    get_bundle()

    src = standardized_regression_coefficients(n_samples=n_src, seed=seed, target=target)
    morris = morris_elementary_effects(n_trajectories=n_morris, seed=seed + 1, target=target)
    sobol = saltelli_sobol(n_base=n_sobol, seed=seed + 2, target=target)

    top_st = sobol["indices"][:3]
    summary_fa = (
        f"Sobol ST برتر: {", ".join(t['feature'] for t in top_st)}. "
        f"R²(SRC)={src['r_squared']:.2f}. "
        f"Morris μ* برتر: {morris['effects'][0]['feature']}."
    )
    summary_en = (
        f"Top Sobol ST: {", ".join(t['feature'] for t in top_st)}. "
        f"SRC R²={src['r_squared']:.2f}. "
        f"Top Morris μ*: {morris['effects'][0]['feature']}."
    )

    return {
        "engine": "econojin-global-sa-v1",
        "target": target,
        "src": src,
        "morris": morris,
        "sobol": sobol,
        "summary_fa": summary_fa,
        "summary_en": summary_en,
        "methods": ["SRC", "Morris", "Saltelli-Sobol"],
    }
