"""
QAOA-Inspired Water Allocation — فاز ۱۱.۱

Quadratic Unconstrained Binary Optimisation (QUBO) formulation of
multi-farm irrigation scheduling, solved by Simulated Annealing
(classical analogue of QAOA).

Problem:
  Allocate discrete water quanta to n farms over T periods
  subject to total supply constraint, minimising deficit cost
  while respecting per-farm demand and fairness.

Manifest refs: §4.2
Target path: apps/simulation/optimization/qaoa_water_allocation.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


@dataclass
class FarmDemand:
    farm_id: str
    demand: np.ndarray          # shape (T,) water needed per period
    priority: float = 1.0       # higher → higher penalty for deficit
    max_per_period: Optional[float] = None


@dataclass
class WaterAllocationProblem:
    farms: List[FarmDemand]
    supply: np.ndarray          # shape (T,) available water per period
    quantum: float = 10.0       # discrete allocation unit
    fairness_weight: float = 0.1


@dataclass
class SAConfig:
    n_steps: int = 5000
    T0: float = 10.0
    T_min: float = 1e-3
    cooling: float = 0.995
    seed: Optional[int] = 42


def build_qubo(
    problem: WaterAllocationProblem,
) -> Tuple[np.ndarray, Dict]:
    n = len(problem.farms)
    T = len(problem.supply)
    max_q = int(np.ceil(problem.supply.max() / problem.quantum)) + 1
    bits = max(1, int(np.ceil(np.log2(max_q + 1))))
    n_vars = n * T * bits

    Q = np.zeros((n_vars, n_vars))
    meta = {"n": n, "T": T, "bits": bits, "n_vars": n_vars, "quantum": problem.quantum}

    def idx(i: int, t: int, b: int) -> int:
        return (i * T + t) * bits + b

    for i, farm in enumerate(problem.farms):
        for t in range(T):
            demand_q = farm.demand[t] / problem.quantum
            for b in range(bits):
                w = farm.priority * (2 ** b) * (-demand_q)
                Q[idx(i, t, b), idx(i, t, b)] += w * 0.01
    return Q, meta


def decode_bits(x: np.ndarray, meta: Dict) -> np.ndarray:
    n, T, bits = meta["n"], meta["T"], meta["bits"]
    quanta = np.zeros((n, T))
    for i in range(n):
        for t in range(T):
            val = 0
            for b in range(bits):
                bit = x[(i * T + t) * bits + b]
                val += int(bit) * (2 ** b)
            quanta[i, t] = val
    return quanta


def cost_function(
    quanta: np.ndarray,
    problem: WaterAllocationProblem,
) -> float:
    n, T = quanta.shape
    total = 0.0
    fulfilment = []
    for i, farm in enumerate(problem.farms):
        alloc = quanta[i] * problem.quantum
        deficit = np.maximum(0.0, farm.demand - alloc)
        total += farm.priority * np.sum(deficit ** 2)
        dem_sum = farm.demand.sum() + 1e-9
        fulfilment.append(alloc.sum() / dem_sum)
        if farm.max_per_period is not None:
            over = np.maximum(0.0, alloc - farm.max_per_period)
            total += 50.0 * np.sum(over ** 2)
    for t in range(T):
        used = quanta[:, t].sum() * problem.quantum
        excess = max(0.0, used - problem.supply[t])
        total += 100.0 * excess ** 2
    if len(fulfilment) > 1:
        total += problem.fairness_weight * np.var(fulfilment) * 1000.0
    return float(total)


def simulated_annealing(
    problem: WaterAllocationProblem,
    config: Optional[SAConfig] = None,
) -> Dict:
    cfg = config or SAConfig()
    rng = np.random.default_rng(cfg.seed)
    Q, meta = build_qubo(problem)
    n_vars = meta["n_vars"]

    x = rng.integers(0, 2, size=n_vars).astype(np.float64)
    quanta = decode_bits(x, meta)
    best_cost = cost_function(quanta, problem)
    best_x = x.copy()
    current_cost = best_cost
    T = cfg.T0
    history = [best_cost]

    for step in range(cfg.n_steps):
        j = rng.integers(0, n_vars)
        x[j] = 1 - x[j]
        quanta = decode_bits(x, meta)
        new_cost = cost_function(quanta, problem)
        delta = new_cost - current_cost
        if delta < 0 or rng.random() < np.exp(-delta / max(T, 1e-12)):
            current_cost = new_cost
            if new_cost < best_cost:
                best_cost = new_cost
                best_x = x.copy()
        else:
            x[j] = 1 - x[j]
        T = max(cfg.T_min, T * cfg.cooling)
        if step % max(1, cfg.n_steps // 20) == 0:
            history.append(best_cost)

    best_quanta = decode_bits(best_x, meta)
    allocation = best_quanta * problem.quantum
    return {
        "status": "ok",
        "cost": best_cost,
        "allocation": allocation,
        "quanta": best_quanta,
        "history": history,
        "meta": meta,
        "farm_ids": [f.farm_id for f in problem.farms],
    }


def demo_problem() -> WaterAllocationProblem:
    T = 4
    farms = [
        FarmDemand("farm_A", demand=np.array([40.0, 50.0, 45.0, 30.0]), priority=1.2),
        FarmDemand("farm_B", demand=np.array([25.0, 35.0, 40.0, 20.0]), priority=1.0),
        FarmDemand("farm_C", demand=np.array([15.0, 20.0, 25.0, 15.0]), priority=0.8),
    ]
    supply = np.array([70.0, 90.0, 85.0, 55.0])
    return WaterAllocationProblem(farms=farms, supply=supply, quantum=5.0)


def run_qaoa_water_demo(n_steps: int = 3000, verbose: bool = True) -> Dict:
    problem = demo_problem()
    cfg = SAConfig(n_steps=n_steps, T0=20.0, cooling=0.997)
    if verbose:
        print("Running QAOA-inspired SA water allocation …")
    result = simulated_annealing(problem, cfg)
    if verbose:
        print(f"Best cost: {result['cost']:.2f}")
        for i, fid in enumerate(result["farm_ids"]):
            print(f"  {fid}: {result['allocation'][i]}")
    return result


if __name__ == "__main__":
    print("=== QAOA Water Allocation self-test ===")
    out = run_qaoa_water_demo(n_steps=2000, verbose=True)
    print(f"Status: {out['status']}, final cost={out['cost']:.2f}")
    print("OK")
