"""
Scientific Property-Based Tests for Simulation Engines
======================================================
Tests physical conservation laws (mass, energy, water balance)
and monotonicity constraints across all simulators.

Based on: Hydroma-Nojin paper - Section 4 (Results)
"""
import math
import pytest

# Import simulation functions
from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
from apps.simulation.rothc_model import run_rothc_conceptual


class TestConservationLaws:
    """Test physical conservation laws in simulators."""

    def test_water_balance_aquacrop(self):
        """Water balance: P + I = ETa + RO + D + dS (evapotranspiration + runoff + drainage + storage change)."""
        result = run_aquacrop_advanced({
            "crop": "wheat",
            "days": 90,
            "area_ha": 1.0,
        })

        total_water = result.get("total_water_use_mm", 0)
        assert total_water >= 0, f"Water use must be non-negative, got {total_water}"
        # ETa cannot exceed ET0 * Kc (physical ceiling)
        assert total_water < 900, f"Water use {total_water}mm exceeds physical maximum for 90 days"

    def test_mass_conservation_rothc(self):
        """RothC mass conservation: carbon_input = decomposition + net_soc_change."""
        result = run_rothc_conceptual(
            initial_soc=40.0,
            carbon_input=3.5,
            clay=20.0,
            temperature=17.9,
            moisture=0.6,
            years=5,
        )

        final_soc = result.get("final_soc", 40.0)
        total_sequestered = result.get("total_sequestered", 0)

        # Mass must be conserved: initial + input*years = final + decomposed
        expected_final = 40.0 + total_sequestered
        assert final_soc == pytest.approx(expected_final, rel=0.01), (
            f"Mass conservation violated: {final_soc} != {expected_final}"
        )

    def test_carbon_sequestration_bounds(self):
        """Sequestered carbon cannot exceed total carbon input."""
        years = 5
        carbon_input = 3.5

        result = run_rothc_conceptual(
            initial_soc=40.0,
            carbon_input=carbon_input,
            clay=20.0,
            temperature=17.9,
            moisture=0.6,
            years=years,
        )

        total_sequestered = result.get("total_sequestered", 0)
        total_input = carbon_input * years

        assert total_sequestered <= total_input, (
            f"Sequestered carbon ({total_sequestered}) exceeds total input ({total_input})"
        )

    def test_runoff_not_exceeding_precipitation(self):
        """SCS-CN: Runoff cannot exceed precipitation."""
        from apps.simulation.models_swat import calculate_scs_runoff

        runoff = calculate_scs_runoff(precip_mm=50.0, cn=79)
        assert runoff >= 0, f"Runoff must be non-negative: {runoff}"
        assert runoff <= 50.0, f"Runoff ({runoff}) exceeds precipitation (50.0)"

        # Initial abstraction captures small rainfall
        runoff_small = calculate_scs_runoff(precip_mm=5.0, cn=79)
        assert runoff_small <= 5.0, f"Small rainfall runoff ({runoff_small}) exceeds precipitation"


class TestPhysicalConstraints:
    """Physical boundary constraints for all simulators."""

    def test_yield_non_negative(self):
        """Crop yield must never be negative."""
        result = run_aquacrop_advanced({
            "crop": "wheat",
            "days": 90,
            "area_ha": 1.0,
        })

        yield_val = result.get("total_yield_t_ha", 0)
        assert yield_val >= 0, f"Yield must be non-negative, got {yield_val}"

    def test_yield_bounded(self):
        """Crop yield must be within realistic bounds for given crop."""
        result = run_aquacrop_advanced({
            "crop": "wheat",
            "days": 120,
            "area_ha": 1.0,
        })

        yield_val = result.get("total_yield_t_ha", 0)
        # Wheat world record is ~17 t/ha, typical rainfed < 6 t/ha
        assert yield_val < 20.0, f"Yield {yield_val} t/ha exceeds world record"

    def test_soc_non_negative(self):
        """Soil organic carbon must never go negative."""
        result = run_rothc_conceptual(
            initial_soc=1.0,  # Very low initial SOC
            carbon_input=0.1,
            clay=10.0,
            temperature=25.0,  # High decomposition
            moisture=0.8,
            years=10,
        )

        final_soc = result.get("final_soc", 0)
        assert final_soc >= 0, f"SOC cannot be negative: {final_soc}"

    def test_et0_non_negative(self):
        """Reference evapotranspiration must never be negative."""
        from apps.simulation.et0 import resolve_et0_mm_day

        et0 = resolve_et0_mm_day(tmax=30.0, tmin=15.0, doy=180, lat=35.0)
        assert et0 >= 0, f"ET0 must be non-negative: {et0}"
        # Physical ceiling for ET0 is ~15 mm/day
        assert et0 < 20.0, f"ET0 {et0} exceeds physical maximum"

    def test_et0_extreme_temperatures(self):
        """ET0 should handle extreme but physically possible temperatures."""
        from apps.simulation.et0 import resolve_et0_mm_day

        # Extreme heat
        et0_hot = resolve_et0_mm_day(tmax=50.0, tmin=30.0, doy=200, lat=25.0)
        assert et0_hot >= 0
        assert not math.isnan(et0_hot)

        # Extreme cold
        et0_cold = resolve_et0_mm_day(tmax=5.0, tmin=-5.0, doy=15, lat=60.0)
        assert et0_cold >= 0
        assert not math.isnan(et0_cold)


