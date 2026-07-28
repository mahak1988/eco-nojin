from apps.simulation.evaluation_metrics import evaluate_series, nse, rmse
from apps.simulation.nitrogen_cycle import evaluate_n_series, run_nitrogen_cycle


def test_nse_perfect():
    x = [1.0, 2.0, 3.0, 4.0]
    assert abs(nse(x, x) - 1.0) < 1e-9


def test_nse_mean_baseline():
    o = [1.0, 2.0, 3.0, 4.0]
    mean = sum(o) / len(o)
    s = [mean] * len(o)
    assert abs(nse(o, s)) < 1e-9


def test_evaluate_pack():
    m = evaluate_series([10, 12, 11, 13], [10.5, 11.5, 11.2, 12.5], "soc")
    assert m["n"] == 4
    assert m["nse"] is not None
    assert m["rmse"] is not None


def test_n_cycle_runs():
    r = run_nitrogen_cycle({"years": 3, "fertilizer_n_t_ha_y": 0.1})
    assert len(r["series"]) == 4
    assert r["balances_t_ha"]["fertilizer_cum"] > 0


def test_n_evaluate():
    r = run_nitrogen_cycle({"years": 2})
    obs_no3 = [row["no3"] for row in r["series"]]
    # perfect match
    ev = evaluate_n_series(r, {"no3": obs_no3})
    assert abs(ev["metrics_by_variable"]["no3"]["nse"] - 1.0) < 1e-6
