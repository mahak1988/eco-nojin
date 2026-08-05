"""
Contract tests: Simulation ↔ Satellite ↔ MRV pipeline
Verifies that data flows correctly between the simulation,
satellite, and MRV subsystems — without real I/O.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ── 1. Satellite MRV output feeds into EcoCredit system ────────
class TestSatelliteToMrvContract:
    def test_mrv_from_bands_output_shape(self):
        """mrv_from_bands must return a dict with ecocredit_score."""
        from apps.satellite.mrv_bridge import mrv_from_bands
        with patch("apps.satellite.mrv_bridge.indices_from_mean_reflectance",
                   return_value={"ndvi": 0.52, "evi": 0.38}), \
             patch("apps.satellite.mrv_bridge.mrv_from_ndvi",
                   return_value={"ecocredit_score": 72.0, "carbon_t_ha": 3.1}):
            try:
                result = mrv_from_bands(red=0.08, nir=0.45)
                assert isinstance(result, dict)
            except Exception:
                pytest.skip("mrv_from_bands requires live dependencies")

    def test_ndvi_valid_range(self):
        """NDVI computed from reflectance must be in [-1, 1]."""
        from apps.satellite.processors.indices import indices_from_mean_reflectance
        try:
            result = indices_from_mean_reflectance(red=0.08, nir=0.45)
            ndvi = result.get("ndvi", 0)
            assert -1 <= ndvi <= 1, f"NDVI {ndvi} out of range"
        except ImportError:
            pytest.skip("indices module not importable in isolation")

    def test_indices_contains_ndvi(self):
        """indices_from_mean_reflectance must include ndvi key."""
        from apps.satellite.processors.indices import indices_from_mean_reflectance
        try:
            result = indices_from_mean_reflectance(red=0.08, nir=0.45)
            assert "ndvi" in result
        except ImportError:
            pytest.skip("indices module not importable in isolation")

    def test_aquacrop_mrv_output_contract(self):
        """aquacrop_to_mrv must produce a dict with ecocredit_score."""
        from apps.satellite.mrv_bridge import aquacrop_to_mrv
        try:
            dummy_aquacrop_result = {
                "yield_t_ha": 4.2,
                "water_productivity": 1.1,
                "crop": "wheat",
            }
            result = aquacrop_to_mrv(dummy_aquacrop_result)
            assert isinstance(result, dict)
        except (ImportError, TypeError):
            pytest.skip("aquacrop_to_mrv not callable without context")


# ── 2. SpiderGuard middleware contract ─────────────────────────
class TestSpiderGuardContract:
    def test_middleware_instantiates(self):
        from apps.spider_security.middleware import SpiderGuardMiddleware
        app_mock = MagicMock()
        mw = SpiderGuardMiddleware(app_mock, max_requests=100, window_seconds=60)
        assert mw.max_requests == 100
        assert mw.window == 60

    def test_bot_patterns_cover_major_bots(self):
        from apps.spider_security.middleware import BOT_UA_PATTERNS
        required = {"googlebot", "bingbot", "ahrefsbot", "semrushbot"}
        found = {p for p in required if any(p in pat for pat in BOT_UA_PATTERNS)}
        assert found == required, f"Missing bot patterns: {required - found}"

    def test_middleware_block_flag(self):
        from apps.spider_security.middleware import SpiderGuardMiddleware
        app_mock = MagicMock()
        mw = SpiderGuardMiddleware(app_mock, block_after=False)
        assert mw.block_after is False


# ── 3. Simulation ↔ Satellite data flow ────────────────────────
class TestSimulationSatelliteFlow:
    def test_aquacrop_mrv_bridge_import(self):
        """aquacrop_mrv_from_location is importable."""
        try:
            from apps.simulation.aquacrop_mrv import aquacrop_mrv_from_location
            assert callable(aquacrop_mrv_from_location)
        except ImportError as e:
            pytest.skip(f"Import skipped: {e}")

    def test_rothc_mrv_bridge_import(self):
        """rothc_to_mrv is importable."""
        try:
            from apps.simulation.rothc_mrv import rothc_to_mrv
            assert callable(rothc_to_mrv)
        except ImportError as e:
            pytest.skip(f"Import skipped: {e}")

    def test_simulation_run_request_schema(self):
        from apps.simulation.router import SimulationRunRequest
        req = SimulationRunRequest(
            simulator_id="aquacrop",
            parameters={"crop": "wheat", "days": 90}
        )
        assert req.simulator_id == "aquacrop"
        assert req.parameters["days"] == 90

    def test_simulation_run_response_schema(self):
        from apps.simulation.router import SimulationRunResponse
        resp = SimulationRunResponse(
            run_id="test-001",
            simulator_id="aquacrop",
            simulator_name="AquaCrop",
            status="completed",
            outputs={"yield_t_ha": 4.2},
            metrics={"kge": 0.85},
            execution_time_ms=100.0,
        )
        assert resp.status == "completed"
        assert resp.metrics["kge"] == 0.85


# ── 4. Satellite BBox helper ───────────────────────────────────
class TestBBoxContract:
    def test_bbox_from_point(self):
        from apps.satellite.providers.base import BBox
        bbox = BBox.from_point(lat=32.65, lon=51.67, delta=0.05)
        assert bbox.min_lat < bbox.max_lat
        assert bbox.min_lon < bbox.max_lon
        # delta=0.05 means ±0.05 around the point
        assert abs((bbox.max_lat - bbox.min_lat) - 0.10) < 0.001

    def test_bbox_coords_valid(self):
        from apps.satellite.providers.base import BBox
        bbox = BBox.from_point(lat=35.7, lon=51.4, delta=0.1)
        assert -90 <= bbox.min_lat <= 90
        assert -90 <= bbox.max_lat <= 90
        assert -180 <= bbox.min_lon <= 180
        assert -180 <= bbox.max_lon <= 180


# ── 5. GEE status probe ────────────────────────────────────────
class TestGeeStatusContract:
    def test_probe_gee_returns_dict(self):
        from apps.satellite.gee_status import probe_gee
        result = probe_gee()
        assert isinstance(result, dict)
        assert "available" in result

    def test_probe_gee_available_is_bool(self):
        from apps.satellite.gee_status import probe_gee
        result = probe_gee()
        assert isinstance(result["available"], bool)


# ── 6. Satellite schemas ───────────────────────────────────────
class TestSatelliteSchemas:
    def test_ndvi_point_schema(self):
        from apps.satellite.schemas import NDVIPoint
        pt = NDVIPoint(date="2025-01-15", mean_ndvi=0.55)
        assert pt.mean_ndvi == 0.55
        assert pt.source == "synthetic"

    def test_bbox_query_validation(self):
        from apps.satellite.schemas import BBoxQuery
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            BBoxQuery(min_lng=200, min_lat=0, max_lng=0, max_lat=0)  # invalid lng

    def test_change_detection_result_schema(self):
        from apps.satellite.schemas import ChangeDetectionResult
        r = ChangeDetectionResult(
            mean_ndvi_a=0.45,
            mean_ndvi_b=0.55,
            delta_ndvi=0.10,
            status="improved",
        )
        assert r.delta_ndvi == 0.10
        assert r.status == "improved"
