"""
DayCent-style 7-pool soil organic matter / carbon model.

Pools (from typical §3.1 extension):
  MET  – Metabolic litter          (fast, labile plant residues)
  STR  – Structural litter         (cellulose / lignin-rich)
  ACT  – Active SOM                (microbial biomass + products)
  SLOW – Slow SOM                  (physically protected / intermediate)
  PASS – Passive SOM               (chemically stabilised, centuries)
  DOC  – Dissolved Organic Carbon  (mobile, leachable)
  BC   – Black Carbon / Biochar    (highly recalcitrant)

Turnover follows first-order kinetics modified by temperature,
moisture and soil texture (clay) factors, following the classic
CENTURY / DayCent philosophy (Parton et al.).

This module is self-contained and can be synchronised with a local
project via the helper at the bottom.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional, Tuple, List
from enum import Enum
import json
from pathlib import Path


class Pool(str, Enum):
    MET = "MET"
    STR = "STR"
    ACT = "ACT"
    SLOW = "SLOW"
    PASS = "PASS"
    DOC = "DOC"
    BC = "BC"


# Default potential decomposition rates [1/day]  (order-of-magnitude DayCent-like)
DEFAULT_K = {
    Pool.MET: 0.05,      # ~ weeks
    Pool.STR: 0.01,      # months
    Pool.ACT: 0.02,      # months–year
    Pool.SLOW: 0.0005,   # decades
    Pool.PASS: 0.00001,  # centuries
    Pool.DOC: 0.1,       # days–weeks (highly labile)
    Pool.BC: 0.000001,   # millennia (very stable)
}


@dataclass
class SoilState:
    """Carbon stocks [g C m-2] (or any consistent mass unit)."""
    MET: float = 0.0
    STR: float = 0.0
    ACT: float = 0.0
    SLOW: float = 0.0
    PASS: float = 0.0
    DOC: float = 0.0
    BC: float = 0.0

    def as_array(self) -> np.ndarray:
        return np.array([self.MET, self.STR, self.ACT, self.SLOW, self.PASS, self.DOC, self.BC])

    def total_soc(self) -> float:
        """Total soil organic carbon excluding pure litter if desired; here includes all."""
        return float(self.MET + self.STR + self.ACT + self.SLOW + self.PASS + self.DOC + self.BC)

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, float]) -> "SoilState":
        return cls(**{k: float(d.get(k, 0.0)) for k in cls.__dataclass_fields__})


@dataclass
class EnvironmentalDrivers:
    """Daily drivers."""
    temperature: float          # °C  (soil or air, depending on formulation)
    moisture: float             # volumetric water content or relative water content [0-1]
    clay_fraction: float = 0.2  # 0-1
    precipitation: float = 0.0  # mm d-1 (used for DOC leaching)
    pet: float = 0.0            # potential ET mm d-1


@dataclass
class FlowFractions:
    """
    Carbon transfer coefficients (partitioning of decomposed C).
    Values are illustrative; calibrate to site.
    """
    # from MET
    met_to_act: float = 0.45
    met_to_doc: float = 0.10
    met_to_co2: float = 0.45

    # from STR  (lignin effect reduces to ACT, increases to SLOW)
    str_to_act: float = 0.30
    str_to_slow: float = 0.25
    str_to_doc: float = 0.05
    str_to_co2: float = 0.40

    # from ACT
    act_to_slow: float = 0.25
    act_to_pass: float = 0.02
    act_to_doc: float = 0.08
    act_to_co2: float = 0.65

    # from SLOW
    slow_to_act: float = 0.15
    slow_to_pass: float = 0.05
    slow_to_doc: float = 0.02
    slow_to_co2: float = 0.78

    # from PASS
    pass_to_act: float = 0.05
    pass_to_doc: float = 0.01
    pass_to_co2: float = 0.94

    # from DOC
    doc_to_act: float = 0.40
    doc_to_co2: float = 0.50
    doc_leach: float = 0.10   # fraction lost to leaching (further modified by water flux)

    # from BC (very little moves)
    bc_to_pass: float = 0.01
    bc_to_co2: float = 0.005
    # remainder stays in BC


def temperature_factor(t_c: float, t_opt: float = 30.0, t_max: float = 45.0) -> float:
    """DayCent-style Q10 / Lloyd-Taylor-ish temperature response (simplified)."""
    if t_c <= 0.0:
        return 0.0
    # classic CENTURY:  tfunc = 0.125 * exp(0.07 * t)  clipped
    tf = np.exp(0.08 * (t_c - 10.0))   # rough Q10≈2.2
    return float(np.clip(tf, 0.0, 3.0))


def moisture_factor(theta: float, theta_opt: float = 0.6) -> float:
    """Simple parabolic / linear moisture response."""
    if theta <= 0.0:
        return 0.0
    if theta < theta_opt:
        return float(theta / theta_opt)
    # slight decline above optimum
    return float(max(0.0, 1.0 - 0.5 * (theta - theta_opt) / (1.0 - theta_opt)))


def clay_factor(clay: float) -> float:
    """Higher clay stabilises (slows) decomposition of SLOW & PASS."""
    return float(1.0 - 0.75 * np.clip(clay, 0.0, 0.6))


@dataclass
class DayCentSevenPool:
    """
    Stateful 7-pool simulator.
    """
    state: SoilState = field(default_factory=SoilState)
    k: Dict[Pool, float] = field(default_factory=lambda: DEFAULT_K.copy())
    flows: FlowFractions = field(default_factory=FlowFractions)
    lignin_str: float = 0.25          # fraction of STR that is lignin-like
    co2_total: float = 0.0            # cumulative CO2-C emitted
    leached_doc: float = 0.0          # cumulative DOC leached

    def potential_decomp(self, pool: Pool, env: EnvironmentalDrivers) -> float:
        """k_eff * C"""
        tf = temperature_factor(env.temperature)
        mf = moisture_factor(env.moisture)
        cf = 1.0
        if pool in (Pool.SLOW, Pool.PASS, Pool.BC):
            cf = clay_factor(env.clay_fraction)
        # structural litter slowed by lignin
        if pool == Pool.STR:
            cf *= (1.0 - 0.7 * self.lignin_str)
        k_eff = self.k[pool] * tf * mf * cf
        c = getattr(self.state, pool.value)
        return k_eff * c

    def step(self, env: EnvironmentalDrivers, dt: float = 1.0) -> Dict[str, float]:
        """
        Advance one time step (default daily).
        Returns fluxes of CO2 and leached DOC for the step.
        """
        # 1. compute potential decomposition amounts
        decomp = {p: self.potential_decomp(p, env) * dt for p in Pool}

        # 2. allocate flows
        f = self.flows
        co2 = 0.0
        leach = 0.0

        # MET
        d = decomp[Pool.MET]
        self.state.MET -= d
        self.state.ACT += d * f.met_to_act
        self.state.DOC += d * f.met_to_doc
        co2 += d * f.met_to_co2

        # STR
        d = decomp[Pool.STR]
        self.state.STR -= d
        self.state.ACT += d * f.str_to_act
        self.state.SLOW += d * f.str_to_slow
        self.state.DOC += d * f.str_to_doc
        co2 += d * f.str_to_co2

        # ACT
        d = decomp[Pool.ACT]
        self.state.ACT -= d
        self.state.SLOW += d * f.act_to_slow
        self.state.PASS += d * f.act_to_pass
        self.state.DOC += d * f.act_to_doc
        co2 += d * f.act_to_co2

        # SLOW
        d = decomp[Pool.SLOW]
        self.state.SLOW -= d
        self.state.ACT += d * f.slow_to_act
        self.state.PASS += d * f.slow_to_pass
        self.state.DOC += d * f.slow_to_doc
        co2 += d * f.slow_to_co2

        # PASS
        d = decomp[Pool.PASS]
        self.state.PASS -= d
        self.state.ACT += d * f.pass_to_act
        self.state.DOC += d * f.pass_to_doc
        co2 += d * f.pass_to_co2

        # DOC – decomposition + leaching
        d = decomp[Pool.DOC]
        self.state.DOC -= d
        self.state.ACT += d * f.doc_to_act
        co2 += d * f.doc_to_co2
        # extra leaching driven by water surplus
        water_surplus = max(0.0, env.precipitation - env.pet)
        leach_frac = f.doc_leach * min(1.0, water_surplus / 20.0)  # simple scaling
        leach_amt = self.state.DOC * leach_frac
        self.state.DOC -= leach_amt
        leach += leach_amt

        # BC
        d = decomp[Pool.BC]
        self.state.BC -= d
        self.state.PASS += d * f.bc_to_pass
        co2 += d * f.bc_to_co2
        # remainder stays

        # numerical safety
        for p in Pool:
            v = getattr(self.state, p.value)
            if v < 0:
                setattr(self.state, p.value, 0.0)

        self.co2_total += co2
        self.leached_doc += leach

        return {"co2": co2, "leach_doc": leach, "total_soc": self.state.total_soc()}

    def add_litter(self, metabolic: float, structural: float, doc: float = 0.0, bc: float = 0.0) -> None:
        """Plant residue / external carbon inputs."""
        self.state.MET += metabolic
        self.state.STR += structural
        self.state.DOC += doc
        self.state.BC += bc

    def add_biochar(self, amount: float) -> None:
        self.state.BC += amount

    def snapshot(self) -> Dict:
        return {
            "state": self.state.to_dict(),
            "co2_total": self.co2_total,
            "leached_doc": self.leached_doc,
            "total_soc": self.state.total_soc(),
        }

    def run_sequence(
        self,
        drivers: List[EnvironmentalDrivers],
        litter_inputs: Optional[List[Tuple[float, float]]] = None,
    ) -> List[Dict]:
        """Run a multi-day sequence. litter_inputs = list of (met, str) per day."""
        history = []
        for i, env in enumerate(drivers):
            if litter_inputs is not None and i < len(litter_inputs):
                met, st = litter_inputs[i]
                self.add_litter(met, st)
            flux = self.step(env)
            history.append({**self.snapshot(), **flux})
        return history


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def save_state(model: DayCentSevenPool, path: str | Path) -> None:
    path = Path(path)
    data = {
        "state": model.state.to_dict(),
        "k": {p.value: model.k[p] for p in Pool},
        "co2_total": model.co2_total,
        "leached_doc": model.leached_doc,
        "lignin_str": model.lignin_str,
    }
    path.write_text(json.dumps(data, indent=2))


def load_state(path: str | Path) -> DayCentSevenPool:
    data = json.loads(Path(path).read_text())
    state = SoilState.from_dict(data["state"])
    k = {Pool(p): v for p, v in data.get("k", {}).items()}
    model = DayCentSevenPool(state=state, k=k or DEFAULT_K.copy())
    model.co2_total = data.get("co2_total", 0.0)
    model.leached_doc = data.get("leached_doc", 0.0)
    model.lignin_str = data.get("lignin_str", 0.25)
    return model


# ---------------------------------------------------------------------------
# Synchronisation command with local project
# ---------------------------------------------------------------------------

SYNC_README = """
# همسان‌سازی (Sync) با پروژه محلی

