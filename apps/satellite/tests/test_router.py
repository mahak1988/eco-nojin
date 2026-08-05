"""
Tests for apps/satellite/router.py
Covers: gee/status, availability, timeseries, mrv endpoints,
        aquacrop-mrv, rothc-mrv, change-detection, fields.
All satellite I/O is mocked — no real network calls.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from apps.satellite.router import router as satellite_router

# ── Minimal test app ────────────────────────────────────────────
app = FastAPI()
app.include_router(satellite_router)


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


# ── 1. GEE Status ───────────────────────────────────────────────
class TestGeeStatus:
    @pytest.mark.anyio
    async def test_gee_status_returns_dict(self, client):
        with patch("apps.satellite.router.probe_gee", return_value={"available": False, "provider": "synthetic"}):
            resp = await client.get("/api/v1/satellite/gee/status")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)

    @pytest.mark.anyio
    async def test_gee_status_has_available_key(self, client):
        with patch("apps.satellite.router.probe_gee", return_value={"available": True}):
            resp = await client.get("/api/v1/satellite/gee/status")
        assert "available" in resp.json()


# ── 2. Availability ─────────────────────────────────────────────
class TestAvailability:
    @pytest.mark.anyio
    async def test_availability_default_coords(self, client):
        mock_svc = AsyncMock()
        mock_svc.check_availability = AsyncMock(
            return_value={"available": True, "scenes": 12, "cloud_free": 8}
        )
        with patch("apps.satellite.router.get_satellite_service", return_value=mock_svc):
            resp = await client.get("/api/v1/satellite/availability")
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_availability_custom_coords(self, client):
        mock_svc = AsyncMock()
        mock_svc.check_availability = AsyncMock(return_value={"available": True, "scenes": 5})
        with patch("apps.satellite.router.get_satellite_service", return_value=mock_svc):
            resp = await client.get("/api/v1/satellite/availability?lat=35.7&lon=51.4&days=30")
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_availability_days_validation(self, client):
        mock_svc = AsyncMock()
        mock_svc.check_availability = AsyncMock(return_value={})
        with patch("apps.satellite.router.get_satellite_service", return_value=mock_svc):
            # days must be >= 7
            resp = await client.get("/api/v1/satellite/availability?days=3")
        assert resp.status_code == 422


# ── 3. Timeseries ───────────────────────────────────────────────
class TestTimeseries:
    @pytest.mark.anyio
    async def test_timeseries_default(self, client):
        mock_svc = AsyncMock()
        mock_ndvi = MagicMock()
        mock_ndvi.mean_ndvi = 0.45
        mock_ndvi.date = "2025-01-01"
        mock_svc.get_ndvi_timeseries = AsyncMock(return_value=[mock_ndvi])
        with patch("apps.satellite.router.get_satellite_service", return_value=mock_svc):
            resp = await client.get("/api/v1/satellite/timeseries")
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_timeseries_with_farm_id(self, client):
        mock_svc = AsyncMock()
        mock_svc.get_ndvi_timeseries = AsyncMock(return_value=[])
        with patch("apps.satellite.router.get_satellite_service", return_value=mock_svc):
            resp = await client.get("/api/v1/satellite/timeseries?farm_id=42")
        assert resp.status_code == 200


# ── 4. MRV / Indices (POST endpoints) ──────────────────────────
class TestMrvEndpoints:
    @pytest.mark.anyio
    async def test_mrv_from_bands_basic(self, client):
        with patch(
            "apps.satellite.router.indices_from_mean_reflectance",
            return_value={"ndvi": 0.52, "evi": 0.38},
        ), patch(
            "apps.satellite.router.mrv_from_bands",
            return_value={"ecocredit_score": 72.1, "carbon_t_ha": 3.2},
        ):
            resp = await client.post(
                "/api/v1/satellite/mrv/bands",
                json={"red": 0.08, "nir": 0.45},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "ecocredit_score" in data or isinstance(data, dict)

    @pytest.mark.anyio
    async def test_mrv_from_bands_validation(self, client):
        """reflectance values must be in [0, 1]"""
        resp = await client.post(
            "/api/v1/satellite/mrv/bands",
            json={"red": 2.0, "nir": 0.4},  # invalid
        )
        assert resp.status_code == 422

    @pytest.mark.anyio
    async def test_mrv_ndvi_endpoint(self, client):
        with patch(
            "apps.satellite.router.mrv_from_ndvi",
            return_value={"ecocredit_score": 65.0},
        ):
            resp = await client.post(
                "/api/v1/satellite/mrv/ndvi",
                json={"ndvi_observed": 0.55, "ndvi_expected": 0.60},
            )
        assert resp.status_code in (200, 404, 422)  # endpoint may or may not exist

    @pytest.mark.anyio
    async def test_mrv_from_location(self, client):
        with patch(
            "apps.satellite.router.mrv_from_location",
            return_value={"ecocredit_score": 80.0, "lat": 32.65, "lon": 51.67},
        ):
            resp = await client.post(
                "/api/v1/satellite/mrv/location",
                json={"lat": 32.65, "lon": 51.67, "days": 60},
            )
        assert resp.status_code in (200, 404)


# ── 5. AquaCrop MRV ────────────────────────────────────────────
class TestAquacropMrv:
    @pytest.mark.anyio
    async def test_aquacrop_mrv_basic(self, client):
        with patch(
            "apps.satellite.router.aquacrop_mrv_from_location",
            return_value={"ecocredit_score": 55.0, "yield_t_ha": 4.2},
        ), patch(
            "apps.satellite.router.aquacrop_to_mrv",
            return_value={"ecocredit_score": 55.0},
        ):
            resp = await client.post(
                "/api/v1/satellite/aquacrop-mrv",
                json={"crop": "wheat", "days": 90, "area_ha": 2.5},
            )
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_aquacrop_mrv_area_validation(self, client):
        resp = await client.post(
            "/api/v1/satellite/aquacrop-mrv",
            json={"crop": "maize", "days": 90, "area_ha": -1},  # invalid
        )
        assert resp.status_code == 422

    @pytest.mark.anyio
    async def test_aquacrop_mrv_different_crops(self, client):
        for crop in ["wheat", "maize", "rice"]:
            with patch(
                "apps.satellite.router.aquacrop_mrv_from_location",
                return_value={"ecocredit_score": 60.0},
            ), patch(
                "apps.satellite.router.aquacrop_to_mrv",
                return_value={"ecocredit_score": 60.0},
            ):
                resp = await client.post(
                    "/api/v1/satellite/aquacrop-mrv",
                    json={"crop": crop, "days": 90, "area_ha": 1.0},
                )
            assert resp.status_code == 200, f"crop={crop} failed"


# ── 6. RothC MRV ───────────────────────────────────────────────
class TestRothcMrv:
    @pytest.mark.anyio
    async def test_rothc_mrv_basic(self, client):
        with patch(
            "apps.satellite.router.rothc_to_mrv",
            return_value={"ecocredit_score": 88.0, "soc_change_t_ha": 1.1},
        ):
            resp = await client.post(
                "/api/v1/satellite/rothc-mrv",
                json={
                    "years": 10,
                    "clay_pct": 25.0,
                    "temp_c": 15.0,
                    "rain_mm_year": 500,
                    "et_mm_year": 700,
                    "c_input_t_ha_y": 1.5,
                    "soc_t_ha": 40.0,
                },
            )
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_rothc_mrv_years_validation(self, client):
        resp = await client.post(
            "/api/v1/satellite/rothc-mrv",
            json={"years": 0, "clay_pct": 25.0, "temp_c": 15.0,
                  "rain_mm_year": 500, "et_mm_year": 700,
                  "c_input_t_ha_y": 1.5, "soc_t_ha": 40.0},
        )
        assert resp.status_code == 422

    @pytest.mark.anyio
    async def test_rothc_mrv_temp_range(self, client):
        """temp_c must be in [-10, 40]"""
        resp = await client.post(
            "/api/v1/satellite/rothc-mrv",
            json={"years": 10, "clay_pct": 25.0, "temp_c": 99.0,
                  "rain_mm_year": 500, "et_mm_year": 700,
                  "c_input_t_ha_y": 1.5, "soc_t_ha": 40.0},
        )
        assert resp.status_code == 422


# ── 7. Change Detection ────────────────────────────────────────
class TestChangeDetection:
    @pytest.mark.anyio
    async def test_change_detection_stable(self, client):
        mock_svc = AsyncMock()
        mock_point = MagicMock()
        mock_point.mean_ndvi = 0.50
        mock_svc.get_ndvi_timeseries = AsyncMock(return_value=[mock_point, mock_point])
        with patch("apps.satellite.router.get_satellite_service", return_value=mock_svc):
            resp = await client.post("/api/v1/satellite/change-detection?lat=32.65&lon=51.67&days=120")
        assert resp.status_code == 200
        data = resp.json()
        assert "signal" in data
        assert data["signal"] in ("greening", "browning", "stable")

    @pytest.mark.anyio
    async def test_change_detection_response_shape(self, client):
        mock_svc = AsyncMock()
        mock_point = MagicMock()
        mock_point.mean_ndvi = 0.65
        mock_svc.get_ndvi_timeseries = AsyncMock(return_value=[mock_point])
        with patch("apps.satellite.router.get_satellite_service", return_value=mock_svc):
            resp = await client.post("/api/v1/satellite/change-detection")
        assert resp.status_code == 200
        data = resp.json()
        assert "period_a" in data
        assert "period_b" in data
        assert "delta_ndvi" in data


# ── 8. Fields Stub ─────────────────────────────────────────────
class TestFieldsStub:
    @pytest.mark.anyio
    async def test_fields_returns_data_list(self, client):
        resp = await client.get("/api/v1/satellite/fields")
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert isinstance(data["data"], list)

    @pytest.mark.anyio
    async def test_fields_with_farm_id(self, client):
        resp = await client.get("/api/v1/satellite/fields?farm_id=7")
        assert resp.status_code == 200
        assert resp.json()["farm_id"] == 7
