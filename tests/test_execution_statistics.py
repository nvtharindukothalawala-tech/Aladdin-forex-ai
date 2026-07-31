"""
test_execution_statistics.py

Tests execution statistics API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient


from app.api.main import app

client = TestClient(app)


def test_get_execution_statistics():

    response = client.get("/execution/statistics/1")

    assert response.status_code == 200

    data = response.json()

    assert "total_executions" in data

    assert "successful_executions" in data

    assert "failed_executions" in data

    assert "success_rate" in data

    assert isinstance(
        data["total_executions"],
        int,
    )

    assert isinstance(
        data["success_rate"],
        (int, float),
    )
