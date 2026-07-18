"""
Tests for Accounting, Alerts, and Agriculture Schools API routes
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from apps.main import app

client = TestClient(app)


class TestAccountingAPI:
    def test_list_transactions(self):
        response = client.get("/api/accounting/transactions")
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert "total" in data

    def test_list_transactions_with_type_filter(self):
        response = client.get("/api/accounting/transactions?type=income")
        assert response.status_code == 200
        data = response.json()
        for tx in data["transactions"]:
            assert tx["type"] == "income"

    def test_get_summary(self):
        response = client.get("/api/accounting/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "net_profit" in data

    def test_get_invoices(self):
        response = client.get("/api/accounting/invoices")
        assert response.status_code == 200
        assert "invoices" in response.json()

    def test_get_ledger(self):
        response = client.get("/api/accounting/ledger")
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data


class TestAlertsAPI:
    def test_list_alerts(self):
        response = client.get("/api/v1/alerts/")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert data["total"] > 0

    def test_active_alerts(self):
        response = client.get("/api/v1/alerts/active")
        assert response.status_code == 200
        for alert in response.json()["alerts"]:
            assert alert["acknowledged"] is False

    def test_critical_alerts(self):
        response = client.get("/api/v1/alerts/critical")
        assert response.status_code == 200
        for alert in response.json()["alerts"]:
            assert alert["severity"] == "critical"

    def test_acknowledge_alert(self):
        response = client.post("/api/v1/alerts/alert-002/acknowledge")
        assert response.status_code == 200
        assert response.json()["status"] == "acknowledged"

    def test_filter_by_severity(self):
        response = client.get("/api/v1/alerts/?severity=critical")
        assert response.status_code == 200
        for alert in response.json()["alerts"]:
            assert alert["severity"] == "critical"


class TestAgricultureSchoolsAPI:
    def test_list_schools(self):
        response = client.get("/api/v1/agriculture-schools/")
        assert response.status_code == 200
        data = response.json()
        assert "schools" in data
        assert data["total"] >= 5

    def test_search_schools(self):
        response = client.get("/api/v1/agriculture-schools/?search=%D8%AA%D9%87%D8%B1%D8%A7%D9%86")
        assert response.status_code == 200
        data = response.json()
        for school in data["schools"]:
            haystack = school["name"] + school.get("province", "")
            assert "تهران" in haystack

    def test_filter_by_type(self):
        response = client.get("/api/v1/agriculture-schools/?type=university")
        assert response.status_code == 200
        for school in response.json()["schools"]:
            assert school["type"] == "university"

    def test_stats(self):
        response = client.get("/api/v1/agriculture-schools/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_schools" in data
        assert "total_students" in data
        assert "by_type" in data
