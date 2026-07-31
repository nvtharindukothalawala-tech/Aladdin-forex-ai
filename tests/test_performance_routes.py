"""
test_performance_routes.py

Tests performance analytics API with JWT authentication.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient


from app.api.main import app

client = TestClient(app)


def get_auth_headers():
    """
    Create user and return JWT headers.
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

    return {"Authorization": f"Bearer {token}"}


def test_get_performance():

    headers = get_auth_headers()

    response = client.get(
        "/analytics/performance",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_trades" in data

    assert "winning_trades" in data

    assert "win_rate" in data

    assert "total_profit" in data
