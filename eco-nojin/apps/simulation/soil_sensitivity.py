"""
Global sensitivity for soil models: RothC (ΔSOC) and RUSLE (A).
Pure Python Saltelli/Morris/SRC — same estimators as apps/ml/global_sensitivity.
"""

from __future__ import annotations

import math
import random
from typing import Any, Callable

from apps.simulation.rothc_model import run_rothc
from apps.simulation.soil_models import run_rusle2

ROTHC_PARAMS = [
    ("clay_pct", 5.0, 45.0),
    ("temp_c", 5.0, 30.0),
    ("rain_mm_year", 200.0, 1200.0),
    ("et_mm_year", 400.0, 1400.0),
    ("c_input_t_ha_y", 0.2, 4.0),
    ("soc_t_ha", 15.0, 80.0),
]

RUSLE_PARAMS = [
    ("R", 50.0, 400.0),
    ("K", 0.1, 0.55),
    ("slope_length_m", 10.0, 120.0),
    ("slope_pct", 1.0, 25.0),
    ("C", 0.05, 0.5),
    ("P", 0.3, 1.0),
]


def _mean(xs: list[float]) -> float:
    return sum(xs) / max(len(xs), 1)


def _var(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def _std(xs: list[float]) -> float:
    return math.sqrt(max(_var(xs), 0.0))


def _sample(rng: random.Random, lo: float, hi: float) -> float:
    return lo + (hi - lo) * rng.random()


def _rothc_y(vec: list[float]) -> float:
    keys = [p[0] for p in ROTHC_PARAMS]
    d = {k: v for k, v in zip(keys, vec)}
    d["years"] = 15
    d["plant_cover"] = True
    return float(run_rothc(d)["delta"])


def _rusle_y(vec: list[float]) -> float:
    keys = [p[0] for p in RUSLE_PARAMS]
    d = {k: v for k, v in zip(keys, vec)}
    return float(run_rusle2(d)["outputs"]["A_t_ha_year"])


def _src(param_spec: list[tuple[str, float, float]], model: Callable[[list[float]], float], n: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    d = len(param_spec)
    X, y = [], []
    for _ in range(n):
        row = [_sample(rng, lo, hi) for _, lo, hi in param_spec]
        X.append(row)
        y.append(model(row))
    means = [_mean([X[i][j] for i in range(n)]) for j in range(d)]
    stds = [max(_std([X[i][j] for i in range(n)]), 1e-9) for j in range(d)]
    y_m, y_s = _mean(y), max(_std(y), 1e-9)
    Z = [[(X[i][j] - means[j]) / stds[j] for j in range(d)] for i in range(n)]
    yz = [(yi - y_m) / y_s for yi in y]
    g = [[0.0] * (d + 1) for _ in range(d)]
    for i in range(n):
        for a in range(d):
            for b in range(d):
                g[a][b] += Z[i][a] * Z[i][b]
            g[a][d] += Z[i][a] * yz[i]
    for a in range(d):
        g[a][a] += 1e-6
    beta = _gauss(g, d)
    y_hat = [sum(beta[j] * Z[i][j] for j in range(d)) for i in range(n)]
    ss_res = sum((yz[i] - y_hat[i]) ** 2 for i in range(n))
    ss_tot = sum(v ** 2 for v in yz) or 1.0
    rows = [
        {"feature": param_spec[j][0], "src": round(beta[j], 5), "abs_src": round(abs(beta[j]), 5)}
        for j in range(d)
    ]
    rows.sort(key=lambda r: r["abs_src"], reverse=True)
    return {"method": "SRC", "r_squared": round(1 - ss_res / ss_tot, 4), "coefficients": rows}


def _gauss(aug: list[list[float]], n: int) -> list[float]:
    a = [row[:] for row in aug]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(a[r][col]))
        a[col], a[piv] = a[piv], a[col]
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


def _morris(param_spec: list[tuple[str, float, float]], model: Callable[[list[float]], float], r: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    d = len(param_spec)
    p_levels = 6
    delta = p_levels / (2 * (p_levels - 1))
    ees: list[list[float]] = [[] for _ in range(d)]
    for _ in range(r):
        u = [rng.randrange(p_levels) / (p_levels - 1) for _ in range(d)]
        order = list(range(d))
        rng.shuffle(order)
        x = [lo + u[j] * (hi - lo) for j, (_, lo, hi) in enumerate(param_spec)]
        y0 = model(x)
        for j in order:
            step = 1.0 if u[j] + delta <= 1.0 else -1.0
            u[j] = min(1.0, max(0.0, u[j] + step * delta))
            lo, hi = param_spec[j][1], param_spec[j][2]
            x_new = x[:]
            x_new[j] = lo + u[j] * (hi - lo)
            y1 = model(x_new)
            ees[j].append((y1 - y0) / (step * delta))
            x, y0 = x_new, y1
    rows = []
    for j, (name, _, _) in enumerate(param_spec):
        vals = ees[j]
        rows.append(
            {
                "feature": name,
                "mu_star": round(_mean([abs(v) for v in vals]), 5),
                "sigma": round(_std(vals), 5),
                "mu": round(_mean(vals), 5),
            }
        )
    rows.sort(key=lambda r: r["mu_star"], reverse=True)
    return {"method": "Morris", "effects": rows}


def _sobol(param_spec: list[tuple[str, float, float]], model: Callable[[list[float]], float], n: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    d = len(param_spec)
    n = max(16, min(n, 96))

    def mat() -> list[list[float]]:
        return [[_sample(rng, lo, hi) for _, lo, hi in param_spec] for _ in range(n)]

    A, B = mat(), mat()
    y_a = [model(row) for row in A]
    y_b = [model(row) for row in B]
    y_ab = []
    for i in range(d):
        M = []
        for r in range(n):
            row = A[r][:]
            row[i] = B[r][i]
            M.append(row)
        y_ab.append([model(row) for row in M])
    all_y = y_a + y_b
    for col in y_ab:
        all_y.extend(col)
    vy = max(_var(all_y), 1e-12)
    indices = []
    for i, (name, _, _) in enumerate(param_spec):
        s1 = sum(y_a[r] * (y_ab[i][r] - y_b[r]) for r in range(n)) / (n * vy)
        st = sum((y_a[r] - y_ab[i][r]) ** 2 for r in range(n)) / (2 * n * vy)
        indices.append(
            {
                "feature": name,
                "S1": round(max(-0.05, min(1.2, s1)), 5),
                "ST": round(max(0.0, min(1.5, st)), 5),
                "ST_minus_S1": round(max(0.0, st - max(0.0, s1)), 5),
            }
        )
    indices.sort(key=lambda r: r["ST"], reverse=True)
    return {
        "method": "Saltelli-Sobol",
        "n_base": n,
        "n_model_runs": n * (2 + d),
        "output_variance": round(vy, 6),
        "indices": indices,
    }


def global_sa_rothc(n_src: int = 100, n_morris: int = 10, n_sobol: int = 32, seed: int = 42) -> dict[str, Any]:
    return {
        "model": "rothc_26_3",
        "target": "delta_soc_t_ha",
        "src": _src(ROTHC_PARAMS, _rothc_y, n_src, seed),
        "morris": _morris(ROTHC_PARAMS, _rothc_y, n_morris, seed + 1),
        "sobol": _sobol(ROTHC_PARAMS, _rothc_y, n_sobol, seed + 2),
        "notes_fa": "خروجی هدف: تغییر SOC در ۱۵ سال. S1/ST روی clay، ورودی کربن، دما و رطوبت.",
        "notes_en": "Target: 15-year ΔSOC. Expect C input and climate modifiers to dominate ST.",
    }


def global_sa_rusle(n_src: int = 100, n_morris: int = 10, n_sobol: int = 32, seed: int = 42) -> dict[str, Any]:
    return {
        "model": "rusle2_proxy",
        "target": "A_t_ha_year",
        "src": _src(RUSLE_PARAMS, _rusle_y, n_src, seed),
        "morris": _morris(RUSLE_PARAMS, _rusle_y, n_morris, seed + 1),
        "sobol": _sobol(RUSLE_PARAMS, _rusle_y, n_sobol, seed + 2),
        "notes_fa": "خروجی هدف: فرسایش سالانه A. معمولاً R، LS (شیب) و C پوشش حساس‌ترین‌اند.",
        "notes_en": "Target: annual soil loss A. R, slope LS, and cover C often dominate.",
    }
