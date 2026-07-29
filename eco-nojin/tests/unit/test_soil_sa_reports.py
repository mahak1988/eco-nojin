from apps.simulation.report_builder import report_rothc, report_rusle
from apps.simulation.rothc_model import run_rothc
from apps.simulation.science_analysis import attach_analysis
from apps.simulation.soil_models import run_rusle2, run_soil_profile
from apps.simulation.soil_sensitivity import global_sa_rothc, global_sa_rusle


def test_rusle_and_profile():
    r = run_rusle2({"R": 150, "K": 0.3, "slope_pct": 8, "C": 0.15, "P": 0.7})
    assert r["outputs"]["A_t_ha_year"] > 0
    p = run_soil_profile({"clay_pct": 30})
    assert p["total_awc_mm"] > 0
    assert len(p["layers"]) >= 3


def test_global_sa_soil():
    sa = global_sa_rothc(n_src=40, n_morris=5, n_sobol=16, seed=1)
    assert len(sa["sobol"]["indices"]) == 6
    sa2 = global_sa_rusle(n_src=40, n_morris=5, n_sobol=16, seed=2)
    assert sa2["sobol"]["indices"][0]["ST"] >= 0


def test_final_reports():
    rothc = attach_analysis("rothc", run_rothc({"years": 5}))
    rep = report_rothc(rothc)
    assert rep["report_version"] == "1.1"
    assert "executive_summary_fa" in rep
    rusle = attach_analysis("rusle", run_rusle2({}))
    rep2 = report_rusle(rusle)
    assert any(m["id"] == "A_t_ha_year" for m in rep2["metrics"])
