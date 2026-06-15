"""Deployment Tests - Phase 13"""
import pytest
import requests


class TestProductionReadiness:
    def test_api_health_endpoint(self):
        try:
            response = requests.get('http://localhost:8000/health', timeout=5)
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("API not running")
    
    def test_all_pilots_accessible(self):
        pilots = [
            "dishmok", "behbahan", "rodbar_talesh", "snow_mountain",
            "ouarzazate", "wadi_rum", "sahel_senegal", "ethiopian_highlands",
            "rajasthan", "outback_australia", "atacama_chile", "mongolian_steppe"
        ]
        try:
            response = requests.get('http://localhost:8000/gateway/pilots', timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert len(data['pilots']) == 12
        except requests.exceptions.ConnectionError:
            pytest.skip("API not running")
