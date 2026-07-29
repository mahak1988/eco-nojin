from apps.crops.agronomy_services import yield_prediction
from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
from apps.simulation.et0 import et0_hargreaves
from apps.simulation.models_swat import run_swat_plus
from apps.simulation.rothc_model import run_rothc


def test_et0_positive():
    e = et0_hargreaves(15, 32, lat_deg=32, day_of_year=180)
    assert 1.0 < e < 12.0


def test_rothc_compartments():
    r = run_rothc({"years": 5, "soc_t_ha": 40, "c_input_t_ha_y": 1.5})
    assert r["model"] == "rothc_26_3"
    assert len(r["series"]) == 6
    assert "dpm" in r["series"][0]


def test_aquacrop_fao_ky():
    dry = run_aquacrop_advanced({"days": 40, "rain_mm_day": 0.0, "et0_mm_day": 5.0})
    wet = run_aquacrop_advanced({"days": 40, "rain_mm_day": 3.0, "et0_mm_day": 5.0})
    assert dry["model"] == "aquacrop_fao_conceptual"
    assert wet["yield_relative"] >= dry["yield_relative"] - 1e-6


def test_scs_cn():
    r = run_swat_plus({"precip_mm_year": 500, "curve_number": 70})
    assert r["outputs"]["runoff_mm_year"] >= 0
    assert "S_mm" in r["inputs"]


def test_yield_ky():
    y0 = yield_prediction("wheat", water_stress=0.0)
    y1 = yield_prediction("wheat", water_stress=0.5)
    assert y0["yield_t_ha"] > y1["yield_t_ha"]
    assert y0["model"] == "fao33_ky_response"
