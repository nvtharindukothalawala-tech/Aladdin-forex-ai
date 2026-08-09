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
    """
    Test successful approved trade execution.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.10,
            "approved": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "EUR/USD"

    assert data["direction"] == "BUY"

    assert data["volume"] == 0.10

    assert data["status"] == "EXECUTED"

    assert data["broker_order_id"] == "MOCK_ORDER_001"


def test_execution_api_rejects_unapproved_trade():
    """
    Test that execution API cannot
    execute an unapproved trade.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.10,
            "approved": False,
        },
    )

    assert response.status_code == 403

def test_ai_execution_api_runs_server_side_approval_workflow():
    """
    Test that AI execution uses Aladdin's
    internal analysis and approval workflow.
    """

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"]["action"] == "BUY"

    assert data["approval"]["approved"] is True

    assert data["execution_result"]["status"] == "EXECUTED"