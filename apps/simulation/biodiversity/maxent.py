"""MaxEnt-style habitat suitability — pure-Python proxy (not official MaxEnt software)."""

from __future__ import annotations

import logging
import math
import random
import time
from typing import Any

from apps.simulation.base import (
    BaseSimulator,
    SimulationParameter,
    SimulationResult,
    SimulationRegistry,
    SimulationStatus,
)

logger = logging.getLogger(__name__)


@SimulationRegistry.register
class MaxEntSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "maxent"

    @property
    def name(self) -> str:
        return "MaxEnt habitat suitability (proxy)"

    @property
    def category(self) -> str:
        return "biodiversity"

    @property
    def description(self) -> str:
        return (
            "Presence-inspired suitability surface (pure Python). "
            "Not a replacement for official Maxent software."
        )

    @property
    def version(self) -> str:
        return "1.1.0-proxy"

    def get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(
                name="n_occurrences",
                label="Occurrence samples",
                type="int",
                default=80,
                min_value=10,
                max_value=500,
                required=True,
            ),
            SimulationParameter(
                name="study_area_size",
                label="Study area",
                type="float",
                default=5000.0,
                min_value=100.0,
                max_value=100000.0,
                unit="km2",
                required=True,
            ),
            SimulationParameter(
                name="regularization_multiplier",
                label="Regularization",
                type="float",
                default=1.0,
                min_value=0.1,
                max_value=5.0,
                required=True,
            ),
            SimulationParameter(
                name="seed",
                label="Random seed",
                type="int",
                default=42,
                min_value=0,
                max_value=99999,
                required=False,
            ),
        ]

    async def run(self, parameters: dict[str, Any]) -> SimulationResult:
        start = time.time()
        errors = self.validate(parameters)
        if errors:
            return SimulationResult(
                simulator_id=self.id,
                simulator_name=self.name,
                status=SimulationStatus.FAILED,
                parameters=parameters,
                error="; ".join(errors),
            )
        try:
            outputs = self._run(parameters)
            elapsed = (time.time() - start) * 1000
            metrics = {
                k: float(v)
                for k, v in outputs.get("metrics", {}).items()
                if isinstance(v, (int, float))
            }
            return SimulationResult(
                simulator_id=self.id,
                simulator_name=self.name,
                status=SimulationStatus.COMPLETED,
                parameters=parameters,
                outputs=outputs,
                metrics=metrics,
                charts={s["key"]: s["values"] for s in outputs.get("series", [])},
                execution_time_ms=elapsed,
            )
        except Exception as e:
            return SimulationResult(
                simulator_id=self.id,
                simulator_name=self.name,
                status=SimulationStatus.FAILED,
                parameters=parameters,
                error=str(e),
                execution_time_ms=(time.time() - start) * 1000,
            )

    def _run(self, params: dict[str, Any]) -> dict:
        rng = random.Random(int(params.get("seed", 42)))
        n_occ = int(params.get("n_occurrences", 80))
        study_area = float(params.get("study_area_size", 5000.0))
        reg = float(params.get("regularization_multiplier", 1.0))
        n = 40
        env = []
        for i in range(n):
            for j in range(n):
                env.append(
                    {
                        "temp": 12 + 8 * math.sin(i / 12) + rng.uniform(-1, 1),
                        "precip": 400 + 150 * math.cos(j / 10) + rng.uniform(-20, 20),
                        "elev": 200 + 100 * math.sin(i / 15) * math.cos(j / 14),
                    }
                )
        occ_idx = rng.sample(range(len(env)), min(n_occ, len(env)))
        occ = [env[i] for i in occ_idx]
        avg_t = sum(x["temp"] for x in occ) / len(occ)
        avg_p = sum(x["precip"] for x in occ) / len(occ)
        avg_e = sum(x["elev"] for x in occ) / len(occ)
        scores = []
        for e in env:
            dist = (
                abs(e["temp"] - avg_t) * 0.4
                + abs(e["precip"] - avg_p) * 0.003
                + abs(e["elev"] - avg_e) * 0.01
            )
            scores.append(max(0.0, min(1.0, 1.0 / (1.0 + dist * reg * 0.15))))
        suitable = sum(1 for s in scores if s > 0.5) * (study_area / len(scores))
        return {
            "series": [
                {
                    "key": "suitability",
                    "label": "Suitability sample",
                    "color": "#10b981",
                    "values": [round(s, 3) for s in scores[:80]],
                    "kind": "bar",
                }
            ],
            "metrics": {
                "mean_suitability": round(sum(scores) / len(scores), 4),
                "suitable_area_km2": round(suitable, 2),
                "percent_suitable": round(100 * suitable / study_area, 2),
                "n_cells": len(scores),
                "engine": "pure_python_maxent_proxy",
            },
            "disclaimer": "Proxy model — not official MaxEnt.",
        }
