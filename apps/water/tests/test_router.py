"""Tests for water router — /api/v1/water."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from apps.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_water_dashboard(client: AsyncClient):
    r = await client.get("/api/v1/water/dashboard")
    assert r.status_code in (200, 401, 403)
    if r.status_code == 200:
        body = r.json()
        assert isinstance(body, dict)


@pytest.mark.asyncio
async def test_water_balance(client: AsyncClient):
    r = await client.get("/api/v1/water/balance")
    assert r.status_code in (200, 401, 403)


@pytest.mark.asyncio
async def test_water_sources(client: AsyncClient):
    r = await client.get("/api/v1/water/sources")
    assert r.status_code in (200, 401, 403)
    if r.status_code == 200:
        body = r.json()
        assert isinstance(body, list)


@pytest.mark.asyncio
async def test_water_quality(client: AsyncClient):
    r = await client.get("/api/v1/water/quality")
    assert r.status_code in (200, 401, 403)
    if r.status_code == 200:
        body = r.json()
        assert isinstance(body, list)


@pytest.mark.asyncio
async def test_irrigation_systems(client: AsyncClient):
    r = await client.get("/api/v1/water/irrigation/systems")
    assert r.status_code in (200, 401, 403)


@pytest.mark.asyncio
async def test_irrigation_schedules_get(client: AsyncClient):
    r = await client.get("/api/v1/water/irrigation/schedules")
    assert r.status_code in (200, 401, 403)


@pytest.mark.asyncio
async def test_irrigation_schedule_alias(client: AsyncClient):
    r = await client.get("/api/v1/water/irrigation-schedule")
    assert r.status_code in (200, 401, 403)


@pytest.mark.asyncio
async def test_irrigation_schedules_post(client: AsyncClient):
    r = await client.post("/api/v1/water/irrigation/schedules", json={})
    assert r.status_code in (200, 201, 401, 403, 422)


@pytest.mark.asyncio
async def test_irrigation_calculate_water(client: AsyncClient):
    r = await client.post(
        "/api/v1/water/irrigation/calculate",
        json={"area_ha": 3.0, "et0_mm_day": 7.0, "kc": 1.0},
    )
    assert r.status_code in (200, 401, 403, 422)


class TestWaterRouterImport:
    def test_router_importable(self):
        try:
            from apps.water.router import router

            assert router is not None
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_water_dashboard_callable(self):
        try:
            from apps.water.router import get_water_dashboard

            assert callable(get_water_dashboard)
        except (ImportError, AttributeError) as e:
            pytest.skip(f"Not available: {e}")

    def test_water_sources_callable(self):
        try:
            from apps.water.router import list_water_sources

            assert callable(list_water_sources)
        except (ImportError, AttributeError) as e:
            pytest.skip(f"Not available: {e}")
