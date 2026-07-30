"""
test_risk_routes.py

Contains API tests for Risk Management endpoints.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient

from app.api.main import app

# Create test client
client = TestClient(app)


# ==========================================
# Risk Calculate API Test
# ==========================================


def test_calculate_risk_api():
    """
    Test risk amount calculation endpoint.
    """

    response = client.post(
        "/risk/calculate",
        json={
            "account_balance": 10000,
            "risk_percent": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_amount"] == 200


# ==========================================
# Forex Lot Size API Test
# ==========================================


def test_calculate_lot_size_api():
    """
    Test Forex lot size endpoint.
    """

    response = client.post(
        "/risk/lot-size",
        json={
            "risk_amount": 200,
            "stop_loss_pips": 20,
            "pip_value": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["lot_size"] == 1.0


# ==========================================
# Risk Reward API Test
# ==========================================


def test_calculate_risk_reward_api():
    """
    Test risk reward calculation endpoint.
    """

    response = client.post(
        "/risk/risk-reward",
        json={
            "entry_price": 1.1000,
            "stop_loss": 1.0980,
            "take_profit": 1.1060,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_reward_ratio"] == 3.0
