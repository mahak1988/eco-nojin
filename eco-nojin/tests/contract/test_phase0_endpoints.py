"""Contract tests for core Phase 0/1 endpoints."""

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
async def test_health(client: AsyncClient):
    r = await client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert "status" in body
    assert "database" in body


@pytest.mark.asyncio
async def test_education_courses_envelope(client: AsyncClient):
    r = await client.get("/api/v1/education/courses?page=1&size=5")
    assert r.status_code == 200
    body = r.json()
    assert "data" in body or "items" in body
    if "meta" in body:
        assert "total" in body["meta"]


@pytest.mark.asyncio
async def test_rbac_seed(client: AsyncClient):
    r = await client.post("/api/v1/rbac/seed")
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True or body.get("roles", 0) >= 1


@pytest.mark.asyncio
async def test_accounting_summary(client: AsyncClient):
    r = await client.get("/api/v1/accounting/summary")
    assert r.status_code == 200
    body = r.json()
    assert "total_income" in body or "net_profit" in body
