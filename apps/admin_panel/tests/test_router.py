"""
Real tests for Admin Panel Router.
Tests use mocked dependencies via app.dependency_overrides.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from apps.admin_panel.router import get_admin_service
from apps.main import app
from apps.users.dependencies import get_current_active_superuser

# ==========================================
# Shared Test Data
# ==========================================

MOCK_DASHBOARD = {
    "user_count": 42,
    "active_user_count": 38,
    "superuser_count": 3,
    "total_settings": 15,
    "total_audit_logs": 1280,
    "total_reports": 7,
}

MOCK_SETTINGS = [
    type(
        "AdminSetting",
        (),
        {
            "id": 1,
            "key": "site_name",
            "value": "Econojin",
            "description": "Site name",
            "is_active": True,
            "created_at": datetime(2025, 1, 1, tzinfo=UTC),
            "updated_at": datetime(2025, 1, 1, tzinfo=UTC),
            "__repr__": lambda s: f"<AdminSetting(key={s.key})>",
        },
    )(),
    type(
        "AdminSetting",
        (),
        {
            "id": 2,
            "key": "max_users",
            "value": "10000",
            "description": "Max registered users",
            "is_active": True,
            "created_at": datetime(2025, 1, 2, tzinfo=UTC),
            "updated_at": datetime(2025, 1, 2, tzinfo=UTC),
            "__repr__": lambda s: f"<AdminSetting(key={s.key})>",
        },
    )(),
]

MOCK_USERS = [
    type(
        "User",
        (),
        {
            "id": 1,
            "email": "admin@example.com",
            "full_name": "Admin User",
            "phone": "+1234567890",
            "organization": "Econojin",
            "role": "admin",
            "is_active": True,
            "is_superuser": True,
            "created_at": datetime(2025, 1, 1, tzinfo=UTC),
            "updated_at": datetime(2025, 1, 1, tzinfo=UTC),
            "__repr__": lambda s: f"<User(id={s.id})>",
        },
    )(),
    type(
        "User",
        (),
        {
            "id": 2,
            "email": "user@example.com",
            "full_name": "Regular User",
            "phone": None,
            "organization": None,
            "role": "farmer",
            "is_active": True,
            "is_superuser": False,
            "created_at": datetime(2025, 1, 2, tzinfo=UTC),
            "updated_at": datetime(2025, 1, 2, tzinfo=UTC),
            "__repr__": lambda s: f"<User(id={s.id})>",
        },
    )(),
    type(
        "User",
        (),
        {
            "id": 3,
            "email": "inactive@example.com",
            "full_name": "Inactive User",
            "phone": None,
            "organization": None,
            "role": "farmer",
            "is_active": False,
            "is_superuser": False,
            "created_at": datetime(2025, 1, 3, tzinfo=UTC),
            "updated_at": datetime(2025, 1, 3, tzinfo=UTC),
            "__repr__": lambda s: f"<User(id={s.id})>",
        },
    )(),
]

MOCK_AUDIT_LOGS = [
    type(
        "AuditLog",
        (),
        {
            "id": 1,
            "actor_id": 1,
            "actor_email": "admin@example.com",
            "event_type": "login",
            "event_data": '{"ip": "127.0.0.1"}',
            "created_at": datetime(2025, 1, 1, 10, 0, 0, tzinfo=UTC),
            "__repr__": lambda s: f"<AuditLog(id={s.id})>",
        },
    )(),
    type(
        "AuditLog",
        (),
        {
            "id": 2,
            "actor_id": 2,
            "actor_email": "user@example.com",
            "event_type": "login",
            "event_data": '{"ip": "127.0.0.2"}',
            "created_at": datetime(2025, 1, 1, 11, 0, 0, tzinfo=UTC),
            "__repr__": lambda s: f"<AuditLog(id={s.id})>",
        },
    )(),
]

MOCK_REPORTS = [
    type(
        "SystemReport",
        (),
        {
            "id": 1,
            "report_name": "Weekly Performance",
            "status": "completed",
            "report_data": '{"avg_response": 120}',
            "created_at": datetime(2025, 1, 1, tzinfo=UTC),
            "completed_at": datetime(2025, 1, 1, 1, 0, 0, tzinfo=UTC),
            "__repr__": lambda s: f"<SystemReport(id={s.id})>",
        },
    )(),
]


# ==========================================
# Mock Service Factory
# ==========================================


def create_mock_admin_service():
    """Create a mock AdminService for testing."""
    mock = AsyncMock()

    mock.get_dashboard_summary.return_value = MOCK_DASHBOARD
    mock.get_system_settings.return_value = MOCK_SETTINGS
    mock.upsert_system_setting.return_value = type(
        "AdminSetting",
        (),
        {
            "id": 1,
            "key": "test_key",
            "value": "test_value",
            "description": "Test setting",
            "is_active": True,
            "created_at": datetime(2025, 1, 1, tzinfo=UTC),
            "updated_at": datetime(2025, 1, 1, tzinfo=UTC),
        },
    )()
    mock.list_audit_logs.return_value = MOCK_AUDIT_LOGS
    mock.record_audit_event.return_value = MOCK_AUDIT_LOGS[0]
    mock.list_system_reports.return_value = MOCK_REPORTS
    mock.create_system_report.return_value = type(
        "SystemReport",
        (),
        {
            "id": 3,
            "report_name": "Test Report",
            "status": "completed",
            "report_data": "Report generated",
            "created_at": datetime(2025, 1, 1, tzinfo=UTC),
            "completed_at": datetime(2025, 1, 1, 1, 0, 0, tzinfo=UTC),
            "__repr__": lambda s: f"<SystemReport(id={s.id})>",
        },
    )()
    mock.list_users.return_value = MOCK_USERS
    mock.get_user_detail.return_value = MOCK_USERS[0]
    mock.update_user_status.return_value = type(
        "User",
        (),
        {
            "id": 2,
            "email": "user@example.com",
            "full_name": "Regular User",
            "phone": None,
            "organization": None,
            "role": "farmer",
            "is_active": False,
            "is_superuser": False,
            "created_at": datetime(2025, 1, 1, tzinfo=UTC),
            "updated_at": datetime(2025, 1, 1, tzinfo=UTC),
        },
    )()
    mock.update_user_role.return_value = type(
        "User",
        (),
        {
            "id": 2,
            "email": "user@example.com",
            "full_name": "Regular User",
            "phone": None,
            "organization": None,
            "role": "farmer",
            "is_active": True,
            "is_superuser": True,
            "created_at": datetime(2025, 1, 1, tzinfo=UTC),
            "updated_at": datetime(2025, 1, 1, tzinfo=UTC),
        },
    )()
    mock.delete_user.return_value = True
    mock.get_system_health.return_value = {
        "database": "healthy",
        "database_latency_ms": 1.23,
        "redis": "not_configured",
        "redis_latency_ms": None,
        "uptime_seconds": 3600,
        "total_users": 42,
        "active_users_last_24h": 5,
        "total_api_routes": 15,
        "environment": "test",
        "python_version": "3.12",
    }

    return mock


# ==========================================
# Fixtures
# ==========================================


@pytest.fixture(autouse=True)
def override_deps():
    """Override FastAPI dependencies for all tests."""
    mock_service = create_mock_admin_service()

    async def fake_superuser():
        return type(
            "User",
            (),
            {
                "id": 1,
                "email": "admin@example.com",
                "is_superuser": True,
                "is_active": True,
            },
        )()

    async def fake_get_admin_service():
        return mock_service

    app.dependency_overrides[get_current_active_superuser] = fake_superuser
    app.dependency_overrides[get_admin_service] = fake_get_admin_service

    yield mock_service

    app.dependency_overrides.clear()


# ==========================================
# Test Client
# ==========================================

client = TestClient(app)


class TestAdminDashboard:
    """Tests for GET /api/v1/admin/"""

    def test_dashboard_returns_summary(self):
        response = client.get("/api/v1/admin/")
        assert response.status_code == 200
        data = response.json()
        assert data["user_count"] == 42
        assert data["active_user_count"] == 38
        assert data["superuser_count"] == 3
        assert data["total_settings"] == 15
        assert data["total_audit_logs"] == 1280
        assert data["total_reports"] == 7

    def test_dashboard_has_all_required_fields(self):
        response = client.get("/api/v1/admin/")
        assert response.status_code == 200
        required_fields = [
            "user_count",
            "active_user_count",
            "superuser_count",
            "total_settings",
            "total_audit_logs",
            "total_reports",
        ]
        for field in required_fields:
            assert field in response.json(), f"Missing field: {field}"


class TestAdminSettings:
    """Tests for GET/PUT /api/v1/admin/settings"""

    def test_list_settings(self):
        response = client.get("/api/v1/admin/settings")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["key"] == "site_name"
        assert data[0]["value"] == "Econojin"

    def test_list_settings_with_pagination(self):
        response = client.get("/api/v1/admin/settings?limit=10&offset=0")
        assert response.status_code == 200

    def test_upsert_setting(self, override_deps):
        mock_service = override_deps
        mock_service.upsert_system_setting.return_value = type(
            "AdminSetting",
            (),
            {
                "id": 1,
                "key": "test_key",
                "value": "new_value",
                "description": "Updated",
                "is_active": True,
                "created_at": datetime(2025, 1, 1, tzinfo=UTC),
                "updated_at": datetime(2025, 1, 2, tzinfo=UTC),
            },
        )()
        response = client.put("/api/v1/admin/settings/test_key", json={"value": "new_value"})
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == "new_value"

    def test_upsert_setting_empty_payload_fails(self):
        response = client.put("/api/v1/admin/settings/test_key", json={})
        assert response.status_code == 400
        assert "required" in response.json()["detail"].lower()


class TestAdminUsers:
    """Tests for GET/PATCH/DELETE /api/v1/admin/users"""

    def test_list_users(self):
        response = client.get("/api/v1/admin/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["email"] == "admin@example.com"

    def test_list_users_with_search(self):
        response = client.get("/api/v1/admin/users?search=admin")
        assert response.status_code == 200

    def test_list_users_filter_active(self):
        response = client.get("/api/v1/admin/users?is_active=true")
        assert response.status_code == 200

    def test_list_users_filter_role(self):
        response = client.get("/api/v1/admin/users?role=farmer")
        assert response.status_code == 200

    def test_get_user_detail(self):
        response = client.get("/api/v1/admin/users/1")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@example.com"
        assert data["full_name"] == "Admin User"

    def test_get_user_detail_not_found(self, override_deps):
        override_deps.get_user_detail.return_value = None
        response = client.get("/api/v1/admin/users/999")
        assert response.status_code == 404

    def test_update_user_status(self, override_deps):
        override_deps.update_user_status.return_value = type(
            "User",
            (),
            {
                "id": 2,
                "email": "user@example.com",
                "full_name": "Regular User",
                "phone": None,
                "organization": None,
                "role": "farmer",
                "is_active": False,
                "is_superuser": False,
                "created_at": datetime(2025, 1, 1, tzinfo=UTC),
                "updated_at": datetime(2025, 1, 1, tzinfo=UTC),
            },
        )()
        response = client.patch("/api/v1/admin/users/2/status", json={"is_active": False})
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_update_user_status_not_found(self, override_deps):
        override_deps.update_user_status.return_value = None
        response = client.patch("/api/v1/admin/users/999/status", json={"is_active": False})
        assert response.status_code == 404

    def test_update_user_role(self, override_deps):
        override_deps.update_user_role.return_value = type(
            "User",
            (),
            {
                "id": 2,
                "email": "user@example.com",
                "full_name": "Regular User",
                "phone": None,
                "organization": None,
                "role": "farmer",
                "is_active": True,
                "is_superuser": True,
                "created_at": datetime(2025, 1, 1, tzinfo=UTC),
                "updated_at": datetime(2025, 1, 1, tzinfo=UTC),
            },
        )()
        response = client.patch("/api/v1/admin/users/2/role", json={"is_superuser": True})
        assert response.status_code == 200
        assert response.json()["is_superuser"] is True

    def test_delete_user(self):
        response = client.delete("/api/v1/admin/users/2")
        assert response.status_code == 204

    def test_delete_user_not_found(self, override_deps):
        override_deps.delete_user.return_value = False
        response = client.delete("/api/v1/admin/users/999")
        assert response.status_code == 404

    def test_delete_self_returns_400(self):
        response = client.delete("/api/v1/admin/users/1")
        assert response.status_code == 400
        assert "cannot delete yourself" in response.json()["detail"].lower()

    def test_status_update_self_deactivate_returns_400(self):
        response = client.patch("/api/v1/admin/users/1/status", json={"is_active": False})
        assert response.status_code == 400
        assert "cannot deactivate yourself" in response.json()["detail"].lower()


class TestAdminAuditLogs:
    """Tests for GET /api/v1/admin/audit-logs"""

    def test_list_audit_logs(self):
        response = client.get("/api/v1/admin/audit-logs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["event_type"] == "login"

    def test_audit_logs_filter_by_event_type(self):
        response = client.get("/api/v1/admin/audit-logs?event_type=login")
        assert response.status_code == 200

    def test_audit_logs_filter_by_actor_email(self):
        response = client.get("/api/v1/admin/audit-logs?actor_email=admin@example.com")
        assert response.status_code == 200

    def test_audit_logs_with_pagination(self):
        response = client.get("/api/v1/admin/audit-logs?limit=10&offset=0")
        assert response.status_code == 200


class TestAdminReports:
    """Tests for GET/POST /api/v1/admin/reports"""

    def test_list_reports(self):
        response = client.get("/api/v1/admin/reports")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["report_name"] == "Weekly Performance"

    def test_list_reports_with_pagination(self):
        response = client.get("/api/v1/admin/reports?limit=10&offset=0")
        assert response.status_code == 200

    def test_generate_report(self):
        response = client.post(
            "/api/v1/admin/reports", json={"report_name": "Test Report", "report_type": "csv"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["report_name"] == "Test Report"
        assert data["status"] == "completed"
        assert "successfully" in data["message"]

    def test_generate_report_invalid_type(self):
        response = client.post(
            "/api/v1/admin/reports", json={"report_name": "Test", "report_type": "pdf"}
        )
        assert response.status_code == 422


class TestSystemHealth:
    """Tests for GET /api/v1/admin/health"""

    def test_health_endpoint(self):
        response = client.get("/api/v1/admin/health")
        assert response.status_code == 200
        data = response.json()
        assert data["database"] == "healthy"
        assert data["database_latency_ms"] == 1.23
        assert data["redis"] == "not_configured"
        assert "total_users" in data
        assert "environment" in data
        assert "python_version" in data

    def test_health_has_all_required_fields(self):
        response = client.get("/api/v1/admin/health")
        assert response.status_code == 200
        required = [
            "database",
            "database_latency_ms",
            "redis",
            "uptime_seconds",
            "total_users",
            "active_users_last_24h",
            "total_api_routes",
            "environment",
            "python_version",
        ]
        for field in required:
            assert field in response.json(), f"Missing field: {field}"
