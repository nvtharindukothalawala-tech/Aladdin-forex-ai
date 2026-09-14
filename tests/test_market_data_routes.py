"""
test_market_data_routes.py

Tests for authenticated MT5 market-data API.

The MetaTrader 5 provider is mocked so these tests
can run safely in CI without an MT5 terminal.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from datetime import (
    datetime,
    timezone,
)
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.main import app

import app.api.routes.market_data_routes as market_data_routes


client = TestClient(app)


# ==========================================
# Authentication Helper
# ==========================================


def get_auth_headers():
    """
    Create a unique test user and return JWT headers.
    """

    unique_id = uuid4().hex[:8]

    username = f"marketdata_{unique_id}"
    email = f"{username}@email.com"
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

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


# ==========================================
# Fake MT5 Provider
# ==========================================


class FakeMT5Module:
    """
    Minimal MT5 timeframe constants required
    by the market-data route.
    """

    TIMEFRAME_M15 = 15
    TIMEFRAME_H1 = 60
    TIMEFRAME_H4 = 240


class FakeMT5DataProvider:
    """
    Fake read-only MT5 provider for route tests.
    """

    disconnected = False
    last_symbol = None
    last_timeframe = None
    last_count = None

    def _require_mt5(self):
        return FakeMT5Module

    def get_candles(
        self,
        symbol,
        timeframe,
        count=100,
    ):
        FakeMT5DataProvider.last_symbol = symbol
        FakeMT5DataProvider.last_timeframe = timeframe
        FakeMT5DataProvider.last_count = count

        candles = []

        for index in range(count):
            candles.append(
                SimpleNamespace(
                    symbol="EURUSD",
                    timestamp=datetime(
                        2026,
                        9,
                        14,
                        10,
                        0,
                        tzinfo=timezone.utc,
                    ),
                    open_price=1.1550 + (
                        index * 0.0001
                    ),
                    high_price=1.1560 + (
                        index * 0.0001
                    ),
                    low_price=1.1540 + (
                        index * 0.0001
                    ),
                    close_price=1.1555 + (
                        index * 0.0001
                    ),
                    volume=1000.0 + index,
                )
            )

        return candles

    def disconnect(self):
        FakeMT5DataProvider.disconnected = True


# ==========================================
# Authentication
# ==========================================


def test_market_data_requires_authentication():
    """
    Candle data must not be available
    without a valid JWT.
    """

    response = client.get(
        "/market-data/candles"
        "?symbol=EURUSD"
        "&timeframe=H1"
        "&count=50"
    )

    assert response.status_code == 401


# ==========================================
# Successful Candle Request
# ==========================================


def test_get_authenticated_market_candles(
    monkeypatch,
):
    """
    Authenticated users should receive
    normalized OHLC candle data.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeMT5DataProvider,
    )

    FakeMT5DataProvider.disconnected = False

    headers = get_auth_headers()

    response = client.get(
        "/market-data/candles"
        "?symbol=eur/usd"
        "&timeframe=h1"
        "&count=50",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "EURUSD"
    assert data["broker_symbol"] == "EURUSD"
    assert data["timeframe"] == "H1"
    assert data["count"] == 50

    assert len(data["candles"]) == 50

    first_candle = data["candles"][0]

    assert "time" in first_candle
    assert "open" in first_candle
    assert "high" in first_candle
    assert "low" in first_candle
    assert "close" in first_candle
    assert "volume" in first_candle

    assert (
        FakeMT5DataProvider.last_symbol
        == "EURUSD"
    )

    assert (
        FakeMT5DataProvider.last_timeframe
        == FakeMT5Module.TIMEFRAME_H1
    )

    assert FakeMT5DataProvider.last_count == 50

    assert FakeMT5DataProvider.disconnected is True


# ==========================================
# Timeframe Mapping
# ==========================================


def test_m15_timeframe_is_mapped_correctly(
    monkeypatch,
):
    """
    M15 should map to the MT5 M15 constant.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeMT5DataProvider,
    )

    headers = get_auth_headers()

    response = client.get(
        "/market-data/candles"
        "?symbol=EURUSD"
        "&timeframe=M15"
        "&count=50",
        headers=headers,
    )

    assert response.status_code == 200

    assert (
        FakeMT5DataProvider.last_timeframe
        == FakeMT5Module.TIMEFRAME_M15
    )


def test_h4_timeframe_is_mapped_correctly(
    monkeypatch,
):
    """
    H4 should map to the MT5 H4 constant.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeMT5DataProvider,
    )

    headers = get_auth_headers()

    response = client.get(
        "/market-data/candles"
        "?symbol=EURUSD"
        "&timeframe=H4"
        "&count=50",
        headers=headers,
    )

    assert response.status_code == 200

    assert (
        FakeMT5DataProvider.last_timeframe
        == FakeMT5Module.TIMEFRAME_H4
    )


# ==========================================
# Validation
# ==========================================


def test_market_data_rejects_unsupported_symbol(
    monkeypatch,
):
    """
    Symbols outside the official Aladdin
    symbol list should return HTTP 400.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeMT5DataProvider,
    )

    headers = get_auth_headers()

    response = client.get(
        "/market-data/candles"
        "?symbol=BTCUSD"
        "&timeframe=H1"
        "&count=50",
        headers=headers,
    )

    assert response.status_code == 400

    assert (
        "Unsupported Aladdin trading symbol"
        in response.json()["detail"]
    )


def test_market_data_rejects_unsupported_timeframe(
    monkeypatch,
):
    """
    Only M15, H1, and H4 are supported.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeMT5DataProvider,
    )

    headers = get_auth_headers()

    response = client.get(
        "/market-data/candles"
        "?symbol=EURUSD"
        "&timeframe=M5"
        "&count=50",
        headers=headers,
    )

    assert response.status_code == 400

    assert (
        "Supported timeframes are M15, H1, and H4"
        in response.json()["detail"]
    )


def test_market_data_rejects_count_below_minimum(
    monkeypatch,
):
    """
    FastAPI should reject candle counts below 50.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeMT5DataProvider,
    )

    headers = get_auth_headers()

    response = client.get(
        "/market-data/candles"
        "?symbol=EURUSD"
        "&timeframe=H1"
        "&count=49",
        headers=headers,
    )

    assert response.status_code == 422


def test_market_data_rejects_count_above_maximum(
    monkeypatch,
):
    """
    FastAPI should reject candle counts above 1000.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeMT5DataProvider,
    )

    headers = get_auth_headers()

    response = client.get(
        "/market-data/candles"
        "?symbol=EURUSD"
        "&timeframe=H1"
        "&count=1001",
        headers=headers,
    )

    assert response.status_code == 422


# ==========================================
# Provider Failure
# ==========================================


def test_market_data_returns_503_when_mt5_fails(
    monkeypatch,
):
    """
    MT5 runtime failures should be exposed
    as service-unavailable responses.
    """

    class FailingProvider(
        FakeMT5DataProvider
    ):
        def get_candles(
            self,
            symbol,
            timeframe,
            count=100,
        ):
            raise RuntimeError(
                "MT5 market data unavailable."
            )

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FailingProvider,
    )

    headers = get_auth_headers()

    response = client.get(
        "/market-data/candles"
        "?symbol=EURUSD"
        "&timeframe=H1"
        "&count=50",
        headers=headers,
    )

    assert response.status_code == 503

    assert (
        response.json()["detail"]
        == "MT5 market data unavailable."
    )