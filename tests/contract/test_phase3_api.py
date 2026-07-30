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
    assert "farms_count" in body or body.get("ok") is True


@pytest.mark.asyncio
async def test_dashboard_overview(client):
    r = await client.get("/api/v1/dashboard/overview", headers={"User-Agent": "pytest"})
    assert r.status_code == 200
    body = r.json()
    assert "farms_count" in body or body.get("ok") is True or "counts" in body


@pytest.mark.asyncio
async def test_debug_routers(client):
    r = await client.get("/api/v1/debug/routers", headers={"User-Agent": "pytest"})
    assert r.status_code == 200
    body = r.json()
    assert "loaded" in body
    # path_count can be low if some routers fail; loaded list is the SSOT
    assert len(body.get("loaded") or []) >= 5
    failed_labels = [f.get("label") for f in (body.get("failed") or [])]
    # After pagination fix these must not fail on ListMeta
    for must_work in ("farms", "crops", "education", "planting", "inventory"):
        assert must_work not in failed_labels, f"{must_work} failed: {body.get('failed')}"


@pytest.mark.asyncio
async def test_science_status_if_loaded(client):
    r = await client.get("/api/v1/science/status", headers={"User-Agent": "pytest"})
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        assert isinstance(r.json(), dict)


@pytest.mark.asyncio
async def test_pagination_exports():
    from apps.shared_core.schemas.pagination import ListMeta, build_meta, page_to_offset

    p, s, off = page_to_offset(2, 10)
    assert (p, s, off) == (2, 10, 10)
    m = build_meta(25, 2, 10)
    assert m.pages == 3
    assert isinstance(m, ListMeta)