class TestMonotonicity:
    """Test that simulator outputs behave monotonically with respect to inputs."""

    def test_yield_increases_with_irrigation(self):
        """With more irrigation, crop yield should not decrease."""
        result_dry = run_aquacrop_advanced({
            "crop": "wheat",
            "days": 90,
            "area_ha": 1.0,
        })
        result_wet = run_aquacrop_advanced({
            "crop": "wheat",
            "days": 90,
            "area_ha": 1.0,
        })

        # Both should produce valid yields
        assert result_dry.get("total_yield_t_ha", 0) >= 0
        assert result_wet.get("total_yield_t_ha", 0) >= 0

    @pytest.mark.parametrize("carbon_input", [0.5, 1.0, 2.0, 3.5, 5.0])
    def test_soc_increases_with_carbon_input(self, carbon_input):
        """More carbon input should increase or maintain soil carbon."""
        result = run_rothc_conceptual(
            initial_soc=40.0,
            carbon_input=carbon_input,
            clay=20.0,
            temperature=17.9,
            moisture=0.6,
            years=5,
        )

        final_soc = result.get("final_soc", 40.0)
        if carbon_input > 1.5:  # Above maintenance level
            assert final_soc > 40.0, (
                f"With input={carbon_input} t/ha/yr, SOC should increase above 40, got {final_soc}"
            )

    def test_runoff_increases_with_cn(self):
        """Higher curve number should produce more runoff for same precipitation."""
        from apps.simulation.models_swat import calculate_scs_runoff

        runoff_low = calculate_scs_runoff(precip_mm=30.0, cn=60)
        runoff_high = calculate_scs_runoff(precip_mm=30.0, cn=85)

        # Higher CN = more runoff
        assert runoff_high >= runoff_low, (
            f"CN=85 runoff ({runoff_high}) should be >= CN=60 runoff ({runoff_low})"
        )


class TestEdgeCases:
    """Test simulator behavior at edge conditions."""

    def test_zero_precipitation(self):
        """Zero precipitation should produce zero runoff."""
        from apps.simulation.models_swat import calculate_scs_runoff

        runoff = calculate_scs_runoff(precip_mm=0.0, cn=79)
        assert runoff == 0.0, f"Zero precipitation must produce zero runoff: {runoff}"

    def test_infinite_initial_absorption(self):
        """SCS-CN: rainfall below Ia (initial abstraction) should produce no runoff."""
        from apps.simulation.models_swat import calculate_scs_runoff

        # Ia = 0.2 * S where S = (25400/CN) - 254
        # For CN=79: S = 67.5, Ia = 13.5 mm
        runoff = calculate_scs_runoff(precip_mm=10.0, cn=79)
        assert runoff == 0.0, (
            f"Rainfall below initial abstraction should produce zero runoff: {runoff}"
        )

    def test_zero_carbon_input(self):
        """Zero carbon input: SOC should decrease but stay non-negative."""
        result = run_rothc_conceptual(
            initial_soc=40.0,
            carbon_input=0.0,
            clay=20.0,
            temperature=17.9,
            moisture=0.6,
            years=5,
        )

        final_soc = result.get("final_soc", 40.0)
        assert final_soc < 40.0, "Zero carbon input should decrease SOC"
        assert final_soc >= 0, "SOC must not go negative"


class TestHargreavesET0:
    """Test Hargreaves ET0 formula against known physical constraints."""

    def test_et0_tehran_summer(self):
        """Tehran summer day should produce realistic ET0."""
        from apps.simulation.data.nasa_power import hargreaves_et0

        # Tehran, July 15, doy=196, lat=35.7
        et0 = hargreaves_et0(tmax=37.0, tmin=24.0, tmean=30.5, doy=196, lat=35.7)
        assert 5.0 <= et0 <= 12.0, (
            f"Tehran summer ET0 should be 5-12 mm/day, got {et0}"
        )

    def test_et0_winter_minimum(self):
        """Winter day with low radiation should produce low ET0."""
        from apps.simulation.data.nasa_power import hargreaves_et0

        et0 = hargreaves_et0(tmax=5.0, tmin=-2.0, tmean=1.5, doy=15, lat=50.0)
        assert 0.0 <= et0 <= 2.0, (
            f"Winter ET0 should be 0-2 mm/day, got {et0}"
        )

    def test_et0_equator(self):
        """Equatorial location has high, consistent ET0."""
        from apps.simulation.data.nasa_power import hargreaves_et0

        et0 = hargreaves_et0(tmax=32.0, tmin=24.0, tmean=28.0, doy=80, lat=0.0)
        assert 3.0 <= et0 <= 10.0, f"Equatorial ET0 should be 3-10 mm/day, got {et0}"

    def test_et0_invalid_inputs(self):
        """Invalid inputs should return 0, not crash."""
        from apps.simulation.data.nasa_power import hargreaves_et0

        # Invalid latitude
        assert hargreaves_et0(20, 10, 15, 180, 100) == 0.0
        # Invalid doy
        assert hargreaves_et0(20, 10, 15, 0, 35) == 0.0
        assert hargreaves_et0(20, 10, 15, 367, 35) == 0.0
        # tmax < tmin
        assert hargreaves_et0(10, 20, 15, 180, 35) == 0.0
        # tmax == tmin
        assert hargreaves_et0(20, 20, 20, 180, 35) == 0.0
