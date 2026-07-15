from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_and_login_flow():
    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "StrongPass!123",
        "displayName": "Alice Demo",
        "acceptedTerms": True,
    }

    register_response = client.post("/auth/register", json=payload)
    assert register_response.status_code == 201, register_response.text
    body = register_response.json()
    assert body["user"]["username"] == "alice"
    assert body["accessToken"]

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {body['accessToken']}"},
    )
    assert me_response.status_code == 200, me_response.text
    assert me_response.json()["username"] == "alice"
