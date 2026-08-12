"""
test_notification_routes.py

Tests notification API with JWT authentication.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def get_auth_headers(
    username="notificationuser",
    email="notification@email.com",
):
    """
    Create a user and return JWT authorization header.
    """

    client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": "password123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_get_notifications():
    """
    Verify that an authenticated user can
    retrieve their notifications.
    """

    headers = get_auth_headers()

    response = client.get(
        "/notifications",
        headers=headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_get_unread_notifications():
    """
    Verify that an authenticated user can
    retrieve unread notifications.
    """

    headers = get_auth_headers(
        username="unreaduser",
        email="unread@email.com",
    )

    response = client.get(
        "/notifications/unread",
        headers=headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_notifications_require_authentication():
    """
    Verify that notifications cannot be accessed
    without authentication.
    """

    response = client.get(
        "/notifications",
    )

    assert response.status_code == 401


def test_unread_notifications_require_authentication():
    """
    Verify that unread notifications require authentication.
    """

    response = client.get(
        "/notifications/unread",
    )

    assert response.status_code == 401