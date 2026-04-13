"""
Integration Smoke Tests
Verify all API endpoints are reachable and return expected status codes.
Run against a live instance: pytest tests/integration/ -v
"""

import pytest

# These tests require a running instance with the env vars set
# pytest.ini or conftest.py should configure the base URL

BASE_URL = "http://localhost:8000/api/v1"


class TestHealthEndpoints:
    def test_health_check(self, client):
        resp = client.get(f"{BASE_URL}/health")
        assert resp.status_code == 200


class TestAuthFlow:
    def test_login_with_demo_credentials(self, client):
        resp = client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "demo@hexagon.com",
                "password": "Clarion2026!",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "user" in data

    def test_login_wrong_password(self, client):
        resp = client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "demo@hexagon.com",
                "password": "wrong",
            },
        )
        assert resp.status_code == 401

    def test_me_without_token(self, client):
        resp = client.get(f"{BASE_URL}/auth/me")
        assert resp.status_code == 401


class TestProtectedEndpoints:
    """Verify all protected endpoints return 401 without auth."""

    ENDPOINTS = [
        ("GET", "/analytics/dashboard"),
        ("GET", "/predictions"),
        ("GET", "/predictions/at-risk"),
        ("GET", "/notifications"),
        ("GET", "/notifications/unread"),
        ("GET", "/chatbot/history"),
        ("GET", "/chatbot/tools"),
        ("GET", "/help/sections"),
        ("GET", "/appearance/layouts"),
        ("GET", "/appearance/theme"),
        ("GET", "/preferences"),
    ]

    @pytest.mark.parametrize("method,path", ENDPOINTS)
    def test_requires_auth(self, client, method, path):
        if method == "GET":
            resp = client.get(f"{BASE_URL}{path}")
        else:
            resp = client.post(f"{BASE_URL}{path}")
        assert resp.status_code == 401, f"{method} {path} should require auth"


class TestAdminEndpoints:
    """Verify admin endpoints require admin role."""

    ADMIN_ENDPOINTS = [
        "/admin/users",
        "/admin/health",
        "/admin/audit",
        "/admin/config/branding",
        "/admin/config/features",
    ]

    @pytest.mark.parametrize("path", ADMIN_ENDPOINTS)
    def test_admin_requires_auth(self, client, path):
        resp = client.get(f"{BASE_URL}{path}")
        assert resp.status_code == 401
