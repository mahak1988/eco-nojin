from apps.simulation.kge_deep import kge_components
from apps.simulation.phosphorus_cycle import run_phosphorus_cycle
from apps.simulation.soil_amendment_types import classify_soil, recommend_amendments


def test_p_cycle():
    r = run_phosphorus_cycle({"years": 3, "fertilizer_p_kg_ha_y": 30})
    assert len(r["series"]) == 4
    assert r["balances_kg_ha"]["fertilizer_cum"] > 0


def test_kge_perfect():
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    d = kge_components(x, x)
    assert abs(d["kge_gupta2009"]["value"] - 1.0) < 1e-6


def test_amend_sodic():
    c = classify_soil({"esp_pct": 20, "ec_ds_m": 2, "ph": 8.5})
    assert "sodic" in c["tags"]
    plan = recommend_amendments({"esp_pct": 20, "cec_cmol_kg": 18, "ph": 8.5})
    assert plan["plans"]
