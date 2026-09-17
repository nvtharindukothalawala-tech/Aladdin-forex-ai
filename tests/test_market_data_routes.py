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

def test_market_candles_include_rsi14_series(
    monkeypatch,
):
    """
    The candle response should include a backend-computed
    RSI14 series derived from the same MT5 candle dataset.

    The latest chart RSI must match ALADDIN's existing
    TechnicalIndicators RSI calculation.
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
    assert "rsi14" in data["indicators"]

    rsi14 = data["indicators"]["rsi14"]

    assert rsi14["period"] == 14

    # RSI14 requires 15 closing prices.
    # With 50 candles, indices 14..49 produce
    # 36 timestamp-aligned RSI points.
    assert len(rsi14["series"]) == 36

    assert (
        rsi14["series"][0]["time"]
        == data["candles"][14]["time"]
    )

    assert (
        rsi14["series"][-1]["time"]
        == data["candles"][-1]["time"]
    )

    expected_latest_rsi = (
        TechnicalIndicators.calculate_rsi(
            [
                candle["close"]
                for candle in data["candles"]
            ],
            14,
        )
    )

    assert (
        rsi14["series"][-1]["value"]
        == expected_latest_rsi
    )


def test_market_candles_include_adx14_series(
    monkeypatch,
):
    """
    The candle response should include a backend-computed
    ADX14 series derived from the same MT5 candle dataset.

    The latest chart ADX must match ALADDIN's existing
    TechnicalIndicators ADX calculation.
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
    assert "adx14" in data["indicators"]

    adx14 = data["indicators"]["adx14"]

    assert adx14["period"] == 14

    # Existing ALADDIN ADX14 requires at least
    # 28 candles. With 50 candles, indices
    # 27..49 produce 23 timestamp-aligned points.
    assert len(adx14["series"]) == 23

    assert (
        adx14["series"][0]["time"]
        == data["candles"][27]["time"]
    )

    assert (
        adx14["series"][-1]["time"]
        == data["candles"][-1]["time"]
    )

    candle_objects = (
        FakeMT5DataProvider()
        .get_candles(
            symbol="EURUSD",
            timeframe=FakeMT5Module.TIMEFRAME_H1,
            count=50,
        )
    )

    expected_latest_adx = (
        TechnicalIndicators.calculate_adx(
            candle_objects,
            14,
        )
    )

    assert (
        adx14["series"][-1]["value"]
        == expected_latest_adx
    )

# ==========================================
# Chart Market Structure
# ==========================================


class FakeStructureMT5DataProvider(
    FakeMT5DataProvider
):
    """
    Deterministic candle provider containing:

    - confirmed swing highs
    - confirmed swing lows
    - bullish BOS
    - bearish CHoCH

    Used only for market-structure route tests.
    """

    candle_fetch_count = 0

    def get_candles(
        self,
        symbol,
        timeframe,
        count=100,
    ):
        FakeStructureMT5DataProvider.candle_fetch_count += 1

        FakeMT5DataProvider.last_symbol = symbol
        FakeMT5DataProvider.last_timeframe = timeframe
        FakeMT5DataProvider.last_count = count

        base_time = datetime(
            2026,
            9,
            14,
            10,
            0,
            tzinfo=timezone.utc,
        )

        prices = [
            # open, high, low, close
            #
            # Index 2 becomes a confirmed swing high
            # at 1.1050.
            (1.1000, 1.1010, 1.0990, 1.1000),
            (1.1000, 1.1020, 1.0995, 1.1010),
            (1.1010, 1.1050, 1.1005, 1.1030),
            (1.1030, 1.1040, 1.1010, 1.1020),
            (1.1020, 1.1045, 1.1005, 1.1040),

            # Index 5 closes above the swing high.
            # This creates BOS_BULLISH.
            (1.1040, 1.1070, 1.1030, 1.1060),

            # Build a later confirmed swing low
            # at index 8 with price 1.1010.
            (1.1060, 1.1065, 1.1030, 1.1040),
            (1.1040, 1.1050, 1.1020, 1.1030),
            (1.1030, 1.1040, 1.1010, 1.1020),
            (1.1020, 1.1045, 1.1020, 1.1040),
            (1.1040, 1.1050, 1.1030, 1.1045),

            # Index 11 closes below the later
            # swing low, creating CHOCH_BEARISH.
            (1.1045, 1.1050, 1.0990, 1.1000),
        ]

        # Add neutral candles after the deterministic
        # structure sequence so the route receives the
        # requested minimum of 50 candles.
        while len(prices) < count:
            index = len(prices)

            prices.append(
                (
                    1.1000,
                    1.1008 + (index * 0.000001),
                    1.0995,
                    1.1000,
                )
            )

        candles = []

        for index, (
            open_price,
            high_price,
            low_price,
            close_price,
        ) in enumerate(prices[:count]):

            candles.append(
                SimpleNamespace(
                    symbol="EURUSD",
                    timestamp=(
                        base_time
                        + (
                            index
                            * (
                                datetime.resolution
                                * 3600000000
                            )
                        )
                    ),
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    volume=1000.0 + index,
                )
            )

        return candles