## روش پیشنهادی (rsync یا git)

### ۱. اگر مخزن git دارید:
```bash
# از ریشه پروژه محلی
git remote add origin <URL-مخزن>
git fetch origin
git checkout -b feature/daycent-seven-pool
# کپی فایل‌های تولید شده
cp -r /path/to/artifacts/apps ./
git add apps/satellite/algorithms/sebs.py \\
        apps/satellite/algorithms/kriging.py \\
        apps/simulation/biogeochemistry/daycent_seven_pool.py
git commit -m "Sprint 0: SEBS + Kriging precip + DayCent 7-pool"
git push -u origin feature/daycent-seven-pool
```

### ۲. همسان‌سازی مستقیم با rsync (بدون git):
```bash
# از ماشین دارای artifacts
rsync -av --progress \\
  /home/workdir/artifacts/apps/ \\
  user@local-machine:/path/to/your/project/apps/
```

### ۳. دستور یک‌خطی برای کپی داخل همان میزبان (اگر پروژه محلی روی همان FS است):
```bash
PROJECT_ROOT=/path/to/your/local/project
mkdir -p $PROJECT_ROOT/apps/satellite/algorithms
mkdir -p $PROJECT_ROOT/apps/simulation/biogeochemistry
cp apps/satellite/algorithms/sebs.py          $PROJECT_ROOT/apps/satellite/algorithms/
cp apps/satellite/algorithms/kriging.py       $PROJECT_ROOT/apps/satellite/algorithms/
cp apps/simulation/biogeochemistry/daycent_seven_pool.py \\
                                               $PROJECT_ROOT/apps/simulation/biogeochemistry/
```

