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
from app.market.indicators import TechnicalIndicators

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

    TIMEFRAME_M1 = 1
    TIMEFRAME_M5 = 5
    TIMEFRAME_M15 = 15
    TIMEFRAME_M30 = 30
    TIMEFRAME_H1 = 60
    TIMEFRAME_H4 = 240
    TIMEFRAME_D1 = 1440
    TIMEFRAME_W1 = 10080


class FakeMT5DataProvider:
    """
    Fake read-only MT5 provider for route tests.
    """

    disconnected = False

    last_symbol = None
    last_timeframe = None
    last_count = None

    quote_symbols = []

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

    def get_quote(
        self,
        symbol,
    ):
        """
        Return deterministic fake MT5 quote data.
        """

        FakeMT5DataProvider.quote_symbols.append(
            symbol
        )

        quote_map = {
            "EURUSD": {
                "broker_symbol": "EURUSD",
                "bid": 1.16050,
                "ask": 1.16062,
                "spread": 0.00012,
                "spread_points": 12.0,
                "digits": 5,
                "point": 0.00001,
                "time": 1789372800,
            },
            "GBPUSD": {
                "broker_symbol": "GBPUSD",
                "bid": 1.35010,
                "ask": 1.35024,
                "spread": 0.00014,
                "spread_points": 14.0,
                "digits": 5,
                "point": 0.00001,
                "time": 1789372801,
            },
            "AUDUSD": {
                "broker_symbol": "AUDUSD",
                "bid": 0.66510,
                "ask": 0.66522,
                "spread": 0.00012,
                "spread_points": 12.0,
                "digits": 5,
                "point": 0.00001,
                "time": 1789372802,
            },
            "NZDUSD": {
                "broker_symbol": "NZDUSD",
                "bid": 0.61510,
                "ask": 0.61523,
                "spread": 0.00013,
                "spread_points": 13.0,
                "digits": 5,
                "point": 0.00001,
                "time": 1789372803,
            },
            "USDCAD": {
                "broker_symbol": "USDCAD",
                "bid": 1.37510,
                "ask": 1.37525,
                "spread": 0.00015,
                "spread_points": 15.0,
                "digits": 5,
                "point": 0.00001,
                "time": 1789372804,
            },
            "USDCHF": {
                "broker_symbol": "USDCHF",
                "bid": 0.79510,
                "ask": 0.79523,
                "spread": 0.00013,
                "spread_points": 13.0,
                "digits": 5,
                "point": 0.00001,
                "time": 1789372805,
            },
            "USDJPY": {
                "broker_symbol": "USDJPY",
                "bid": 147.250,
                "ask": 147.263,
                "spread": 0.013,
                "spread_points": 13.0,
                "digits": 3,
                "point": 0.001,
                "time": 1789372806,
            },
            "XAUUSD": {
                "broker_symbol": "GOLD",
                "bid": 2500.10,
                "ask": 2500.35,
                "spread": 0.25,
                "spread_points": 25.0,
                "digits": 2,
                "point": 0.01,
                "time": 1789372807,
            },
        }

        values = quote_map[
            symbol
        ]

        return {
            "symbol": symbol,
            **values,
        }

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


def test_market_quotes_require_authentication():
    """
    Market Watch quotes must not be available
    without a valid JWT.
    """

    response = client.get(
        "/market-data/quotes"
    )

    assert response.status_code == 401


# ==========================================
# Successful Market Watch Request
# ==========================================


def test_get_authenticated_market_quotes(
    monkeypatch,
):
    """
    Authenticated users should receive
    all official ALADDIN Market Watch quotes.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeMT5DataProvider,
    )

    FakeMT5DataProvider.disconnected = False
    FakeMT5DataProvider.quote_symbols = []

    headers = get_auth_headers()

    response = client.get(
        "/market-data/quotes",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 8
    assert len(data["quotes"]) == 8

    symbols = [
        quote["symbol"]
        for quote in data["quotes"]
    ]

    assert symbols == [
        "EURUSD",
        "GBPUSD",
        "AUDUSD",
        "NZDUSD",
        "USDCAD",
        "USDCHF",
        "USDJPY",
        "XAUUSD",
    ]

    assert (
        FakeMT5DataProvider.quote_symbols
        == symbols
    )

    assert FakeMT5DataProvider.disconnected is True


def test_market_quotes_return_expected_fields(
    monkeypatch,
):
    """
    Market Watch quote objects should expose
    the complete frontend quote contract.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeMT5DataProvider,
    )

    headers = get_auth_headers()

    response = client.get(
        "/market-data/quotes",
        headers=headers,
    )

    assert response.status_code == 200

    quote = response.json()[
        "quotes"
    ][0]

    assert quote["symbol"] == "EURUSD"

    assert (
        quote["display_symbol"]
        == "EUR/USD"
    )

    assert (
        quote["broker_symbol"]
        == "EURUSD"
    )

    assert quote["bid"] == 1.16050
    assert quote["ask"] == 1.16062
    assert quote["spread"] == 0.00012

    assert (
        quote["spread_points"]
        == 12.0
    )

    assert quote["digits"] == 5
    assert quote["point"] == 0.00001
    assert quote["time"] == 1789372800


