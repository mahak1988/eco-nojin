from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
from apps.simulation.models_swat import run_swat_plus
from apps.simulation.scenario_engine import run_scenarios


def test_swat_proxy():
    r = run_swat_plus({"area_km2": 10, "precip_mm_year": 400})
    assert r["model"] == "swat_plus_proxy"
    assert "water_yield_mm_year" in r["outputs"]


def test_aquacrop_advanced():
    r = run_aquacrop_advanced({"days": 20, "area_ha": 1})
    assert r["irrigation_need_mm"] >= 0
    assert 0 <= r["yield_relative"] <= 1.5


def test_aquacrop_ndvi_canopy():
    r = run_aquacrop_advanced({"days": 10, "canopy_cover": [0.2, 0.5, 0.8] * 4})
    assert r["ndvi_calibrated"] is True


def test_scenarios_rank():
    out = run_scenarios()
    assert out["count"] >= 2
    assert out["best"] is not None
