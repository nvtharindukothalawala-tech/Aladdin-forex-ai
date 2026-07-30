"""
test_performance_routes.py

Tests performance API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient


from app.api.main import app

client = TestClient(app)


def test_get_performance():

    response = client.get("/analytics/performance")

    assert response.status_code == 200

    data = response.json()

    assert "total_trades" in data

    assert "win_rate" in data

    assert "total_profit" in data
