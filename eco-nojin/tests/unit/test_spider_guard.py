from fastapi import FastAPI
from fastapi.testclient import TestClient
from apps.spider_security.middleware import SpiderGuardMiddleware


def test_basic_request_passes():
    app = FastAPI()
    app.add_middleware(SpiderGuardMiddleware, max_requests=5, window_seconds=1, block_after=True)

    @app.get("/ping")
    def ping():
        return {"ok": True}

    client = TestClient(app)
    r = client.get("/ping", headers={"User-Agent": "pytest"})
    assert r.status_code == 200
    assert r.json() == {"ok": True}