def test_market_candles_include_market_structure(
    monkeypatch,
):
    """
    The candle response should expose backend-computed
    market structure derived from the same candle dataset.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeStructureMT5DataProvider,
    )

    FakeStructureMT5DataProvider.candle_fetch_count = 0

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

    assert "market_structure" in data

    structure = data["market_structure"]

    assert "order_block" in structure

    order_block = structure["order_block"]

    if order_block is not None:
        assert set(order_block) == {
            "type",
            "candle_index",
            "high_price",
            "low_price",
            "open_price",
            "close_price",
            "time",
        }

        assert order_block["type"] in {
            "ORDER_BLOCK_BULLISH",
            "ORDER_BLOCK_BEARISH",
        }

        assert isinstance(
            order_block["candle_index"],
            int,
        )
        assert isinstance(
            order_block["high_price"],
            (int, float),
        )
        assert isinstance(
            order_block["low_price"],
            (int, float),
        )
        assert isinstance(
            order_block["open_price"],
            (int, float),
        )
        assert isinstance(
            order_block["close_price"],
            (int, float),
        )
        assert isinstance(
            order_block["time"],
            int,
        )

    assert "fvg" in structure

    fvg = structure["fvg"]

    if fvg is not None:
        assert set(fvg) == {
            "type",
            "start_index",
            "middle_index",
            "end_index",
            "lower_price",
            "upper_price",
            "time",
        }

        assert fvg["type"] in {
            "FVG_BULLISH",
            "FVG_BEARISH",
        }

        assert isinstance(fvg["start_index"], int)
        assert isinstance(fvg["middle_index"], int)
        assert isinstance(fvg["end_index"], int)
        assert isinstance(
            fvg["lower_price"],
            (int, float),
        )
        assert isinstance(
            fvg["upper_price"],
            (int, float),
        )
        assert isinstance(fvg["time"], int)

    assert "liquidity_sweep" in structure

    liquidity_sweep = structure["liquidity_sweep"]

    if liquidity_sweep is not None:
        assert set(liquidity_sweep) == {
            "type",
            "level_price",
            "swing_index",
            "sweep_index",
            "time",
        }

        assert liquidity_sweep["type"] in {
            "LIQUIDITY_SWEEP_HIGH",
            "LIQUIDITY_SWEEP_LOW",
        }

        assert isinstance(
            liquidity_sweep["level_price"],
            (int, float),
        )
        assert isinstance(
            liquidity_sweep["swing_index"],
            int,
        )
        assert isinstance(
            liquidity_sweep["sweep_index"],
            int,
        )
        assert isinstance(
            liquidity_sweep["time"],
            int,
        )

    assert structure["lookback"] == 2
    assert isinstance(
        structure["swing_highs"],
        list,
    )
    assert isinstance(
        structure["swing_lows"],
        list,
    )

    assert len(structure["swing_highs"]) > 0
    assert len(structure["swing_lows"]) > 0

    first_high = structure["swing_highs"][0]

    assert set(first_high) == {
        "index",
        "price",
        "time",
    }

    first_low = structure["swing_lows"][0]

    assert set(first_low) == {
        "index",
        "price",
        "time",
    }

    assert structure["bos"] is not None

    assert set(structure["bos"]) == {
        "type",
        "broken_price",
        "swing_index",
        "break_index",
        "time",
    }

    if structure["choch"] is not None:
        assert set(structure["choch"]) == {
            "type",
            "broken_price",
            "swing_index",
            "break_index",
            "time",
        }


def test_market_structure_reuses_single_candle_fetch(
    monkeypatch,
):
    """
    Market structure must reuse the candle dataset already
    fetched by the chart route and must not trigger another
    MT5 candle request.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeStructureMT5DataProvider,
    )

    FakeStructureMT5DataProvider.candle_fetch_count = 0

    headers = get_auth_headers()

    response = client.get(
        "/market-data/candles"
        "?symbol=EURUSD"
        "&timeframe=H1"
        "&count=50",
        headers=headers,
    )

    assert response.status_code == 200

    assert (
        FakeStructureMT5DataProvider.candle_fetch_count
        == 1
    )

