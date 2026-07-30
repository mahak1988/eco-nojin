"""Phase 3 smoke tests."""

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
    assert "rate_limit" in (r.json().get("security") or {})


@pytest.mark.asyncio
async def test_dashboard_stats(client):
    r = await client.get("/api/v1/dashboard/stats", headers={"User-Agent": "pytest"})
    assert r.status_code == 200
    assert "farms_count" in r.json() or r.json().get("ok") is True


@pytest.mark.asyncio
async def test_dashboard_overview(client):
    r = await client.get("/api/v1/dashboard/overview", headers={"User-Agent": "pytest"})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_debug_routers(client):
    r = await client.get("/api/v1/debug/routers", headers={"User-Agent": "pytest"})
    assert r.status_code == 200
    body = r.json()
    assert len(body.get("loaded") or []) >= 5
    failed = [f.get("label") for f in (body.get("failed") or [])]
    for must in ("farms", "crops", "education", "planting", "inventory"):
        assert must not in failed


@pytest.mark.asyncio
async def test_crops_list(client):
    r = await client.get("/api/v1/crops?page=1&size=5", headers={"User-Agent": "pytest"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert "data" in body and "meta" in body


@pytest.mark.asyncio
async def test_farms_list(client):
    r = await client.get("/api/v1/farms?page=1&size=5", headers={"User-Agent": "pytest"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert "data" in body and "meta" in body


@pytest.mark.asyncio
async def test_pagination_exports():
    from apps.shared_core.schemas.pagination import ListMeta, build_meta, page_to_offset

    assert page_to_offset(2, 10) == 10
    assert isinstance(page_to_offset(1, 20), int)
    m = build_meta(25, 2, 10)
    assert m.pages == 3
    assert isinstance(m, ListMeta)
