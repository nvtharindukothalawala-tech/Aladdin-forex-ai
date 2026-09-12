"""
test_performance_routes.py

Tests authenticated performance analytics API.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def get_auth_headers():
    """
    Create a test user and return JWT headers.
    """

    client.post(
        "/auth/register",
        json={
            "username": "performanceuser",
            "email": "performance@email.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "performanceuser",
            "password": "password123",
        },
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def test_get_authenticated_performance():
    """
    Authenticated users should receive
    journal-based performance analytics.
    """

    headers = get_auth_headers()

    response = client.get(
        "/performance/",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_trades" in data
    assert "winning_trades" in data
    assert "losing_trades" in data
    assert "win_rate" in data
    assert "total_profit" in data
    assert "average_risk_reward" in data


def test_performance_requires_authentication():
    """
    Performance analytics should not be
    available without authentication.
    """

    response = client.get(
        "/performance/",
    )

    assert response.status_code == 401