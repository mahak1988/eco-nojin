#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures
=========================================
Adapted from fastapi/full-stack-fastapi-template with async support.
Provides fixtures for database, authentication, and API testing.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import AsyncGenerator, Generator
from httpx import ASGITransport, AsyncClient

# ── Test Settings ──────────────────────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ── Database Fixtures ──────────────────────────────────────────
@pytest.fixture
def mock_db_session():
    """Mock database session for unit tests."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.refresh = AsyncMock()
    session.add = AsyncMock()
    session.add_all = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def mock_user():
    """Mock user object for testing."""
    user = MagicMock()
    user.id = 1
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.hashed_password = "$argon2id$v=19$m=102400,t=2,p=8$...hashed..."
    user.is_active = True
    user.is_superuser = False
    user.phone = "+989123456789"
    return user


@pytest.fixture
def mock_superuser():
    """Mock superuser object for testing."""
    user = MagicMock()
    user.id = 1
    user.email = "admin@econojin.com"
    user.full_name = "Admin User"
    user.hashed_password = "$argon2id$v=19$m=102400,t=2,p=8$...hashed..."
    user.is_active = True
    user.is_superuser = True
    return user


# ── Sample Data Fixtures ───────────────────────────────────────
@pytest.fixture
def sample_user_data():
    """Sample user creation data."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
        "phone": "+989123456789",
    }


@pytest.fixture
def sample_farmer_data():
    """Sample farmer creation data."""
    return {
        "name": "Mohammad Rezaei",
        "phone": "+989123456789",
        "village": "Qaleh Ganj",
        "province": "Kerman",
        "land_size_ha": 5.5,
        "crop_type": "wheat",
    }


@pytest.fixture
def sample_event_data():
    """Sample calendar event data."""
    return {
        "title": "آبیاری مزرعه",
        "description": "آبیاری قطره‌ای مزرعه گندم",
        "event_type": "irrigation",
        "start_date": "2026-07-20T06:00:00",
        "end_date": "2026-07-20T08:00:00",
    }


# ── API Client Fixtures ────────────────────────────────────────
@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for API testing."""
    from apps.main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def auth_headers(mock_user) -> dict:
    """Generate authorization headers for testing."""
    from apps.shared_core.security import create_access_token
    from datetime import timedelta
    
    token = create_access_token(
        subject=str(mock_user.id),
        expires_delta=timedelta(minutes=30),
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def superuser_headers(mock_superuser) -> dict:
    """Generate authorization headers for superuser testing."""
    from apps.shared_core.security import create_access_token
    from datetime import timedelta
    
    token = create_access_token(
        subject=str(mock_superuser.id),
        expires_delta=timedelta(minutes=30),
    )
    return {"Authorization": f"Bearer {token}"}


# ── Test Helpers ───────────────────────────────────────────────
@pytest.fixture
def assert_response_ok():
    """Helper to assert successful API response."""
    def _assert(response, expected_status: int = 200):
        assert response.status_code == expected_status, \
            f"Expected {expected_status}, got {response.status_code}: {response.text}"
    return _assert


@pytest.fixture
def assert_response_error():
    """Helper to assert error API response."""
    def _assert(response, expected_status: int = 422):
        assert response.status_code == expected_status, \
            f"Expected {expected_status}, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data or "error" in data
    return _assert