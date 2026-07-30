"""
test_trading_routes.py

Tests trading workflow API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient


from app.api.main import app

client = TestClient(app)


def test_trading_workflow_api():

    response = client.post(
        "/trading/analyze",
        json={
            "symbol": "EUR/USD",
            "trend": "Bullish",
            "momentum": "Positive",
            "risk_reward": 3,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1100,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"]["action"] == "BUY"

    assert data["trade_plan"]["direction"] == "BUY"
