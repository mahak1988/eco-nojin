"""Contract: farms list/create."""

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
async def test_list_farms(client: AsyncClient):
    r = await client.get("/api/v1/farms?page=1&size=5")
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert "meta" in body


@pytest.mark.asyncio
async def test_create_farm_local(client: AsyncClient):
    r = await client.post(
        "/api/v1/farms",
        json={"name": "Contract Field", "region": "Test", "area_ha": 1.5},
    )
    # local soft auth may allow; otherwise 401
    assert r.status_code in (201, 401, 403)
    if r.status_code == 201:
        assert r.json().get("name") == "Contract Field"
