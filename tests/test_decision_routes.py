"""
test_decision_routes.py

Tests for decision API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient


from app.api.main import app

client = TestClient(app)


def test_decision_api_buy():

    response = client.post(
        "/decision/analyze",
        json={
            "trend": "Bullish",
            "momentum": "Positive",
            "risk_reward": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["action"] == "BUY"

    assert data["confidence"] == 75