def test_market_quotes_preserve_broker_alias(
    monkeypatch,
):
    """
    Market Watch should preserve the actual
    broker symbol returned by MT5.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeMT5DataProvider,
    )

    headers = get_auth_headers()

    response = client.get(
        "/market-data/quotes",
        headers=headers,
    )

    assert response.status_code == 200

    gold_quote = response.json()[
        "quotes"
    ][-1]

    assert gold_quote["symbol"] == "XAUUSD"

    assert (
        gold_quote["display_symbol"]
        == "XAU/USD"
    )

    assert (
        gold_quote["broker_symbol"]
        == "GOLD"
    )

    assert gold_quote["digits"] == 2


# ==========================================
# Market Watch Provider Failure
# ==========================================


def test_market_quotes_return_503_when_mt5_fails(
    monkeypatch,
):
    """
    MT5 quote failures should return
    service-unavailable and still disconnect.
    """

    class FailingQuoteProvider(
        FakeMT5DataProvider
    ):
        def get_quote(
            self,
            symbol,
        ):
            raise RuntimeError(
                "MT5 quote data unavailable."
            )

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FailingQuoteProvider,
    )

    FakeMT5DataProvider.disconnected = False

    headers = get_auth_headers()

    response = client.get(
        "/market-data/quotes",
        headers=headers,
    )

    assert response.status_code == 503

    assert (
        response.json()["detail"]
        == "MT5 quote data unavailable."
    )

    assert FakeMT5DataProvider.disconnected is True


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


def test_additional_chart_timeframes_are_mapped_correctly(
    monkeypatch,
):
    """
    ALADDIN V2 chart-only timeframes should map
    to their corresponding MT5 constants.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeMT5DataProvider,
    )

    headers = get_auth_headers()

    cases = [
        (
            "M1",
            FakeMT5Module.TIMEFRAME_M1,
        ),
        (
            "M5",
            FakeMT5Module.TIMEFRAME_M5,
        ),
        (
            "M30",
            FakeMT5Module.TIMEFRAME_M30,
        ),
        (
            "D1",
            FakeMT5Module.TIMEFRAME_D1,
        ),
        (
            "W1",
            FakeMT5Module.TIMEFRAME_W1,
        ),
    ]

    for timeframe, expected_constant in cases:
        response = client.get(
            "/market-data/candles"
            f"?symbol=EURUSD"
            f"&timeframe={timeframe}"
            f"&count=50",
            headers=headers,
        )

        assert response.status_code == 200

        assert (
            FakeMT5DataProvider.last_timeframe
            == expected_constant
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
    Only the official ALADDIN V2 chart timeframes are supported.
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
        "&timeframe=M2"
        "&count=50",
        headers=headers,
    )

    assert response.status_code == 400

    assert (
        "Supported timeframes are M1, M5, M15, M30, H1, H4, D1, and W1"
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
    FastAPI should reject candle counts above 5000.
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
        "&count=5001",
        headers=headers,
    )

    assert response.status_code == 422


# ==========================================
# Candle Provider Failure
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
# ==========================================
# Chart Technical Indicators
# ==========================================


def test_market_candles_include_ema20_series(
    monkeypatch,
):
    """
    The candle response should include a backend-computed
    EMA20 series derived from the same MT5 candle dataset.
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
        "&count=50",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "indicators" in data
    assert "ema20" in data["indicators"]

    ema20 = data["indicators"]["ema20"]

    assert ema20["period"] == 20
    assert len(ema20["series"]) == 31

    assert (
        ema20["series"][0]["time"]
        == data["candles"][19]["time"]
    )

    assert (
        ema20["series"][-1]["time"]
        == data["candles"][-1]["time"]
    )

    expected_latest_ema = (
        TechnicalIndicators.calculate_ema(
            [
                candle["close"]
                for candle in data["candles"]
            ],
            20,
        )
    )

    assert (
        ema20["series"][-1]["value"]
        == expected_latest_ema
    )

