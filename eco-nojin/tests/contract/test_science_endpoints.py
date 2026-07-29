"""Contract checks for Phase 3 science API (import-level + formula smoke)."""

from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
from apps.simulation.models_swat import run_swat_plus
from apps.simulation.rothc_model import run_rothc


def test_science_router_module_importable():
    from apps.api.routes import science

    assert science.router.prefix == "/api/v1/science"
    paths = {getattr(r, "path", "") for r in science.router.routes}
    assert any("status" in p for p in paths)
    assert any("aquacrop" in p for p in paths)


def test_aquacrop_contract_keys():
    r = run_aquacrop_advanced({"days": 10, "et0_mm_day": 4.0})
    for k in ("model", "etc_mm", "yield_relative", "citation"):
        assert k in r
    assert r["model"] == "aquacrop_fao_conceptual"


def test_rothc_contract_keys():
    r = run_rothc({"years": 2})
    assert r["model"] == "rothc_26_3"
    assert "series" in r


def test_swat_contract_keys():
    r = run_swat_plus({})
    assert "outputs" in r
    assert "water_yield_mm_year" in r["outputs"]
