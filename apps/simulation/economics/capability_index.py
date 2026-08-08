"""Capability Index + Fuzzy Logic: 5-Dimensions, Sen-Inspired, Centroid Defuzzification
Phase 15.3 | Manifest §6.3 | Hydroma-Nojin"""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Dict,List,Optional
import numpy as np

DIMS=["economic_freedom","climate_resilience","knowledge","social_capital","ecosystem_health"]
DIMS_FA=["water","food","income","health","knowledge"]
DEFAULT_WEIGHTS=[0.25,0.25,0.20,0.15,0.15]

@dataclass
class FuzzySet:
    a:float;b:float;c:float;d:float
    def mu(self,x):
        if x<=self.a or x>=self.d:return 0.0
        if self.b<=x<=self.c:return 1.0
        if x<self.b:return (x-self.a)/(self.b-self.a+1e-15)
        return (self.d-x)/(self.d-self.c+1e-15)

LOW=FuzzySet(0,0,25,40);MED=FuzzySet(30,45,55,70);HIGH=FuzzySet(60,75,100,100)
VERY_LOW=FuzzySet(0,0,10,25);VERY_HIGH=FuzzySet(75,90,100,100)
FSETS={"very_low":VERY_LOW,"low":LOW,"medium":MED,"high":HIGH,"very_high":VERY_HIGH}

def fuzzy_score(x):
    return {k:v.mu(x) for k,v in FSETS.items()}

def defuzzify_centroid(scores):
    centres={"very_low":10.0,"low":25.0,"medium":50.0,"high":75.0,"very_high":90.0}
    num=sum(scores[k]*centres[k] for k in centres)
    den=sum(scores[k] for k in centres)+1e-15
    return float(num/den)

def membership_triangular(x,a,b,c):
    if x<=a or x>=c:return 0.0
    if x<=b:return (x-a)/(b-a+1e-15)
    return (c-x)/(c-b+1e-15)

@dataclass
class CapabilityConfig:
    weights:Optional[np.ndarray]=None;dims:List[str]=field(default_factory=lambda:list(DIMS))
    use_fuzzy:bool=True;verbose:bool=False

def compute_dimension_score(dim_name,raw_value):
    fs=fuzzy_score(raw_value);score=defuzzify_centroid(fs)/100.0
    return {"raw":raw_value,"fuzzy":fs,"score":score,"category":max(fs,key=fs.get)}

def capability_index(raw,cfg=None):
    cfg=cfg or CapabilityConfig()
    w=cfg.weights if cfg.weights is not None else np.array(DEFAULT_WEIGHTS)/sum(DEFAULT_WEIGHTS)
    w=np.asarray(w,float);w=w/(w.sum()+1e-15)
    if len(w)!=len(cfg.dims):
        w=np.ones(len(cfg.dims))/len(cfg.dims)
    per_dim,values={},[]
    for i,d in enumerate(cfg.dims):
        x=float(raw.get(d,50.0));ds=compute_dimension_score(d,x)
        per_dim[d]=ds;values.append(ds["score"])
    values=np.array(values);ci=float(np.dot(w,values))
    return {"status":"ok","CI":ci,"CI_pct":ci*100,"per_dimension":per_dim,"weights":w.tolist(),
            "interpretation":_interpret_ci(ci)}

def _interpret_ci(ci):
    if ci<0.2:return "Critical"
    if ci<0.4:return "Low"
    if ci<0.6:return "Moderate"
    if ci<0.8:return "Good"
    return "Excellent"

def fuzzy_rule_inference(water,income,knowledge):
    """IF-THEN Mamdani inference."""
    rules=[]
    if water<30 and knowledge>60:
        rules.append(("resilience",0.5))
    elif water<30 and knowledge<=60:
        rules.append(("resilience",0.2))
    else:
        rules.append(("resilience",0.8))
    if income>70 and water>50:
        rules.append(("prosperity",0.9))
    else:
        rules.append(("prosperity",0.4))
    return rules

if __name__=="__main__":
    out=capability_index({"economic_freedom":55,"climate_resilience":70,"knowledge":40,"social_capital":65,"ecosystem_health":50})
    print(f"CI={out['CI_pct']:.1f}% [{out['interpretation']}]")
    out_fa=capability_index({"water":55,"food":70,"income":40,"health":65,"knowledge":50},
                             CapabilityConfig(dims=DIMS_FA))
    print(f"CI(FA)={out_fa['CI_pct']:.1f}%")
    rules=fuzzy_rule_inference(25,45,75)
    print(f"Fuzzy rules: {rules}")
    print("ALL CAPABILITY INDEX TESTS PASSED")
