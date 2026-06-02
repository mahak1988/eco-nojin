import pytest
from httpx import ASGITransport, AsyncClient
from api.main import app


@pytest.mark.asyncio
async def test_otp_request_dev_code():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/v1/auth/otp/request",
            json={"phone": "+989001112233", "fid": "otp_test"},
        )
    assert res.status_code == 200
    body = res.json()
    assert body["sent"] is True
    assert "dev_code" in body