def test_market_candles_include_support_resistance_zones(
    monkeypatch,
):
    """
    Market candle response must expose ATR-normalized
    support and resistance zone information.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeStructureMT5DataProvider,
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

    payload = response.json()

    assert "market_structure" in payload

    structure = payload["market_structure"]

    assert "support_resistance" in structure

    support_resistance = structure[
        "support_resistance"
    ]

    assert set(support_resistance) == {
        "atr_period",
        "tolerance_multiplier",
        "tolerance",
        "support_zones",
        "resistance_zones",
    }

    assert support_resistance["atr_period"] == 14

    assert (
        support_resistance["tolerance_multiplier"]
        == 0.25
    )

    assert isinstance(
        support_resistance["tolerance"],
        (int, float),
    )

    assert support_resistance["tolerance"] >= 0

    assert isinstance(
        support_resistance["support_zones"],
        list,
    )

    assert isinstance(
        support_resistance["resistance_zones"],
        list,
    )


def test_support_resistance_zone_response_shape(
    monkeypatch,
):
    """
    Any confirmed support or resistance zone returned
    by the API must use the stable chart contract.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeStructureMT5DataProvider,
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

    support_resistance = response.json()[
        "market_structure"
    ]["support_resistance"]

    zones = (
        support_resistance["support_zones"]
        + support_resistance["resistance_zones"]
    )

    for zone in zones:

        assert set(zone) == {
            "type",
            "lower_price",
            "upper_price",
            "center_price",
            "touch_count",
            "first_index",
            "last_index",
        }

        assert zone["type"] in {
            "SUPPORT",
            "RESISTANCE",
        }

        assert isinstance(
            zone["lower_price"],
            (int, float),
        )

        assert isinstance(
            zone["upper_price"],
            (int, float),
        )

        assert isinstance(
            zone["center_price"],
            (int, float),
        )

        assert isinstance(
            zone["touch_count"],
            int,
        )

        assert zone["touch_count"] >= 2

        assert isinstance(
            zone["first_index"],
            int,
        )

        assert isinstance(
            zone["last_index"],
            int,
        )

        assert (
            zone["lower_price"]
            <= zone["center_price"]
            <= zone["upper_price"]
        )

        assert (
            zone["first_index"]
            <= zone["last_index"]
        )

# ==========================================
# Market Bias API Integration
# ==========================================


