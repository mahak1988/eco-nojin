"""Contract tests — crops, water, weather endpoints."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from apps.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Crops ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_crops_list_contract(client: AsyncClient):
    r = await client.get("/api/v1/crops")
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert "meta" in body
    assert isinstance(body["data"], list)
    meta = body["meta"]
    assert "total" in meta
    assert "page" in meta
    assert "size" in meta


@pytest.mark.asyncio
async def test_crops_irrigation_calc_contract(client: AsyncClient):
    r = await client.post(
        "/api/v1/crops/irrigation/calculate",
        json={"area_ha": 10.0, "et0_mm_day": 8.0, "kc": 1.15, "efficiency": 0.9, "days": 14},
    )
    assert r.status_code in (200, 401, 403)
    if r.status_code == 200:
        body = r.json()
        assert "etc_mm_day" in body
        assert "volume_m3" in body
        assert "gross_mm_period" in body
        assert body["volume_m3"] > 0
        assert body["etc_mm_day"] > 0


# ── Water ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_water_dashboard_contract(client: AsyncClient):
    r = await client.get("/api/v1/water/dashboard")
    assert r.status_code in (200, 401, 403)
    if r.status_code == 200:
        body = r.json()
        assert isinstance(body, dict)


@pytest.mark.asyncio
async def test_water_sources_contract(client: AsyncClient):
    r = await client.get("/api/v1/water/sources")
    assert r.status_code in (200, 401, 403)
    if r.status_code == 200:
        assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_water_quality_contract(client: AsyncClient):
    r = await client.get("/api/v1/water/quality")
    assert r.status_code in (200, 401, 403)
    if r.status_code == 200:
        assert isinstance(r.json(), list)


# ── Weather ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_weather_forecast_contract(client: AsyncClient):
    r = await client.get("/api/v1/weather/forecast?lat=35.68&lon=51.38")
    assert r.status_code in (200, 401, 403, 422, 503)


@pytest.mark.asyncio
async def test_weather_current_contract(client: AsyncClient):
    r = await client.get("/api/v1/weather/current?lat=35.68&lon=51.38")
    assert r.status_code in (200, 401, 403, 422, 503)


@pytest.mark.asyncio
async def test_weather_alerts_contract(client: AsyncClient):
    r = await client.get("/api/v1/weather/alerts?lat=35.68&lon=51.38")
    assert r.status_code in (200, 401, 403, 422, 503)


# ── Dashboard ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_dashboard_stats_contract(client: AsyncClient):
    r = await client.get("/api/v1/dashboard/stats")
    assert r.status_code in (200, 401, 403)


@pytest.mark.asyncio
async def test_dashboard_overview_contract(client: AsyncClient):
    r = await client.get("/api/v1/dashboard/overview")
    assert r.status_code in (200, 401, 403)


# ── Risks ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_risks_demo_contract(client: AsyncClient):
    r = await client.get("/api/v1/risks/predict/demo")
    assert r.status_code in (200, 401, 403)
    if r.status_code == 200:
        body = r.json()
        assert isinstance(body, dict)
        assert len(body) > 0


@pytest.mark.asyncio
async def test_risks_predict_contract(client: AsyncClient):
    r = await client.post(
        "/api/v1/risks/predict",
        json={
            "latitude": 32.65,
            "longitude": 51.67,
            "crop_type": "wheat",
            "area_ha": 10.0,
        },
    )
    assert r.status_code in (200, 401, 403, 422)
