from apps.simulation.ndvi_canopy import ndvi_to_canopy
from apps.simulation.runners import run_aquacrop_advanced_local, run_swat_local


def test_ndvi_to_canopy():
    cc = ndvi_to_canopy([0.2, 0.5, 0.9])
    assert len(cc) == 3
    assert all(0.05 <= x <= 0.98 for x in cc)
    assert cc[2] > cc[0]


def test_swat_local_no_persist():
    r = run_swat_local({"area_km2": 5}, persist=False)
    assert r["model"] == "swat_plus_proxy"
    assert r["mode"] == "sync_local"


def test_aquacrop_local_no_persist():
    r = run_aquacrop_advanced_local({"days": 15}, persist=False)
    assert r["irrigation_need_mm"] >= 0


def test_phase3_router_imports():
    from apps.simulation.phase3_router import router

    paths = {getattr(r, "path", None) for r in router.routes}
    assert any(p and "runs" in p for p in paths if isinstance(p, str))
    assert any(p and "ndvi-canopy" in p for p in paths if isinstance(p, str))
