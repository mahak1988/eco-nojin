#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import AsyncGenerator


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def mock_user():
    """Mock user object"""
    user = MagicMock()
    user.id = 1
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.hashed_password = "hashed_password_here"
    user.is_active = True
    return user


@pytest.fixture
def sample_user_data():
    """Sample user creation data"""
    return {
        "email": "test@example.com",
        "password": "securepassword123",
        "full_name": "Test User"
    }
