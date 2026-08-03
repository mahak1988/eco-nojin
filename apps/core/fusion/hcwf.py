"""HCWF — Hybrid Confidence-Weighted Fusion (ENOS-ISA novel layer).

Does not modify FAO/USDA model formulas; fuses multi-source observations.
License: CC BY-SA 4.0
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List, Tuple

import numpy as np


class DataSource(str, Enum):
    MANUAL = "manual"
    SATELLITE = "satellite"
    SENSOR = "sensor"
    WEATHER = "weather"
    MODEL = "model"


@dataclass
class DataPoint:
    value: float
    source: DataSource
    timestamp: datetime
    confidence: float
    spatial_resolution_m: float
    unit: str


@dataclass
class FusedResult:
    value: float
    confidence: float
    sources_used: List[str]
    uncertainty_range: Tuple[float, float]
    quality_tier: int


class HCWFFusion:
    BASE_CONFIDENCE = {
        DataSource.SENSOR: 0.95,
        DataSource.SATELLITE: 0.85,
        DataSource.MANUAL: 0.70,
        DataSource.WEATHER: 0.80,
        DataSource.MODEL: 0.60,
    }
    TEMPORAL_DECAY_RATE = {
        DataSource.SENSOR: 0.01,
        DataSource.SATELLITE: 0.05,
        DataSource.MANUAL: 0.03,
        DataSource.WEATHER: 0.02,
        DataSource.MODEL: 0.10,
    }

    def __init__(self, farm_location: Tuple[float, float] = (32.65, 51.67)):
        self.farm_location = farm_location
        self.historical_accuracy: dict = {}

    def fuse(self, data_points: List[DataPoint], target_parameter: str = "soil_moisture") -> FusedResult:
        if not data_points:
            raise ValueError("No data points provided")
        eff = [self._effective_confidence(dp) for dp in data_points]
        total = sum(eff)
        if total <= 0:
            raise ValueError("All data points have zero confidence")
        weights = [c / total for c in eff]
        fused = float(sum(w * dp.value for w, dp in zip(weights, data_points)))
        conf = self._combined_confidence(eff)
        unc = self._monte_carlo(data_points, weights)
        tier = self._quality_tier(conf)
        return FusedResult(
            value=fused,
            confidence=conf,
            sources_used=[dp.source.value for dp in data_points],
            uncertainty_range=unc,
            quality_tier=tier,
        )

    def _effective_confidence(self, dp: DataPoint) -> float:
        base = self.BASE_CONFIDENCE.get(dp.source, 0.5)
        ts = dp.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        age_h = max(0.0, (datetime.now(timezone.utc) - ts).total_seconds() / 3600.0)
        decay = float(np.exp(-self.TEMPORAL_DECAY_RATE.get(dp.source, 0.05) * age_h))
        spatial = min(1.0, max(0.05, 100.0 / max(1.0, dp.spatial_resolution_m)))
        hist = float(self.historical_accuracy.get(dp.source, 1.0))
        return float(max(0.0, min(1.0, base * decay * spatial * hist * max(0.0, min(1.0, dp.confidence)))))

    def _combined_confidence(self, confidences: List[float]) -> float:
        if not confidences:
            return 0.0
        prod = float(np.prod([1.0 - c for c in confidences]))
        combined = 1.0 - prod
        bonus = min(0.1, 0.02 * len(confidences))
        return float(min(0.99, combined + bonus))

    def _monte_carlo(
        self, data_points: List[DataPoint], weights: List[float], n: int = 500
    ) -> Tuple[float, float]:
        sims = []
        rng = np.random.default_rng(42)
        for _ in range(n):
            v = 0.0
            for w, dp in zip(weights, data_points):
                noise = (1.0 - max(0.0, min(1.0, dp.confidence))) * abs(dp.value) * 0.2
                v += w * float(rng.normal(dp.value, max(1e-9, noise)))
            sims.append(v)
        return (float(np.percentile(sims, 5)), float(np.percentile(sims, 95)))

    def _quality_tier(self, confidence: float) -> int:
        if confidence >= 0.92:
            return 4
        if confidence >= 0.85:
            return 3
        if confidence >= 0.75:
            return 2
        return 1

    def update_historical_accuracy(self, source: DataSource, accuracy: float) -> None:
        self.historical_accuracy[source] = float(max(0.0, min(1.5, accuracy)))
