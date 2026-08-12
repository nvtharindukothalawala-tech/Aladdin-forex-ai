"""
test_notification_count.py

Tests unread notification count API.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def get_auth_headers():
    """
    Create a user and return JWT authorization header.
    """

    client.post(
        "/auth/register",
        json={
            "username": "notificationcountuser",
            "email": "notificationcount@email.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "notificationcountuser",
            "password": "password123",
        },
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_get_unread_notification_count():

    headers = get_auth_headers()

    response = client.get(
        "/notifications/unread/count",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "unread_count" in data

    assert isinstance(
        data["unread_count"],
        int,
    )


def test_unread_notification_count_requires_authentication():

    response = client.get(
        "/notifications/unread/count"
    )

    assert response.status_code == 401