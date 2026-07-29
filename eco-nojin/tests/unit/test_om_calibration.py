from apps.simulation.organic_matter import run_litter_cascade, run_om_cn_coupled, run_om_two_pool
from apps.simulation.soil_carbon_calibration import calibrate_soil_carbon


def test_calibrate_icbm():
    obs = [30.0, 29.6, 29.3, 29.1, 28.9]
    out = calibrate_soil_carbon("icbm", obs, n_samples=30, seed=1)
    assert out["best"]["rmse"] is not None
    assert len(out["best"]["simulated_soc"]) == len(obs)


def test_om_models():
    a = run_om_two_pool({"years": 5})
    b = run_om_cn_coupled({"years": 5})
    c = run_litter_cascade({"years": 5})
    assert a["om_final"] > 0 and b["soc_final"] > 0 and c["total_final"] > 0