def test_market_candles_include_market_bias(
    monkeypatch,
):
    """
    Market candle responses must expose the
    deterministic market-bias analysis.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeStructureMT5DataProvider,
    )

    FakeStructureMT5DataProvider.candle_fetch_count = 0

    headers = get_auth_headers()

    response = client.get(
        "/market-data/candles"
        "?symbol=EURUSD"
        "&timeframe=H1"
        "&count=100",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    # ------------------------------------------
    # Top-level market bias
    # ------------------------------------------

    assert "market_bias" in data

    market_bias = data["market_bias"]

    assert isinstance(
        market_bias,
        dict,
    )

    # ------------------------------------------
    # Required market-bias fields
    # ------------------------------------------

    assert "bias" in market_bias
    assert "score" in market_bias
    assert "confidence" in market_bias
    assert "bullish_score" in market_bias
    assert "bearish_score" in market_bias
    assert "reasons" in market_bias

    # ------------------------------------------
    # Bias value
    # ------------------------------------------

    assert market_bias["bias"] in {
        "BULLISH",
        "BEARISH",
        "NEUTRAL",
    }

    # ------------------------------------------
    # Numeric score fields
    # ------------------------------------------

    assert isinstance(
        market_bias["score"],
        (int, float),
    )

    assert isinstance(
        market_bias["confidence"],
        (int, float),
    )

    assert isinstance(
        market_bias["bullish_score"],
        (int, float),
    )

    assert isinstance(
        market_bias["bearish_score"],
        (int, float),
    )

    # Confidence must remain in percentage range.

    assert (
        0.0
        <= market_bias["confidence"]
        <= 100.0
    )

    # ------------------------------------------
    # Explanation reasons
    # ------------------------------------------

    assert isinstance(
        market_bias["reasons"],
        list,
    )

    for reason in market_bias["reasons"]:

        assert isinstance(
            reason,
            dict,
        )

        assert "source" in reason
        assert "direction" in reason
        assert "weight" in reason
        assert "message" in reason

        assert reason["direction"] in {
            "BULLISH",
            "BEARISH",
            "NEUTRAL",
        }

        assert isinstance(
            reason["weight"],
            (int, float),
        )

        assert isinstance(
            reason["message"],
            str,
        )


def test_market_bias_reuses_single_candle_fetch(
    monkeypatch,
):
    """
    Market bias must reuse the candle dataset
    already fetched by the chart route.

    It must not create an additional MT5 candle
    request.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeStructureMT5DataProvider,
    )

    FakeStructureMT5DataProvider.candle_fetch_count = 0

    headers = get_auth_headers()

    response = client.get(
        "/market-data/candles"
        "?symbol=EURUSD"
        "&timeframe=H1"
        "&count=100",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "market_bias" in data

    assert (
        FakeStructureMT5DataProvider.candle_fetch_count
        == 1
    )

# ==========================================
# Trade Setup API Integration
# ==========================================


def test_market_candles_include_trade_setup(
    monkeypatch,
):
    """
    Market candle responses must expose the
    deterministic Trade Setup analysis.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeStructureMT5DataProvider,
    )

    FakeStructureMT5DataProvider.candle_fetch_count = 0

    headers = get_auth_headers()

    response = client.get(
        "/market-data/candles"
        "?symbol=EURUSD"
        "&timeframe=H1"
        "&count=100",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "trade_setup" in data

    trade_setup = data["trade_setup"]

    assert isinstance(
        trade_setup,
        dict,
    )

    # ------------------------------------------
    # Required response fields
    # ------------------------------------------

    required_fields = {
        "status",
        "direction",
        "symbol",
        "timeframe",
        "current_price",
        "entry",
        "stop_loss",
        "targets",
        "risk_reward",
        "bias",
        "bias_strength",
        "confidence",
        "bias_score",
        "reasons",
        "invalidation",
        "engine",
    }

    assert required_fields.issubset(
        trade_setup.keys()
    )

    # ------------------------------------------
    # Core contract
    # ------------------------------------------

    assert trade_setup["status"] in {
        "TRADE",
        "WAIT",
    }

    assert trade_setup["symbol"] == "EURUSD"
    assert trade_setup["timeframe"] == "H1"

    assert trade_setup["engine"] == "DETERMINISTIC"

    assert isinstance(
        trade_setup["current_price"],
        (int, float),
    )

    assert isinstance(
        trade_setup["reasons"],
        list,
    )

    assert isinstance(
        trade_setup["invalidation"],
        str,
    )

    # ------------------------------------------
    # Market-bias propagation
    # ------------------------------------------

    market_bias = data["market_bias"]

    assert (
        trade_setup["bias"]
        == market_bias["bias"]
    )

    assert (
        trade_setup["confidence"]
        == market_bias["confidence"]
    )

    assert (
        trade_setup["bias_strength"]
        == market_bias["strength"]
    )

    assert (
        trade_setup["bias_score"]
        == market_bias["score"]
    )

    # ------------------------------------------
    # TRADE / WAIT specific contract
    # ------------------------------------------

    if trade_setup["status"] == "TRADE":

        assert trade_setup["direction"] in {
            "BUY",
            "SELL",
        }

        assert isinstance(
            trade_setup["entry"],
            dict,
        )

        assert isinstance(
            trade_setup["stop_loss"],
            (int, float),
        )

        assert isinstance(
            trade_setup["targets"],
            list,
        )

        assert len(
            trade_setup["targets"]
        ) > 0

        assert isinstance(
            trade_setup["risk_reward"],
            (int, float),
        )

        assert (
            trade_setup["risk_reward"]
            >= 1.5
        )

    else:

        assert trade_setup["direction"] is None

        assert trade_setup["entry"] is None

        assert trade_setup["stop_loss"] is None

        assert trade_setup["targets"] == []

        assert trade_setup["risk_reward"] is None


def test_trade_setup_receives_existing_market_data(
    monkeypatch,
):
    """
    TradeSetupService must receive the already-calculated
    candle and market-analysis data from the route.

    The service must not fetch its own MT5 candles.
    """

    captured = {}

    original_analyze = (
        market_data_routes
        .TradeSetupService
        .analyze
    )

    def capture_trade_setup_call(
        *args,
        **kwargs,
    ):
        captured.update(kwargs)

        return original_analyze(
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeStructureMT5DataProvider,
    )

    monkeypatch.setattr(
        market_data_routes.TradeSetupService,
        "analyze",
        capture_trade_setup_call,
    )

    FakeStructureMT5DataProvider.candle_fetch_count = 0

    headers = get_auth_headers()

    response = client.get(
        "/market-data/candles"
        "?symbol=EURUSD"
        "&timeframe=H1"
        "&count=100",
        headers=headers,
    )

    assert response.status_code == 200

    assert "candles" in captured
    assert "market_bias" in captured
    assert "atr" in captured
    assert "latest_bos" in captured
    assert "latest_choch" in captured
    assert "latest_liquidity_sweep" in captured
    assert "latest_order_block" in captured
    assert "latest_fvg" in captured
    assert "latest_premium_discount" in captured
    assert "support_resistance" in captured
    assert "symbol" in captured
    assert "timeframe" in captured

    assert len(captured["candles"]) == 100

    assert captured["symbol"] == "EURUSD"
    assert captured["timeframe"] == "H1"

    assert isinstance(
        captured["market_bias"],
        dict,
    )

    assert isinstance(
        captured["atr"],
        (int, float),
    )

    assert (
        captured["support_resistance"]
        is not None
    )

    # Most important architecture protection:
    # the route still fetched MT5 candles only once.
    assert (
        FakeStructureMT5DataProvider.candle_fetch_count
        == 1
    )


def test_trade_setup_reuses_single_candle_fetch(
    monkeypatch,
):
    """
    Trade Setup must reuse the same MT5 candle dataset
    already fetched by the market-data route.

    No second MT5 candle request is allowed.
    """

    monkeypatch.setattr(
        market_data_routes,
        "MT5DataProvider",
        FakeStructureMT5DataProvider,
    )

    FakeStructureMT5DataProvider.candle_fetch_count = 0

    headers = get_auth_headers()

    response = client.get(
        "/market-data/candles"
        "?symbol=EURUSD"
        "&timeframe=H1"
        "&count=100",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert "market_bias" in data
    assert "trade_setup" in data

    assert (
        FakeStructureMT5DataProvider.candle_fetch_count
        == 1
    )