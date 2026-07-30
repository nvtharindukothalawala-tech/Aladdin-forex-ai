"""
test_auth_routes.py

Tests authentication APIs.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient


from app.api.main import app

client = TestClient(app)


def test_register_user():

    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@email.com",
            "password": "password123",
        },
    )

    assert response.status_code in [
        200,
        400,
    ]


def test_login_user():

    client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "email": "login@email.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "loginuser",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    assert "access_token" in response.json()