### وابستگی‌ها
```bash
pip install numpy scipy
```

پس از کپی، می‌توانید تست‌های داخلی را اجرا کنید:
```bash
python -m apps.satellite.algorithms.sebs
python -m apps.satellite.algorithms.kriging
python -m apps.simulation.biogeochemistry.daycent_seven_pool
```
"""


if __name__ == "__main__":
    # Quick demonstration
    model = DayCentSevenPool(
        state=SoilState(MET=50, STR=200, ACT=300, SLOW=2000, PASS=5000, DOC=10, BC=100)
    )
    print("Initial total SOC:", model.state.total_soc())

    drivers = [
        EnvironmentalDrivers(temperature=22.0, moisture=0.45, clay_fraction=0.25, precipitation=5.0, pet=3.5)
        for _ in range(30)
    ]
    litter = [(2.0, 5.0)] * 30  # daily litter input

    hist = model.run_sequence(drivers, litter)
    print(f"After 30 days:")
    print(f"  total SOC   : {hist[-1]['total_soc']:.1f}")
    print(f"  cumulative CO2-C : {hist[-1]['co2_total']:.1f}")
    print(f"  cumulative DOC leach : {hist[-1]['leached_doc']:.2f}")
    print("  final pools :", hist[-1]["state"])

    # write the sync instructions next to the module
    sync_path = Path(__file__).with_name("SYNC_INSTRUCTIONS.md")
    sync_path.write_text(SYNC_README)
    print(f"\nSync instructions written to {sync_path}")
