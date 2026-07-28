from apps.simulation.rothc_model import run_rothc
from apps.simulation.rothc_params import PRESETS, falloon_iom, resolve_params, schema_payload


def test_schema_and_presets():
    s = schema_payload()
    assert len(s["parameters"]) >= 15
    assert "iran_arid_rainfed" in PRESETS


def test_resolve_falloon_and_run():
    p = resolve_params({"soc_t_ha": 40.0, "use_falloon_iom": True})
    assert abs(p["iom_t_ha"] - falloon_iom(40.0)) < 0.01
    assert abs(p["dpm_t_ha"] + p["rpm_t_ha"] + p["bio_t_ha"] + p["hum_t_ha"] + p["iom_t_ha"] - 40.0) < 0.05
    r = run_rothc(PRESETS["default_arable"]["params"])
    assert "params_resolved" in r
    assert len(r["series"]) == r["params_resolved"]["years"] + 1


def test_arid_preset_lower_abc():
    arid = run_rothc(PRESETS["iran_arid_rainfed"]["params"])
    mild = run_rothc(PRESETS["default_arable"]["params"])
    assert arid["rate_modifiers"]["b_moisture"] <= mild["rate_modifiers"]["b_moisture"] + 0.05
