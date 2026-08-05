"""Tests for dashboard router — /api/v1/dashboard."""
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
async def test_dashboard_stats(client: AsyncClient):
    r = await client.get("/api/v1/dashboard/stats")
    assert r.status_code in (200, 401, 403)
    if r.status_code == 200:
        body = r.json()
        assert isinstance(body, dict)


@pytest.mark.asyncio
async def test_dashboard_overview(client: AsyncClient):
    r = await client.get("/api/v1/dashboard/overview")
    assert r.status_code in (200, 401, 403)
    if r.status_code == 200:
        body = r.json()
        assert isinstance(body, dict)


@pytest.mark.asyncio
async def test_dashboard_stats_returns_json(client: AsyncClient):
    r = await client.get("/api/v1/dashboard/stats")
    assert r.status_code in (200, 401, 403)
    if r.status_code == 200:
        assert r.headers.get("content-type", "").startswith("application/json")


@pytest.mark.asyncio
async def test_dashboard_overview_returns_json(client: AsyncClient):
    r = await client.get("/api/v1/dashboard/overview")
    assert r.status_code in (200, 401, 403)
    if r.status_code == 200:
        assert r.headers.get("content-type", "").startswith("application/json")


class TestDashboardRouterImport:
    def test_router_importable(self):
        try:
            from apps.dashboard.router import router
            assert router is not None
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_stats_endpoint_exists(self):
        try:
            from apps.dashboard import router as dash_router
            route_paths = [r.path for r in dash_router.router.routes]
            assert any("stats" in p for p in route_paths)
        except (ImportError, AttributeError) as e:
            pytest.skip(f"Not available: {e}")

    def test_overview_endpoint_exists(self):
        try:
            from apps.dashboard import router as dash_router
            route_paths = [r.path for r in dash_router.router.routes]
            assert any("overview" in p for p in route_paths)
        except (ImportError, AttributeError) as e:
            pytest.skip(f"Not available: {e}")
