from apps.simulation.soil_carbon import (
    catalog,
    run_century3,
    run_ensemble,
    run_icbm,
    run_yasso_lite,
)


def test_icbm_runs():
    r = run_icbm({"years": 5, "soc_t_ha": 30, "c_input_t_ha_y": 1.0})
    assert r["model"] == "icbm"
    assert len(r["series"]) == 6


def test_century_and_yasso():
    c = run_century3({"years": 5})
    y = run_yasso_lite({"years": 5})
    assert c["soc_final"] > 0 and y["soc_final"] > 0


def test_ensemble_and_catalog():
    e = run_ensemble({"years": 5, "soc_t_ha": 25})
    assert len(e["comparison"]) == 4
    assert "ensemble_mean_delta" in e
    assert len(catalog()["items"]) >= 4
