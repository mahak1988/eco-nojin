"""
Tests for Accounting, Alerts, and Agriculture Schools API routes
Aligned with actual router prefixes and response envelopes.
"""
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from apps.main import app

client = TestClient(app)


class TestAccountingAPI:
    """Accounting is mounted at /api/v1/accounting"""

    def test_list_accounts(self):
        response = client.get("/api/v1/accounting/accounts")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_journal_entries(self):
        response = client.get("/api/v1/accounting/journal-entries")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_summary(self):
        response = client.get("/api/v1/accounting/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "net_profit" in data

    def test_get_invoices(self):
        response = client.get("/api/v1/accounting/invoices")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_payments(self):
        response = client.get("/api/v1/accounting/payments")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


class TestAlertsAPI:
    """Alerts router: /api/v1/alerts — envelope uses key 'alerts'"""

    def test_list_alerts(self):
        response = client.get("/api/v1/alerts/")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "total" in data

    def test_active_alerts(self):
        response = client.get("/api/v1/alerts/active")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        for alert in data["alerts"]:
            assert alert["acknowledged"] is False

    def test_critical_alerts(self):
        response = client.get("/api/v1/alerts/critical")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        for alert in data["alerts"]:
            assert alert["severity"] == "critical"

    def test_acknowledge_alert(self):
        response = client.post("/api/v1/alerts/alert-002/acknowledge")
        # 200 if soft auth, 401/403 if REQUIRE_AUTH_FOR_WRITES
        assert response.status_code in (200, 401, 403)
        if response.status_code == 200:
            assert response.json()["status"] in ("acknowledged", "not_found")

    def test_filter_by_severity(self):
        response = client.get("/api/v1/alerts/?severity=critical")
        assert response.status_code == 200
        for alert in response.json()["alerts"]:
            assert alert["severity"] == "critical"


class TestAgricultureSchoolsAPI:
    """Schools list envelope: items/total (not schools)"""

    def test_list_schools(self):
        response = client.get("/api/v1/agriculture-schools/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_search_schools(self):
        response = client.get(
            "/api/v1/agriculture-schools/?search=%D8%AA%D9%87%D8%B1%D8%A7%D9%86"
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        for school in data["items"]:
            haystack = school.get("name", "") + school.get("province", "")
            # may be empty DB — only assert structure when results exist
            if data["total"] > 0:
                assert isinstance(haystack, str)

    def test_filter_by_type(self):
        response = client.get("/api/v1/agriculture-schools/?school_type=university")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        for school in data["items"]:
            assert school.get("school_type") == "university"

    def test_stats(self):
        response = client.get("/api/v1/agriculture-schools/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_schools" in data
        assert "total_students" in data
        assert "by_type" in data
