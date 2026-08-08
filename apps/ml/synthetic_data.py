"""Generate labeled synthetic samples aligned with process-model physics."""

from __future__ import annotations

import random
from typing import Any

from apps.ml.features import FEATURE_NAMES, vector_from_dict


def _yield_true(f: dict[str, float]) -> float:
    # physics-inspired: yield drops with stress, heat, low NDVI, low moisture
    water = f["rain_mm_day"] + f["soil_moisture"] / 100.0
    stress = max(0.0, f["et0_mm_day"] - water * 2.0)
    y = (
        0.35
        + 0.4 * f["mean_ndvi"]
        + 0.25 * f["mean_canopy"]
        - 0.04 * stress
        - 0.008 * max(0.0, f["air_temp_c"] - 32)
        - 0.0004 * f["irrigation_need_mm"]
        + 0.02 * max(-1.0, min(1.0, f["soc_delta"]))
    )
    return max(0.05, min(0.98, y))


def _risk_label(y: float, f: dict[str, float]) -> str:
    if y < 0.5 or f["soil_moisture"] < 18 or f["air_temp_c"] > 40:
        return "high"
    if y < 0.7 or f["mean_ndvi"] < 0.3:
        return "medium"
    return "low"


def generate_dataset(
    n: int = 800, seed: int = 42
) -> tuple[list[list[float]], list[float], list[str]]:
    rng = random.Random(seed)
    X: list[list[float]] = []
    y_reg: list[float] = []
    y_cls: list[str] = []
    for _ in range(n):
        f = {
            "et0_mm_day": rng.uniform(2.0, 8.0),
            "rain_mm_day": rng.uniform(0.0, 3.5),
            "mean_ndvi": rng.uniform(0.1, 0.85),
            "mean_canopy": rng.uniform(0.1, 0.9),
            "soil_moisture": rng.uniform(10.0, 55.0),
            "air_temp_c": rng.uniform(15.0, 45.0),
            "irrigation_need_mm": rng.uniform(20.0, 450.0),
            "yield_relative_proxy": rng.uniform(0.2, 0.95),
            "runoff_mm_year": rng.uniform(0.0, 200.0),
            "soc_delta": rng.uniform(-3.0, 2.0),
        }
        yt = _yield_true(f)
        # noise
        yt = max(0.02, min(0.99, yt + rng.gauss(0, 0.04)))
        f["yield_relative_proxy"] = yt
        X.append(vector_from_dict(f))
        y_reg.append(yt)
        y_cls.append(_risk_label(yt, f))
    return X, y_reg, y_cls


def sample_metrics() -> dict[str, Any]:
    """Quick sanity stats on feature coverage."""
    X, y, c = generate_dataset(200)
    from collections import Counter

    return {
        "n": len(X),
        "feature_dim": len(FEATURE_NAMES),
        "features": FEATURE_NAMES,
        "yield_mean": sum(y) / len(y),
        "risk_counts": dict(Counter(c)),
    }
