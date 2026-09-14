"""
test_market_data_quote_resilience.py

Regression tests for partial MT5 Market Watch
quote availability.

These tests protect ALADDIN V2 against temporary
single-symbol quote failures.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.main import app

import app.api.routes.market_data_routes as market_data_routes


client = TestClient(app)


# ==========================================================
# AUTHENTICATION HELPER
# ==========================================================


def get_auth_headers():
    """
    Create a unique test user and return
    authenticated JWT headers.
    """

    unique_id = uuid4().hex[:8]

    username = (
        f"quote_resilience_{unique_id}"
    )

    email = (
        f"{username}@email.com"
    )

    password = "password123"

    register_response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()[
        "access_token"
    ]

    return {
        "Authorization": (
            f"Bearer {token}"
        ),
    }


# ==========================================================
# PARTIAL QUOTE PROVIDER
# ==========================================================


class PartialQuoteProvider:
    """
    Fake MT5 provider where seven symbols return
    valid quotes and XAUUSD temporarily fails.
    """

    disconnected = False

    def get_quote(
        self,
        symbol,
    ):
        """
        Return deterministic quote data.

        XAUUSD simulates a temporary invalid MT5 tick.
        """

        if symbol == "XAUUSD":
            raise RuntimeError(
                "Invalid MT5 bid/ask prices "
                "for XAUUSD."
            )

        if symbol == "USDJPY":

            return {
                "symbol": symbol,
                "broker_symbol": symbol,
                "bid": 154.857,
                "ask": 154.858,
                "spread": 0.001,
                "spread_points": 1.0,
                "digits": 3,
                "point": 0.001,
                "time": 1789402280,
            }

        return {
            "symbol": symbol,
            "broker_symbol": symbol,
            "bid": 1.15336,
            "ask": 1.15337,
            "spread": 0.00001,
            "spread_points": 1.0,
            "digits": 5,
            "point": 0.00001,
            "time": 1789402278,
        }

    def disconnect(
        self,
    ):
        """
        Record that the route closed the
        provider connection.
        """

        PartialQuoteProvider.disconnected = True


# ==========================================================
# PARTIAL MARKET WATCH AVAILABILITY
# ==========================================================


def test_market_watch_survives_single_symbol_failure(
    monkeypatch,
):
    """
    A temporary failure for one MT5 symbol must
    not make the complete Market Watch unavailable.

    Seven valid quotes should still be returned,
    while XAUUSD remains visible as unavailable.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        PartialQuoteProvider,
    )

    PartialQuoteProvider.disconnected = False

    headers = get_auth_headers()

    response = client.get(
        "/market-data/quotes",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 8

    assert (
        data["available_count"]
        == 7
    )

    assert (
        data["unavailable_count"]
        == 1
    )

    assert len(
        data["quotes"]
    ) == 8

    available_quotes = [
        quote
        for quote in data["quotes"]
        if quote["available"]
    ]

    unavailable_quotes = [
        quote
        for quote in data["quotes"]
        if not quote["available"]
    ]

    assert len(
        available_quotes
    ) == 7

    assert len(
        unavailable_quotes
    ) == 1

    gold_quote = (
        unavailable_quotes[0]
    )

    assert (
        gold_quote["symbol"]
        == "XAUUSD"
    )

    assert (
        gold_quote[
            "display_symbol"
        ]
        == "XAU/USD"
    )

    assert (
        gold_quote[
            "broker_symbol"
        ]
        is None
    )

    assert (
        gold_quote["bid"]
        is None
    )

    assert (
        gold_quote["ask"]
        is None
    )

    assert (
        gold_quote["spread"]
        is None
    )

    assert (
        gold_quote[
            "spread_points"
        ]
        is None
    )

    assert (
        gold_quote["digits"]
        is None
    )

    assert (
        gold_quote["point"]
        is None
    )

    assert (
        gold_quote["time"]
        is None
    )

    assert (
        gold_quote[
            "available"
        ]
        is False
    )

    assert (
        gold_quote["error"]
        == (
            "Invalid MT5 bid/ask prices "
            "for XAUUSD."
        )
    )

    eurusd_quote = next(
        quote
        for quote in data["quotes"]
        if quote["symbol"]
        == "EURUSD"
    )

    assert (
        eurusd_quote[
            "available"
        ]
        is True
    )

    assert (
        eurusd_quote["bid"]
        == 1.15336
    )

    assert (
        eurusd_quote["ask"]
        == 1.15337
    )

    assert (
        eurusd_quote["error"]
        is None
    )

    assert (
        PartialQuoteProvider.disconnected
        is True
    )