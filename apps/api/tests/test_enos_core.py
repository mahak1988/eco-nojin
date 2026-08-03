"""Unit tests for ENOS-ISA core (ET0, SCS-CN, HCWF)."""
from datetime import datetime, timedelta, timezone

from apps.core.fusion.hcwf import DataPoint, DataSource, HCWFFusion
from apps.core.models.penman_monteith import WeatherData, calculate_et0
from apps.core.models.scs_cn import adjust_cn_amc, calculate_runoff


def test_et0_never_negative():
    w = WeatherData(
        t_max=5.0,
        t_min=-10.0,
        rh_mean=90.0,
        wind_speed_2m=0.5,
        solar_radiation=5.0,
        elevation=2000,
        latitude=35.7,
    )
    assert calculate_et0(w) >= 0.0


def test_et0_summer_iran_range():
    w = WeatherData(
        t_max=40.0,
        t_min=22.0,
        rh_mean=25.0,
        wind_speed_2m=2.0,
        solar_radiation=25.0,
        elevation=1200,
        latitude=35.7,
    )
    et0 = calculate_et0(w)
    assert 6.0 <= et0 <= 14.0


def test_runoff_no_rain():
    assert calculate_runoff(0, 72) == 0.0


def test_runoff_low_rain_below_ia():
    assert calculate_runoff(10, 72) == 0.0


def test_runoff_basic_range():
    q = calculate_runoff(50, 72)
    assert 10.0 <= q <= 20.0


def test_amc_order():
    cn_ii = 72
    assert adjust_cn_amc(cn_ii, "I") < cn_ii < adjust_cn_amc(cn_ii, "III")


def test_hcwf_single_source():
    fusion = HCWFFusion((35.7, 51.4))
    now = datetime.now(timezone.utc)
    data = [
        DataPoint(0.25, DataSource.MANUAL, now, 0.70, 100, "vwc"),
    ]
    result = fusion.fuse(data, "soil_moisture")
    assert abs(result.value - 0.25) < 0.01
    assert result.quality_tier >= 1


def test_hcwf_multi_source():
    fusion = HCWFFusion((35.7, 51.4))
    now = datetime.now(timezone.utc)
    data = [
        DataPoint(0.20, DataSource.MANUAL, now, 0.70, 100, "vwc"),
        DataPoint(0.25, DataSource.SATELLITE, now, 0.85, 10, "vwc"),
        DataPoint(0.23, DataSource.SENSOR, now, 0.95, 1, "vwc"),
    ]
    result = fusion.fuse(data, "soil_moisture")
    assert 0.20 <= result.value <= 0.26
    assert result.confidence > 0.7
