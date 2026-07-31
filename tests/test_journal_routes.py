"""
test_journal_routes.py

Tests journal API with JWT authentication.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient


from app.api.main import app

client = TestClient(app)


def get_auth_headers():
    """
    Create user and return JWT authorization header.
    """

    client.post(
        "/auth/register",
        json={
            "username": "journaluser",
            "email": "journal@email.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "journaluser",
            "password": "password123",
        },
    )

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_get_journal_count():

    headers = get_auth_headers()

    response = client.get(
        "/journal/count",
        headers=headers,
    )

    assert response.status_code == 200

    assert "total_trades" in response.json()


def test_get_journal_trades():

    headers = get_auth_headers()

    response = client.get(
        "/journal/trades",
        headers=headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )
