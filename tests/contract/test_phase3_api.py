"""Phase 3 smoke: health, dashboard, science, education list envelope."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    from apps.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_security(client):
    r = await client.get("/health", headers={"User-Agent": "pytest"})
    assert r.status_code == 200
    body = r.json()
    assert body.get("database") in ("ok", "fail")
    sec = body.get("security") or {}
    assert "rate_limit" in sec


@pytest.mark.asyncio
async def test_dashboard_stats(client):
    r = await client.get("/api/v1/dashboard/stats", headers={"User-Agent": "pytest"})
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True or body.get("status") == "ok"
    assert "farms_count" in body


@pytest.mark.asyncio
async def test_dashboard_overview(client):
    r = await client.get("/api/v1/dashboard/overview", headers={"User-Agent": "pytest"})
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True or "counts" in body or "farms_count" in body


@pytest.mark.asyncio
async def test_debug_routers(client):
    r = await client.get("/api/v1/debug/routers", headers={"User-Agent": "pytest"})
    assert r.status_code == 200
    body = r.json()
    assert "loaded" in body
    assert body.get("path_count", 0) > 10


@pytest.mark.asyncio
async def test_science_status_if_loaded(client):
    r = await client.get("/api/v1/science/status", headers={"User-Agent": "pytest"})
    # 200 if mounted; 404 if not
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        assert isinstance(r.json(), dict)
