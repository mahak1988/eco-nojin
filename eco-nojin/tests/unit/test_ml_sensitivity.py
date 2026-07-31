from apps.ml.sensitivity import (
    coefficient_importance,
    full_sensitivity_report,
    oat_sensitivity,
    partial_dependence,
)
from apps.ml.service import train_default_models


def test_sensitivity_pipeline():
    train_default_models(n_samples=250, seed=11)
    coef = coefficient_importance()
    assert len(coef["yield"]) == 10
    oat = oat_sensitivity(rel_step=0.1)
    assert len(oat["features"]) == 10
    assert oat["tornado_yield"][0]["abs_delta_yield"] >= 0
    pd = partial_dependence("mean_ndvi", points=8)
    assert len(pd["series"]) == 8
    full = full_sensitivity_report(rel_step=0.1)
    assert "summary_fa" in full
    assert len(full["partial_dependence"]) >= 1
