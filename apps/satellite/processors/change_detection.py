"""NDVI change detection rules."""

from __future__ import annotations

from collections.abc import Sequence


def delta_status(mean_a: float, mean_b: float, improve: float = 0.1, degrade: float = -0.1) -> str:
    delta = mean_b - mean_a
    if delta > improve:
        return "improved"
    if delta < degrade:
        return "degraded"
    return "stable"


def mean_safe(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))
