from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
resp = client.post('/auth/register', json={
    'username': 'alice',
    'email': 'alice@example.com',
    'password': 'StrongPass!123',
    'displayName': 'Alice Demo',
    'acceptedTerms': True,
})
print(resp.status_code)
print(resp.text)
