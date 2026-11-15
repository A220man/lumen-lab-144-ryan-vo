"""Auth route tests for Keycloak OIDC demo mode."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


def test_auth_routes_import():
    """Test that auth routes can be imported."""
    from app.api.v1.auth_routes import router
    assert router is not None
    assert router.prefix == "/auth"


def test_auth_health_endpoint():
    """Test auth health check endpoint."""
    from app.main import app
    client = TestClient(app)
    response = client.get("/auth/auth/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "keycloak"


def test_auth_me_no_auth():
    """Test /auth/me returns 401 without auth cookie."""
    from app.main import app
    client = TestClient(app)
    response = client.get("/auth/auth/me")
    assert response.status_code == 401


def test_auth_routes_exist():
    """Test that all auth routes are registered."""
    from app.main import app
    client = TestClient(app)
    
    expected_routes = [
        "/auth/auth/login",
        "/auth/auth/callback",
        "/auth/auth/logout",
        "/auth/auth/logout-callback",
        "/auth/auth/me",
        "/auth/auth/health",
    ]
    
    for route_path in expected_routes:
        response = client.get(route_path)
        # Routes may return 404 if GET not supported, but should be registered
        assert any(
            r.path == route_path for r in app.routes
        ), f"Route {route_path} not registered"


def test_chart_route_still_works():
    """Test that chart API still works after auth integration."""
    from app.main import app
    client = TestClient(app)
    
    # Chart endpoint should still be accessible
    response = client.post(
        "/api/v1/chart",
        json={
            "birth_info": {
                "year": 1990,
                "month": 1,
                "day": 1,
                "hour": 12,
                "gender": "male",
                "longitude": 116.4,
                "latitude": 39.9,
                "timezone_offset": 8,
            },
            "use_true_solar_time": True,
        },
    )
    # Should not be blocked by auth (public endpoint)
    assert response.status_code in (200, 422)  # 422 = validation error, not auth error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
