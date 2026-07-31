"""
test_execution_history.py

Tests execution history API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient


from app.api.main import app

client = TestClient(app)


def test_get_execution_history():

    response = client.get("/execution/history/1")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        list,
    )
