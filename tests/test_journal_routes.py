"""
test_journal_routes.py

Tests journal API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient


from app.api.main import app

client = TestClient(app)


def test_get_journal_count():

    response = client.get("/journal/count")

    assert response.status_code == 200

    assert "total_trades" in response.json()


def test_get_journal_trades():

    response = client.get("/journal/trades")

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )
