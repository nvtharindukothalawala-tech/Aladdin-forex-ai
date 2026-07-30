"""
test_analysis_routes.py

Tests for market analysis API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_market_analysis_api():

    response = client.post(
        "/analysis/market",
        json={
            "symbol": "EUR/USD",
            "current_price": 1.0850,
            "sma": 1.0800,
            "rsi": 60,
            "atr": 0.0015,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "EUR/USD"

    assert data["trend"] == "Bullish"

    assert data["momentum"] == "Positive"

    assert data["volatility"] == "Normal"
