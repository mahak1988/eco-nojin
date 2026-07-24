"""
Tests for admin_panel module | تست‌های admin_panel
===============================================
Run with: pytest apps/admin_panel/tests/test_router.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

# Import app at module level
from apps.main import app


def create_mock_user():
    """Create a mock superuser object"""
    user = MagicMock()
    user.id = 1
    user.email = "admin@example.com"
    user.is_superuser = True
    user.is_active = True
    return user


def create_mock_admin_service():
    """Create a mock admin service"""
    service = MagicMock()
    service.get_dashboard_summary = AsyncMock(return_value={
        "user_count": 1,
        "active_user_count": 1,
        "superuser_count": 1,
        "total_settings": 0,
        "total_audit_logs": 0,
        "total_reports": 0,
    })
    service.get_system_settings = AsyncMock(return_value=[])
    service.upsert_system_setting = AsyncMock()
    service.list_audit_logs = AsyncMock(return_value=[])
    service.list_system_reports = AsyncMock(return_value=[])
    return service


def test_admin_dashboard_returns_summary():
    """Test admin dashboard endpoint returns summary data"""
    
    # Create mocks
    mock_user = create_mock_user()
    mock_service = create_mock_admin_service()
    
    # Override dependencies using app.dependency_overrides
    import apps.admin_panel.router as admin_router
    
    async def mock_get_current_active_superuser():
        return mock_user
    
    def mock_get_admin_service(session):
        return mock_service
    
    # Apply overrides - must override the actual dependencies used in routes
    app.dependency_overrides[admin_router.get_current_active_superuser] = mock_get_current_active_superuser
    app.dependency_overrides[admin_router.get_admin_service] = mock_get_admin_service
    
    try:
        client = TestClient(app)
        response = client.get("/api/v1/admin/")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
        data = response.json()
        assert data["user_count"] == 1
        assert data["active_user_count"] == 1
        assert data["superuser_count"] == 1
    finally:
        # Clean up overrides
        app.dependency_overrides.clear()


def test_admin_settings_empty_list():
    """Test admin settings endpoint returns empty list"""
    
    # Create mocks
    mock_user = create_mock_user()
    mock_service = create_mock_admin_service()
    
    # Override dependencies using app.dependency_overrides
    import apps.admin_panel.router as admin_router
    
    async def mock_get_current_active_superuser():
        return mock_user
    
    def mock_get_admin_service(session):
        return mock_service
    
    # Apply overrides
    app.dependency_overrides[admin_router.get_current_active_superuser] = mock_get_current_active_superuser
    app.dependency_overrides[admin_router.get_admin_service] = mock_get_admin_service
    
    try:
        client = TestClient(app)
        response = client.get("/api/v1/admin/settings")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
        assert response.json() == []
    finally:
        # Clean up overrides
        app.dependency_overrides.clear()
