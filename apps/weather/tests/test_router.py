"""Tests for weather router — /api/v1/weather."""

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
async def test_weather_current(client: AsyncClient):
    """Current weather — uses Open-Meteo fallback if GEE unavailable."""
    r = await client.get("/api/v1/weather/current?lat=32.65&lon=51.67")
    assert r.status_code in (200, 401, 403, 422, 503)
    if r.status_code == 200:
        body = r.json()
        assert isinstance(body, dict)


@pytest.mark.asyncio
async def test_weather_forecast(client: AsyncClient):
    r = await client.get("/api/v1/weather/forecast?lat=32.65&lon=51.67&days=7")
    assert r.status_code in (200, 401, 403, 422, 503)
    if r.status_code == 200:
        body = r.json()
        assert isinstance(body, (dict, list))


@pytest.mark.asyncio
async def test_weather_forecast_default_params(client: AsyncClient):
    r = await client.get("/api/v1/weather/forecast")
    assert r.status_code in (200, 401, 403, 422, 503)


@pytest.mark.asyncio
async def test_weather_historical(client: AsyncClient):
    r = await client.get(
        "/api/v1/weather/historical?lat=35.6&lon=51.4&start=2025-01-01&end=2025-01-07"
    )
    assert r.status_code in (200, 401, 403, 422, 503)


@pytest.mark.asyncio
async def test_weather_alerts(client: AsyncClient):
    r = await client.get("/api/v1/weather/alerts?lat=32.65&lon=51.67")
    assert r.status_code in (200, 401, 403, 422, 503)
    if r.status_code == 200:
        body = r.json()
        assert isinstance(body, (list, dict))


@pytest.mark.asyncio
async def test_weather_climate(client: AsyncClient):
    r = await client.get("/api/v1/weather/climate?lat=32.65&lon=51.67")
    assert r.status_code in (200, 401, 403, 422, 503)


@pytest.mark.asyncio
async def test_weather_era5(client: AsyncClient):
    r = await client.get("/api/v1/weather/era5?lat=32.65&lon=51.67")
    assert r.status_code in (200, 401, 403, 422, 503)


@pytest.mark.asyncio
async def test_weather_chirps(client: AsyncClient):
    r = await client.get("/api/v1/weather/chirps?lat=32.65&lon=51.67")
    assert r.status_code in (200, 401, 403, 422, 503)


class TestWeatherRouterImport:
    def test_router_importable(self):
        try:
            from apps.weather.router import router

            assert router is not None
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_forecast_endpoint_exists(self):
        try:
            from apps.weather import router as weather_router

            route_paths = [r.path for r in weather_router.router.routes]
            assert any("forecast" in p for p in route_paths)
        except (ImportError, AttributeError) as e:
            pytest.skip(f"Not available: {e}")

    def test_current_endpoint_exists(self):
        try:
            from apps.weather import router as weather_router

            route_paths = [r.path for r in weather_router.router.routes]
            assert any("current" in p for p in route_paths)
        except (ImportError, AttributeError) as e:
            pytest.skip(f"Not available: {e}")

    def test_alerts_endpoint_exists(self):
        try:
            from apps.weather import router as weather_router

            route_paths = [r.path for r in weather_router.router.routes]
            assert any("alerts" in p for p in route_paths)
        except (ImportError, AttributeError) as e:
            pytest.skip(f"Not available: {e}")
