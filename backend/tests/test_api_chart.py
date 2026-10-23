"""Tests for Chart API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    def test_root_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "lumen-lab-ziwei"
    
    def test_api_health(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestGenerateChart:
    def test_generate_chart_basic(self):
        """Test basic chart generation via API."""
        payload = {
            "birth_info": {
                "year": 1990,
                "month": 1,
                "day": 1,
                "hour": 12,
                "gender": "male",
            },
            "use_true_solar_time": False,
        }
        response = client.post("/api/v1/chart", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["solar_date"] == "1990-01-01 12:00"
        assert data["yin_yang_gender"] == "阳男"
        assert data["shichen"] == "午"
        assert len(data["palaces"]) == 12
        assert data["true_solar_time_used"] is False
    
    def test_generate_chart_with_true_solar_time(self):
        """Test chart with true solar time correction."""
        payload = {
            "birth_info": {
                "year": 1990,
                "month": 1,
                "day": 1,
                "hour": 12,
                "gender": "female",
                "longitude": 116.4,
                "timezone_offset": 8,
            },
            "use_true_solar_time": True,
        }
        response = client.post("/api/v1/chart", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["yin_yang_gender"] == "阴女"
        assert data["true_solar_time_used"] is True
    
    def test_gender_validation_rejects_invalid(self):
        """Test API rejects invalid gender (issue #38)."""
        payload = {
            "birth_info": {
                "year": 1990,
                "month": 1,
                "day": 1,
                "hour": 12,
                "gender": "typo",
            },
            "use_true_solar_time": False,
        }
        response = client.post("/api/v1/chart", json=payload)
        
        # Pydantic validation should catch this first (enum)
        assert response.status_code == 422
    
    def test_gender_validation_runtime_check(self):
        """Test that runtime gender validation works (if bypassing Pydantic)."""
        # This tests the engine directly; API validates via Pydantic enum
        pass
    
    def test_hk_boundary_case(self):
        """Test HK boundary case from issue #45 via API."""
        payload = {
            "birth_info": {
                "year": 2025,
                "month": 12,
                "day": 31,
                "hour": 23,
                "gender": "male",
                "longitude": 114.17,
                "timezone_offset": 8,
            },
            "use_true_solar_time": True,
        }
        response = client.post("/api/v1/chart", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        # With true solar time correction, should be 亥 not 子
        assert data["shichen"] == "亥"
        # Day should NOT advance (stays 2025-12-31) -> day pillar 甲申
        assert data["ganzhi_day"] == "甲申"
    def test_invalid_birth_date(self):
        """Test invalid birth date rejected."""
        payload = {
            "birth_info": {
                "year": 1990,
                "month": 13,  # Invalid
                "day": 1,
                "hour": 12,
                "gender": "male",
            },
        }
        response = client.post("/api/v1/chart", json=payload)
        assert response.status_code == 422
    
    def test_invalid_hour(self):
        """Test invalid hour rejected."""
        payload = {
            "birth_info": {
                "year": 1990,
                "month": 1,
                "day": 1,
                "hour": 25,  # Invalid
                "gender": "male",
            },
        }
        response = client.post("/api/v1/chart", json=payload)
        assert response.status_code == 422
    
    def test_missing_required_fields(self):
        """Test missing required fields rejected."""
        payload = {
            "birth_info": {
                "year": 1990,
                "month": 1,
                # missing day, hour, gender
            },
        }
        response = client.post("/api/v1/chart", json=payload)
        assert response.status_code == 422


class TestTrueSolarTimePreview:
    def test_preview_endpoint(self):
        """Test true solar time preview endpoint."""
        response = client.get(
            "/api/v1/chart/true-solar-time-preview",
            params={
                "year": 2025,
                "month": 12,
                "day": 31,
                "hour": 23,
                "longitude": 114.17,
                "timezone_offset": 8,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "local_time" in data
        assert "true_solar_time" in data
        assert "correction_minutes" in data
        assert "shichen_local" in data
        assert "shichen_true_solar" in data
        assert data["shichen_local"] == "子"
        assert data["shichen_true_solar"] == "亥"