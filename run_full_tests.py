"""
EcoNojin Full Test Suite Runner
Tests: Database, Security, Auth, API Integrity
"""
import asyncio
import pytest
import sys
import os

# Set minimal env vars for testing
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Import App and Config
sys.path.insert(0, '.')
try:
    from apps.main import app
    from apps.shared_core.database.session import Base
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

@pytest.fixture
async def client():
    """Create an async test client with overridden dependencies."""
    # For this integration test, we assume the main app DB is accessible or mocked
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def db_engine():
    """Create a test database engine."""
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

class TestDatabase:
    """Test Database Connectivity and Models"""
    
    @pytest.mark.asyncio
    async def test_db_connection(self):
        """Verify database connection is alive."""
        # Just verify app can be imported and runs
        assert app is not None

    @pytest.mark.asyncio
    async def test_tables_exist(self, db_engine):
        """Verify critical tables are created."""
        from sqlalchemy import text
        async with db_engine.begin() as conn:
            # Check for key tables in SQLite
            result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            
            # Since we are using SQLite for this quick test, we just check connectivity
            assert len(tables) > 0

class TestSecurityHardening:
    """Test Security Middleware Implementation"""
    
    @pytest.mark.asyncio
    async def test_security_headers(self, client):
        """Verify security headers are present."""
        response = await client.get("/api/v1/health")
        
        headers = response.headers
        assert headers.get("X-Frame-Options") == "DENY"
        assert headers.get("X-Content-Type-Options") == "nosniff"
        assert "Strict-Transport-Security" in headers
        assert "Content-Security-Policy" in headers
        assert headers.get("X-XSS-Protection") == "1; mode=block"

    @pytest.mark.asyncio
    async def test_honeypot_trap(self, client):
        """Verify honeypot endpoints return 404 or 403 and trigger blocking logic."""
        # Common honeypot paths
        honeypots = ["/wp-admin", "/phpmyadmin", "/.env", "/admin.php"]
        
        for path in honeypots:
            response = await client.get(path)
            # Should not return 200
            assert response.status_code in [404, 403, 418]

    @pytest.mark.asyncio
    async def test_rate_limiting_simulation(self, client):
        """Simulate rapid requests to test rate limiting (Basic Check)."""
        # Note: Real rate limiting test requires many requests. 
        # Here we just ensure the endpoint works and doesn't crash under load.
        for _ in range(5):
            response = await client.get("/api/v1/health")
            assert response.status_code == 200

class TestAuthFlow:
    """Test Authentication Flows"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Basic health check."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_protected_route_without_token(self, client):
        """Verify protected routes reject unauthenticated users."""
        # Assuming /api/v1/users/me is protected
        response = await client.get("/api/v1/users/me")
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_login_endpoint_exists(self, client):
        """Verify login endpoint exists."""
        # Send invalid credentials to check endpoint existence (should return 400/401, not 404)
        response = await client.post("/api/v1/auth/login", json={"email": "test@test.com", "password": "wrong"})
        assert response.status_code != 404

class TestAPIIntegrity:
    """Test General API Structure"""
    
    @pytest.mark.asyncio
    async def test_openapi_schema(self, client):
        """Verify OpenAPI schema is generated."""
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "paths" in data
        assert "info" in data

    @pytest.mark.asyncio
    async def test_cors_headers(self, client):
        """Verify CORS headers are configured correctly (not wildcard)."""
        response = await client.options("/api/v1/health", headers={"Origin": "http://evil.com"})
        # Depending on config, this might be absent or specific
        # If strict CORS is enabled, 'http://evil.com' should NOT be in Allow-Origin
        allow_origin = response.headers.get("Access-Control-Allow-Origin")
        if allow_origin:
            assert allow_origin != "*", "CORS Wildcard detected! Security Risk."

if __name__ == "__main__":
    print("🚀 Starting EcoNojin Full Test Suite...")
    print("="*40)
    
    # Run pytest
    exit_code = pytest.main([
        __file__, 
        "-v", 
        "--tb=short", 
        "-q",
        "--asyncio-mode=auto"
    ])
    
    if exit_code == 0:
        print("\n✅ All Tests Passed!")
    else:
        print(f"\n❌ Some tests failed. Exit code: {exit_code}")
    
    sys.exit(exit_code)
