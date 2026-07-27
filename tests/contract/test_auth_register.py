"""Contract: register requires accept_terms; login works after register."""

from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from apps.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_register_requires_terms(client: AsyncClient):
    email = f"t_{uuid.uuid4().hex[:8]}@example.com"
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Secret123!", "full_name": "T"},
    )
    # missing accept_terms → 422
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_register_login_me(client: AsyncClient):
    email = f"u_{uuid.uuid4().hex[:8]}@example.com"
    r = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Secret123!",
            "full_name": "Test User",
            "role": "farmer",
            "accept_terms": True,
        },
    )
    assert r.status_code in (200, 201), r.text
    body = r.json()
    assert "accessToken" in body or "access_token" in body

    r2 = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Secret123!"},
    )
    assert r2.status_code == 200, r2.text
