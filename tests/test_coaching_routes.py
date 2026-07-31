"""
test_coaching_routes.py

Tests AI coaching API with JWT authentication.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient


from app.api.main import app

client = TestClient(app)


def get_auth_headers():
    """
    Create user and return JWT authorization headers.
    """

    client.post(
        "/auth/register",
        json={
            "username": "coachinguser",
            "email": "coaching@email.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "coachinguser",
            "password": "password123",
        },
    )

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_get_coaching_report():
    """
    Test protected AI coaching endpoint.
    """

    headers = get_auth_headers()

    response = client.get(
        "/coaching/report",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data

    assert "strengths" in data

    assert "weaknesses" in data

    assert "recommendations" in data
