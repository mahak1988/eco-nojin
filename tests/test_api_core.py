import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "healthy"
    assert "auth" in body["modules"]


@pytest.mark.asyncio
async def test_auth_login_and_profile():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post(
            "/api/v1/auth/login",
            json={"fid": "farmer_test_01", "phone": "+989121234567", "name": "Test"},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]

        profile = await client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert profile.status_code == 200
        assert profile.json()["fid"] == "farmer_test_01"


@pytest.mark.asyncio
async def test_farmer_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/api/v1/farmers/",
            json={"name": "Ali Rezaei", "phone": "+989111111111"},
        )
        assert created.status_code == 201
        farmer_id = created.json()["id"]

        fetched = await client.get(f"/api/v1/farmers/{farmer_id}")
        assert fetched.status_code == 200
        assert fetched.json()["name"] == "Ali Rezaei"
