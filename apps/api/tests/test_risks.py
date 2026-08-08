"""
Risks Engine Tests
==================
Tests for heuristic agricultural risk scoring models.
"""

from apps.risks.engine import (
    RiskInput,
    RiskReport,
    _clamp,
    _level,
    evaluate_risks,
    score_disease,
    score_drought,
    score_erosion,
    score_flood,
    score_frost,
    score_heat,
    score_pest,
)


class TestLevelClamp:
    """Tests for helper functions."""

    def test_level_thresholds(self) -> None:
        assert _level(0) == "low"
        assert _level(34.9) == "low"
        assert _level(35) == "moderate"
        assert _level(54.9) == "moderate"
        assert _level(55) == "high"
        assert _level(74.9) == "high"
        assert _level(75) == "critical"
        assert _level(100) == "critical"

    def test_clamp(self) -> None:
        assert _clamp(150) == 100.0
        assert _clamp(-5) == 0.0
        assert _clamp(50) == 50.0
        assert _clamp(50, lo=10, hi=60) == 50.0
        assert _clamp(5, lo=10, hi=60) == 10.0
        assert _clamp(70, lo=10, hi=60) == 60.0


class TestRiskScoring:
    """Tests for individual risk scoring functions."""

    def test_drought_dry(self) -> None:
        """Verify drought risk increases with water stress."""
        inp = RiskInput(
            soil_moisture_pct=20,
            precip_7d_mm=0,
            et0_7d_mm=35,
            days_since_rain=15,
            temp_max_c=35,
        )
        item = score_drought(inp)
        assert item.code == "drought"
        assert item.score > 35  # moderate or higher
        assert len(item.drivers) > 0
        assert len(item.actions) > 0

    def test_drought_normal(self) -> None:
        """Verify low drought risk under normal conditions."""
        inp = RiskInput(
            soil_moisture_pct=50,
            precip_7d_mm=20,
            et0_7d_mm=28,
            days_since_rain=2,
        )
        item = score_drought(inp)
        assert item.score < 35

    def test_flood_normal(self) -> None:
        """Verify low flood risk under dry conditions."""
        inp = RiskInput(precip_7d_mm=5, soil_moisture_pct=30, slope_pct=10)
        item = score_flood(inp)
        assert item.score < 35
        assert "no acute flood signal" in item.drivers

    def test_flood_heavy_rain(self) -> None:
        """Verify flood risk increases with heavy rain."""
        inp = RiskInput(precip_7d_mm=60, soil_moisture_pct=85, slope_pct=2)
        item = score_flood(inp)
        assert item.score > 55
        assert "heavy 7d rain" in " ".join(item.drivers)

    def test_erosion_flat_bare(self) -> None:
        """Verify erosion risk with bare slope."""
        inp = RiskInput(slope_pct=15, vegetation_cover_pct=10, precip_7d_mm=40, wind_m_s=5)
        item = score_erosion(inp)
        assert item.score > 35
        assert "sparse cover" in " ".join(item.drivers)

    def test_erosion_stable(self) -> None:
        """Verify low erosion risk with good cover."""
        inp = RiskInput(slope_pct=3, vegetation_cover_pct=80, precip_7d_mm=5, wind_m_s=2)
        item = score_erosion(inp)
        assert item.score < 35

    def test_pest_vegetable_hot_humid(self) -> None:
        """Verify pest risk for vegetable in hot humidity."""
        inp = RiskInput(temp_max_c=35, humidity_pct=70, crop_category="vegetable")
        item = score_pest(inp)
        assert item.score > 35
        assert "vegetable" in " ".join(item.drivers)

    def test_pest_cereal_cool(self) -> None:
        """Verify low pest risk for cereal in cool conditions."""
        inp = RiskInput(temp_max_c=22, humidity_pct=40, crop_category="cereal")
        item = score_pest(inp)
        assert item.score < 35

    def test_disease_hot_humid(self) -> None:
        """Verify disease risk in humid warm conditions."""
        inp = RiskInput(temp_max_c=24, humidity_pct=80, precip_7d_mm=30)
        item = score_disease(inp)
        assert item.score > 35
        assert "high humidity" in " ".join(item.drivers)

    def test_disease_cool_dry(self) -> None:
        """Verify low disease risk in dry conditions."""
        inp = RiskInput(temp_max_c=15, humidity_pct=30, precip_7d_mm=2)
        item = score_disease(inp)
        assert item.score < 35

    def test_heat_extreme(self) -> None:
        """Verify heat stress with extreme temperature."""
        inp = RiskInput(temp_max_c=45)
        item = score_heat(inp)
        assert item.score > 55
        assert "45" in " ".join(item.drivers)

    def test_heat_normal(self) -> None:
        """Verify low heat risk in normal conditions."""
        inp = RiskInput(temp_max_c=30)
        item = score_heat(inp)
        assert item.score < 10

    def test_frost_risk(self) -> None:
        """Verify frost risk when min temp < 2°C."""
        inp = RiskInput(temp_min_c=-5)
        item = score_frost(inp)
        assert item.score > 55
        assert "-5" in " ".join(item.drivers)

    def test_frost_no_risk(self) -> None:
        """Verify no frost risk when min temp > 2°C."""
        inp = RiskInput(temp_min_c=10)
        item = score_frost(inp)
        assert item.score == 0
        assert "no frost" in " ".join(item.drivers)


class TestEvaluateRisks:
    """Tests for the overall evaluate_risks function."""

    def test_default_input(self) -> None:
        """Verify RiskInput has sensible defaults."""
        inp = RiskInput()
        assert inp.lat == 32.6
        assert inp.lon == 51.7
        assert inp.crop_category == "cereal"

    def test_evaluate_risks_structure(self) -> None:
        """Verify evaluate_risks returns proper structure."""
        report = evaluate_risks(RiskInput())
        assert isinstance(report, RiskReport)
        assert isinstance(report.overall_score, float)
        assert 0 <= report.overall_score <= 100
        assert report.overall_level in ("low", "moderate", "high", "critical")
        assert len(report.items) == 7  # 7 risk types
        assert len(report.notes) > 0

    def test_evaluate_risks_sorted(self) -> None:
        """Verify items are sorted by score descending."""
        report = evaluate_risks(RiskInput())
        scores = [item.score for item in report.items]
        assert scores == sorted(scores, reverse=True)

    def test_evaluate_risks_codes(self) -> None:
        """Verify all expected risk codes are present."""
        report = evaluate_risks(RiskInput())
        codes = {item.code for item in report.items}
        expected = {"drought", "flood", "erosion", "pest", "disease", "heat", "frost"}
        assert codes == expected

    def test_high_risk_input(self) -> None:
        """Verify high-risk input produces critical or high overall."""
        inp = RiskInput(
            soil_moisture_pct=15,
            precip_7d_mm=5,
            et0_7d_mm=40,
            temp_max_c=42,
            temp_min_c=-5,
            days_since_rain=20,
            humidity_pct=75,
            slope_pct=15,
            vegetation_cover_pct=10,
            crop_category="vegetable",
        )
        report = evaluate_risks(inp)
        assert report.overall_level in ("high", "critical")
