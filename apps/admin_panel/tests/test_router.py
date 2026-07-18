import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from apps.main import app


@pytest.fixture(autouse=True)
def mock_admin_dependency(monkeypatch):
    async def fake_get_current_active_superuser():
        class Dummy:
            id = 1
            email = "admin@example.com"
            is_superuser = True
            is_active = True
        return Dummy()

    async def fake_get_admin_service():
        class DummyService:
            async def get_dashboard_summary(self):
                return {
                    "user_count": 1,
                    "active_user_count": 1,
                    "superuser_count": 1,
                    "total_settings": 0,
                    "total_audit_logs": 0,
                    "total_reports": 0,
                }

            async def get_system_settings(self, limit: int = 100, offset: int = 0):
                return []

            async def upsert_system_setting(self, key, value=None, description=None, is_active=None):
                class Setting:
                    id = 1
                    key = key
                    value = value or ""
                    description = description or ""
                    is_active = is_active if is_active is not None else True
                    created_at = "2026-01-01T00:00:00"
                    updated_at = "2026-01-01T00:00:00"
                return Setting()

            async def list_audit_logs(self, event_type=None, limit=100, offset=0):
                return []

            async def list_system_reports(self, limit=100, offset=0):
                return []

        return DummyService()

    monkeypatch.setattr("apps.admin_panel.router.get_current_active_superuser", fake_get_current_active_superuser)
    monkeypatch.setattr("apps.admin_panel.router.get_admin_service", fake_get_admin_service)


def test_admin_dashboard_returns_summary():
    client = TestClient(app)
    response = client.get("/api/v1/admin/")
    assert response.status_code == 200
    assert response.json()["user_count"] == 1


def test_admin_settings_empty_list():
    client = TestClient(app)
    response = client.get("/api/v1/admin/settings")
    assert response.status_code == 200
    assert response.json() == []
