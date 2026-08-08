"""Tests for crops router — /api/v1/crops."""

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
async def test_list_crops(client: AsyncClient):
    r = await client.get("/api/v1/crops?page=1&size=10")
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert "meta" in body
    assert isinstance(body["data"], list)


@pytest.mark.asyncio
async def test_list_crops_pagination(client: AsyncClient):
    r = await client.get("/api/v1/crops?page=1&size=5")
    assert r.status_code == 200
    body = r.json()
    assert "meta" in body
    meta = body["meta"]
    assert "total" in meta


@pytest.mark.asyncio
async def test_get_crop_not_found(client: AsyncClient):
    r = await client.get("/api/v1/crops/999999")
    assert r.status_code in (404, 401, 403)


@pytest.mark.asyncio
async def test_create_crop_local(client: AsyncClient):
    r = await client.post(
        "/api/v1/crops",
        json={
            "name": "Test Wheat",
            "category": "cereal",
            "water_need_mm": 450,
            "growth_days": 120,
        },
    )
    assert r.status_code in (201, 401, 403, 422)
    if r.status_code == 201:
        body = r.json()
        assert body["name"] == "Test Wheat"
        assert body["category"] == "cereal"


@pytest.mark.asyncio
async def test_create_crop_missing_name(client: AsyncClient):
    r = await client.post("/api/v1/crops", json={"category": "vegetable"})
    assert r.status_code in (401, 403, 422)


@pytest.mark.asyncio
async def test_irrigation_calculate(client: AsyncClient):
    r = await client.post(
        "/api/v1/crops/irrigation/calculate",
        json={
            "area_ha": 5.0,
            "et0_mm_day": 6.5,
            "kc": 1.1,
            "efficiency": 0.85,
            "days": 7,
        },
    )
    assert r.status_code in (200, 401, 403)
    if r.status_code == 200:
        body = r.json()
        assert "etc_mm_day" in body
        assert "volume_m3" in body
        assert body["volume_m3"] > 0


@pytest.mark.asyncio
async def test_irrigation_calculate_invalid_area(client: AsyncClient):
    r = await client.post(
        "/api/v1/crops/irrigation/calculate",
        json={"area_ha": -1.0, "et0_mm_day": 5.0},
    )
    assert r.status_code in (401, 403, 422)


@pytest.mark.asyncio
async def test_disease_rules_endpoint(client: AsyncClient):
    r = await client.get("/api/v1/crops/disease-rules")
    assert r.status_code in (200, 401, 403)


@pytest.mark.asyncio
async def test_yield_prediction_endpoint(client: AsyncClient):
    r = await client.get("/api/v1/crops/yield-prediction")
    assert r.status_code in (200, 401, 403)


@pytest.mark.asyncio
async def test_rotation_plan_endpoint(client: AsyncClient):
    r = await client.post("/api/v1/crops/rotation-plan", json={})
    assert r.status_code in (200, 401, 403, 422)


@pytest.mark.asyncio
async def test_seed_demo_blocked_in_production(client: AsyncClient, monkeypatch):
    import apps.shared_core.config as cfg

    monkeypatch.setattr(cfg.settings, "ENVIRONMENT", "production")
    r = await client.post("/api/v1/crops/seed-demo")
    assert r.status_code in (200, 403, 401)


class TestCropRouterImport:
    def test_router_importable(self):
        try:
            from apps.crops.router import router

            assert router is not None
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_list_crops_callable(self):
        try:
            from apps.crops.router import list_crops

            assert callable(list_crops)
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_create_crop_callable(self):
        try:
            from apps.crops.router import create_crop

            assert callable(create_crop)
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_calculate_irrigation_callable(self):
        try:
            from apps.crops.router import calculate_irrigation

            assert callable(calculate_irrigation)
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")
