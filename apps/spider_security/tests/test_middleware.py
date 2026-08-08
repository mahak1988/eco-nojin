"""
Tests for apps/spider_security/middleware.py
Covers: bot UA detection, rate limiting, allowed paths bypass,
        header injection, and legitimate user-agent passthrough.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from apps.spider_security.middleware import BOT_UA_PATTERNS, SpiderGuardMiddleware


# ── Minimal test app with SpiderGuard ──────────────────────────
def make_app(max_requests: int = 120, window_seconds: int = 60):
    app = FastAPI()
    app.add_middleware(
        SpiderGuardMiddleware,
        max_requests=max_requests,
        window_seconds=window_seconds,
        block_after=True,
    )

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/api/v1/farms")
    async def farms():
        return {"farms": []}

    @app.get("/api/v1/data")
    async def data():
        return {"data": "value"}

    return app


@pytest.fixture
async def client():
    app = make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


# ── 1. Bot UA Detection ────────────────────────────────────────
class TestBotDetection:
    @pytest.mark.anyio
    async def test_googlebot_blocked(self, client):
        resp = await client.get(
            "/api/v1/farms",
            headers={"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"},
        )
        assert resp.status_code == 403
        assert resp.json()["detail"] == "bot-detected"

    @pytest.mark.anyio
    async def test_bingbot_blocked(self, client):
        resp = await client.get(
            "/api/v1/data",
            headers={"User-Agent": "Mozilla/5.0 (compatible; bingbot/2.0)"},
        )
        assert resp.status_code == 403

    @pytest.mark.anyio
    async def test_semrushbot_blocked(self, client):
        resp = await client.get(
            "/api/v1/farms",
            headers={"User-Agent": "SemrushBot/7~bl"},
        )
        assert resp.status_code == 403

    @pytest.mark.anyio
    async def test_ahrefsbot_blocked(self, client):
        resp = await client.get(
            "/api/v1/data",
            headers={"User-Agent": "Mozilla/5.0 (compatible; AhrefsBot/7.0)"},
        )
        assert resp.status_code == 403

    @pytest.mark.anyio
    async def test_yandexbot_blocked(self, client):
        resp = await client.get(
            "/api/v1/farms",
            headers={"User-Agent": "Mozilla/5.0 (compatible; YandexBot/3.0)"},
        )
        assert resp.status_code == 403


# ── 2. Legitimate Clients Allowed ─────────────────────────────
class TestLegitimateClients:
    @pytest.mark.anyio
    async def test_browser_ua_allowed(self, client):
        resp = await client.get(
            "/api/v1/farms",
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
                )
            },
        )
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_curl_allowed(self, client):
        """curl must NOT be treated as a bot — it's an API client."""
        resp = await client.get(
            "/api/v1/farms",
            headers={"User-Agent": "curl/7.88.1"},
        )
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_httpie_allowed(self, client):
        resp = await client.get(
            "/api/v1/data",
            headers={"User-Agent": "HTTPie/3.2.2"},
        )
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_python_requests_allowed(self, client):
        resp = await client.get(
            "/api/v1/data",
            headers={"User-Agent": "python-requests/2.31.0"},
        )
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_no_ua_allowed(self, client):
        """Missing UA should pass through (not blocked as bot)."""
        resp = await client.get("/api/v1/farms")
        assert resp.status_code == 200


# ── 3. Allowed Paths Bypass ───────────────────────────────────
class TestAllowedPaths:
    @pytest.mark.anyio
    async def test_health_endpoint_bypasses_checks(self, client):
        """Even a bot UA should pass /health."""
        resp = await client.get(
            "/health",
            headers={"User-Agent": "Googlebot/2.1"},
        )
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_root_bypasses_checks(self, client):
        resp = await client.get(
            "/",
            headers={"User-Agent": "Googlebot"},
        )
        # 404 is fine — the point is not 403
        assert resp.status_code != 403


# ── 4. Rate Limiting ──────────────────────────────────────────
class TestRateLimiting:
    @pytest.mark.anyio
    async def test_rate_limit_triggers(self):
        """After max_requests, the client should get 429."""
        app = make_app(max_requests=3, window_seconds=60)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            ua = {"User-Agent": "Mozilla/5.0 legitimate"}
            for _ in range(3):
                r = await c.get("/api/v1/data", headers=ua)
                assert r.status_code == 200
            # 4th request should be rate-limited
            r = await c.get("/api/v1/data", headers=ua)
            assert r.status_code == 429
            assert r.json()["detail"] == "rate-limited"

    @pytest.mark.anyio
    async def test_rate_limit_not_triggered_under_limit(self):
        app = make_app(max_requests=10, window_seconds=60)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            ua = {"User-Agent": "Mozilla/5.0 legitimate"}
            for _ in range(5):
                r = await c.get("/api/v1/data", headers=ua)
                assert r.status_code == 200


# ── 5. Header Injection ────────────────────────────────────────
class TestHeaderInjection:
    @pytest.mark.anyio
    async def test_spiderguard_header_present(self, client):
        resp = await client.get(
            "/api/v1/farms",
            headers={"User-Agent": "Mozilla/5.0 browser"},
        )
        assert resp.headers.get("x-spiderguard-checked") == "1"

    @pytest.mark.anyio
    async def test_spiderguard_header_absent_on_blocked(self, client):
        resp = await client.get(
            "/api/v1/farms",
            headers={"User-Agent": "Googlebot/2.1 (compatible)"},
        )
        assert resp.status_code == 403
        # header should NOT be set for blocked bots
        assert "x-spiderguard-checked" not in resp.headers


# ── 6. BOT_UA_PATTERNS list ───────────────────────────────────
class TestPatternsList:
    def test_patterns_is_list(self):
        assert isinstance(BOT_UA_PATTERNS, list)

    def test_patterns_not_empty(self):
        assert len(BOT_UA_PATTERNS) > 0

    def test_patterns_are_strings(self):
        assert all(isinstance(p, str) for p in BOT_UA_PATTERNS)

    def test_known_bots_in_patterns(self):
        combined = " ".join(BOT_UA_PATTERNS)
        assert "googlebot" in combined
        assert "bingbot" in combined
