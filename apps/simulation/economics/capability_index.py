"""Capability index + fuzzy logic — phase 15.3. Manifest §6.3"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np

DIMS = ["water", "food", "income", "health", "knowledge"]

@dataclass
class FuzzySet:
    a: float; b: float; c: float; d: float
    def mu(self, x):
        if x <= self.a or x >= self.d: return 0.0
        if self.b <= x <= self.c: return 1.0
        if x < self.b: return (x-self.a)/(self.b-self.a+1e-15)
        return (self.d-x)/(self.d-self.c+1e-15)

LOW, MED, HIGH = FuzzySet(0,0,25,40), FuzzySet(30,45,55,70), FuzzySet(60,75,100,100)

@dataclass
class CapabilityConfig:
    weights: Optional[np.ndarray] = None
    dims: List[str] = field(default_factory=lambda: list(DIMS))

def fuzzy_score(x):
    return {"low": LOW.mu(x), "med": MED.mu(x), "high": HIGH.mu(x)}

def defuzzify_centroid(scores):
    centres = {"low": 20.0, "med": 50.0, "high": 85.0}
    num = sum(scores[k]*centres[k] for k in centres)
    den = sum(scores[k] for k in centres)+1e-15
    return float(num/den/100.0)

def capability_index(raw, cfg=None):
    cfg = cfg or CapabilityConfig()
    w = cfg.weights if cfg.weights is not None else np.ones(len(cfg.dims))/len(cfg.dims)
    w = np.asarray(w, float); w = w/(w.sum()+1e-15)
    per_dim, values = {}, []
    for i, d in enumerate(cfg.dims):
        x = float(raw.get(d, 50.0)); fs = fuzzy_score(x); v = defuzzify_centroid(fs)
        per_dim[d] = {"raw": x, "fuzzy": fs, "score": v}; values.append(v)
    values = np.array(values); ci = float(np.dot(w, values))
    return {"status": "ok", "CI": ci, "CI_pct": ci*100, "per_dimension": per_dim, "weights": w.tolist()}

if __name__ == "__main__":
    out = capability_index({"water":55,"food":70,"income":40,"health":65,"knowledge":50})
    print(f"CI={out['CI_pct']:.1f}%"); print("OK")
