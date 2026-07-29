"""
Calibration of soil carbon process models against observed SOC series.

Methods:
  - grid / random search on free parameters
  - objective: RMSE or NSE on annual SOC (t C/ha)

Fits models: rothc, icbm, century3, yasso07_lite.
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timezone
from typing import Any, Callable

from apps.simulation.rothc_model import run_rothc
from apps.simulation.soil_carbon import run_century3, run_icbm, run_yasso_lite

MODEL_RUNNERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "rothc": run_rothc,
    "icbm": run_icbm,
    "century3": run_century3,
    "yasso07_lite": run_yasso_lite,
}

# Parameter search space (relative / absolute bounds)
SEARCH_SPACE: dict[str, dict[str, tuple[float, float]]] = {
    "rothc": {
        "c_input_t_ha_y": (0.2, 8.0),
        "clay_pct": (5.0, 60.0),
        "dpm_rpm_ratio": (0.5, 2.5),
    },
    "icbm": {
        "c_input_t_ha_y": (0.2, 8.0),
        "k_young": (0.3, 1.5),
        "k_old": (0.002, 0.02),
        "humification": (0.08, 0.35),
        "r_e": (0.3, 2.5),
    },
    "century3": {
        "c_input_t_ha_y": (0.2, 8.0),
        "clay_pct": (5.0, 60.0),
        "metabolic_frac": (0.3, 0.75),
    },
    "yasso07_lite": {
        "c_input_t_ha_y": (0.2, 8.0),
        "temp_c": (5.0, 25.0),
        "rain_mm_year": (100.0, 1500.0),
    },
}


def _rmse(obs: list[float], sim: list[float]) -> float:
    n = min(len(obs), len(sim))
    if n == 0:
        return float("inf")
    return math.sqrt(sum((obs[i] - sim[i]) ** 2 for i in range(n)) / n)


def _nse(obs: list[float], sim: list[float]) -> float:
    n = min(len(obs), len(sim))
    if n < 2:
        return float("-inf")
    mean_o = sum(obs[:n]) / n
    num = sum((obs[i] - sim[i]) ** 2 for i in range(n))
    den = sum((obs[i] - mean_o) ** 2 for i in range(n))
    if den <= 1e-12:
        return float("-inf")
    return 1.0 - num / den


def _extract_soc_series(result: dict[str, Any], years: int) -> list[float]:
    series = result.get("series") or []
    vals = [float(row.get("soc_t_ha", 0)) for row in series]
    # align length years+1
    if len(vals) >= years + 1:
        return vals[: years + 1]
    while len(vals) < years + 1:
        vals.append(vals[-1] if vals else 0.0)
    return vals


def calibrate_soil_carbon(
    model: str,
    observed_soc: list[float],
    base_params: dict[str, Any] | None = None,
    free_params: list[str] | None = None,
    n_samples: int = 80,
    method: str = "random",
    metric: str = "rmse",
    seed: int = 42,
) -> dict[str, Any]:
    """
    Calibrate `model` so simulated annual SOC matches `observed_soc`.

    observed_soc[0] = initial SOC at year 0; length = years+1 preferred.
    """
    model = model.lower().strip()
    if model not in MODEL_RUNNERS:
        raise ValueError(f"Unknown model '{model}'. Choose: {list(MODEL_RUNNERS)}")

    obs = [float(x) for x in observed_soc]
    if len(obs) < 2:
        raise ValueError("Need at least 2 observed SOC points (year 0 and later).")

    years = len(obs) - 1
    base = dict(base_params or {})
    base["years"] = years
    base.setdefault("soc_t_ha", obs[0])

    space = SEARCH_SPACE.get(model, {"c_input_t_ha_y": (0.2, 8.0)})
    keys = free_params or list(space.keys())
    keys = [k for k in keys if k in space]
    if not keys:
        keys = list(space.keys())

    rng = random.Random(seed)
    runner = MODEL_RUNNERS[model]

    best: dict[str, Any] | None = None
    trials: list[dict[str, Any]] = []

    def score_params(trial_p: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        res = runner(trial_p)
        sim = _extract_soc_series(res, years)
        rmse = _rmse(obs, sim)
        nse = _nse(obs, sim)
        obj = rmse if metric == "rmse" else -nse  # minimize
        return obj, {"rmse": rmse, "nse": nse, "sim": sim, "result": res}

    # Latin-ish random search
    for i in range(max(10, n_samples)):
        trial = dict(base)
        for k in keys:
            lo, hi = space[k]
            if method == "grid" and i < 5:
                # coarse grid on first dims
                t = i / 4.0
                trial[k] = lo + t * (hi - lo)
            else:
                trial[k] = lo + rng.random() * (hi - lo)
        try:
            obj, meta = score_params(trial)
        except Exception as e:
            trials.append({"error": str(e)[:80]})
            continue
        entry = {
            "params": {k: round(float(trial[k]), 5) for k in keys},
            "rmse": round(meta["rmse"], 4),
            "nse": round(meta["nse"], 4),
        }
        trials.append(entry)
        if best is None or obj < best["obj"]:
            best = {
                "obj": obj,
                "params": dict(trial),
                "free": entry["params"],
                "rmse": meta["rmse"],
                "nse": meta["nse"],
                "sim_soc": [round(v, 3) for v in meta["sim"]],
                "full": meta["result"],
            }

    # local refine around best (small jitter)
    if best:
        for _ in range(min(40, n_samples // 2)):
            trial = dict(best["params"])
            for k in keys:
                lo, hi = space[k]
                span = (hi - lo) * 0.08
                trial[k] = max(lo, min(hi, float(trial[k]) + rng.uniform(-span, span)))
            try:
                obj, meta = score_params(trial)
            except Exception:
                continue
            if obj < best["obj"]:
                best = {
                    "obj": obj,
                    "params": dict(trial),
                    "free": {k: round(float(trial[k]), 5) for k in keys},
                    "rmse": meta["rmse"],
                    "nse": meta["nse"],
                    "sim_soc": [round(v, 3) for v in meta["sim"]],
                    "full": meta["result"],
                }

    trials_sorted = sorted(
        [t for t in trials if "rmse" in t],
        key=lambda x: x["rmse"],
    )[:15]

    return {
        "model": model,
        "metric": metric,
        "n_observations": len(obs),
        "years": years,
        "observed_soc": obs,
        "best": {
            "free_params": best["free"] if best else {},
            "rmse": round(best["rmse"], 4) if best else None,
            "nse": round(best["nse"], 4) if best else None,
            "simulated_soc": best["sim_soc"] if best else [],
            "all_params": {
                k: best["params"].get(k)
                for k in (
                    "years",
                    "soc_t_ha",
                    "c_input_t_ha_y",
                    "temp_c",
                    "rain_mm_year",
                    "et_mm_year",
                    "clay_pct",
                )
                if best and k in best["params"]
            }
            if best
            else {},
        },
        "top_trials": trials_sorted,
        "search_space": {k: list(space[k]) for k in keys},
        "notes_fa": (
            "کالیبراسیون با جستجوی تصادفی/محلی روی پارامترهای آزاد؛ "
            "برای MRV رسمی از روش‌های بیزی و دادهٔ بیشتر استفاده کنید."
        ),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
