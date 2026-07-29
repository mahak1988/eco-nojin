from apps.ml.global_sensitivity import (
    full_global_sensitivity,
    morris_elementary_effects,
    saltelli_sobol,
    standardized_regression_coefficients,
)
from apps.ml.service import train_default_models


def test_src_morris_sobol():
    train_default_models(n_samples=300, seed=7)
    src = standardized_regression_coefficients(n_samples=80, seed=1, target="yield")
    assert len(src["coefficients"]) == 10
    assert "r_squared" in src

    morris = morris_elementary_effects(n_trajectories=6, levels=4, seed=2, target="yield")
    assert len(morris["effects"]) == 10
    assert morris["effects"][0]["mu_star"] >= 0

    sobol = saltelli_sobol(n_base=24, seed=3, target="yield")
    assert len(sobol["indices"]) == 10
    assert sobol["n_model_runs"] == 24 * (2 + 10)
    for row in sobol["indices"]:
        assert "S1" in row and "ST" in row

    full = full_global_sensitivity(n_src=60, n_morris=5, n_sobol=20, seed=5)
    assert "summary_fa" in full
    assert set(full["methods"]) == {"SRC", "Morris", "Saltelli-Sobol"}
