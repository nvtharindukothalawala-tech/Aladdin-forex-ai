"""
test_execution_routes.py

Tests execution API endpoint.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient


from app.api.main import app

client = TestClient(app)


def test_execute_trade_api():

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "EUR/USD"

    assert data["direction"] == "BUY"

    assert data["volume"] == 0.10

    assert data["status"] == "EXECUTED"

    assert data["broker_order_id"] == "MOCK_ORDER_001"
