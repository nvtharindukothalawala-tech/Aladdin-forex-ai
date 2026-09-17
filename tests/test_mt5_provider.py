"""
test_mt5_provider.py

Tests for the read-only MetaTrader 5 market-data provider.

The MetaTrader5 module is mocked so these tests
can run safely in CI without an MT5 terminal.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from types import SimpleNamespace

import pytest

import app.market.mt5_provider as mt5_provider_module

from app.market.mt5_provider import (
    MT5DataProvider,
)


# ==========================================================
# FAKE MT5 MODULE
# ==========================================================


class FakeMT5Module:
    """
    Minimal deterministic fake MetaTrader5 module used by
    MT5DataProvider quote and pre-trade risk-data tests.
    """

    def __init__(self):
        self.initialized = False
        self.shutdown_called = False
        self.selected_symbols = []

        # ------------------------------------------
        # Account information
        # ------------------------------------------

        self.account = SimpleNamespace(
            equity=10_250.50,
            balance=10_000.00,
            margin=500.00,
            margin_free=9_750.50,
        )

        # ------------------------------------------
        # Symbol information
        # ------------------------------------------

        self.symbols = {
            "EURUSD": SimpleNamespace(
                name="EURUSD",
                point=0.00001,
                digits=5,
                trade_tick_size=0.00001,
                trade_tick_value=1.0,
                volume_min=0.01,
                volume_max=100.0,
                volume_step=0.01,
            ),
            "USDJPY": SimpleNamespace(
                name="USDJPY",
                point=0.001,
                digits=3,
                trade_tick_size=0.001,
                trade_tick_value=0.68,
                volume_min=0.01,
                volume_max=100.0,
                volume_step=0.01,
            ),
            "GOLD": SimpleNamespace(
                name="GOLD",
                point=0.01,
                digits=2,
                trade_tick_size=0.01,
                trade_tick_value=1.0,
                volume_min=0.01,
                volume_max=50.0,
                volume_step=0.01,
            ),
        }

        # ------------------------------------------
        # Live ticks
        # ------------------------------------------

        self.ticks = {
            "EURUSD": SimpleNamespace(
                bid=1.16050,
                ask=1.16062,
                time=1789372800,
            ),
            "USDJPY": SimpleNamespace(
                bid=147.250,
                ask=147.263,
                time=1789372801,
            ),
            "GOLD": SimpleNamespace(
                bid=2500.10,
                ask=2500.35,
                time=1789372802,
            ),
        }

    def initialize(self):
        self.initialized = True
        return True

    def shutdown(self):
        self.shutdown_called = True
        self.initialized = False

    def last_error(self):
        return (
            0,
            "No error",
        )

    def account_info(self):
        return self.account

    def symbol_info(
        self,
        symbol,
    ):
        return self.symbols.get(
            symbol
        )

    def symbols_get(self):
        return list(
            self.symbols.values()
        )

    def symbol_select(
        self,
        symbol,
        enabled,
    ):
        if (
            enabled
            and symbol in self.symbols
        ):
            self.selected_symbols.append(
                symbol
            )
            return True

        return False

    def symbol_info_tick(
        self,
        symbol,
    ):
        return self.ticks.get(
            symbol
        )


# ==========================================================
# FIXTURES
# ==========================================================


@pytest.fixture
def fake_mt5(
    monkeypatch,
):
    """
    Replace the real MetaTrader5 module
    with a deterministic fake.
    """

    fake = FakeMT5Module()

    monkeypatch.setattr(
        mt5_provider_module,
        "mt5",
        fake,
    )

    return fake


@pytest.fixture
def provider(
    fake_mt5,
):
    """
    Provide an MT5DataProvider and always
    release its shared MT5 session lock
    after each test.

    This mirrors the production API routes,
    which disconnect providers in finally
    blocks after market-data operations.
    """

    market_provider = MT5DataProvider()

    try:
        yield market_provider

    finally:
        market_provider.disconnect()


# ==========================================================
# EURUSD QUOTE
# ==========================================================


def test_get_quote_returns_real_market_fields(
    fake_mt5,
    provider,
):
    """
    Quote data should contain broker bid/ask,
    spread information, precision and timestamp.
    """

    quote = provider.get_quote(
        "EUR/USD"
    )

    assert quote["symbol"] == "EURUSD"

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

    assert (
        "EURUSD"
        in fake_mt5.selected_symbols
    )


# ==========================================================
# PRICE PRECISION
# ==========================================================


def test_get_quote_uses_broker_precision(
    provider,
):
    """
    USDJPY should use the broker's
    three-decimal precision.
    """

    quote = provider.get_quote(
        "USDJPY"
    )

    assert quote["symbol"] == "USDJPY"
    assert quote["bid"] == 147.250
    assert quote["ask"] == 147.263
    assert quote["digits"] == 3
    assert quote["point"] == 0.001

    assert (
        quote["spread_points"]
        == 13.0
    )


# ==========================================================
# BROKER SYMBOL ALIAS
# ==========================================================


def test_get_quote_resolves_xauusd_to_gold(
    provider,
):
    """
    XAUUSD should resolve to the broker's
    GOLD alias when XAUUSD is unavailable.
    """

    quote = provider.get_quote(
        "XAU/USD"
    )

    assert quote["symbol"] == "XAUUSD"
    assert quote["broker_symbol"] == "GOLD"

    assert quote["bid"] == 2500.10
    assert quote["ask"] == 2500.35

    assert quote["digits"] == 2
    assert quote["point"] == 0.01

    assert (
        quote["spread_points"]
        == 25.0
    )


# ==========================================================
# INVALID TICK
# ==========================================================


def test_get_quote_rejects_missing_tick(
    fake_mt5,
    provider,
):
    """
    Missing broker tick data should
    raise a runtime error.
    """

    fake_mt5.ticks["EURUSD"] = None

    with pytest.raises(
        RuntimeError,
        match="No MT5 market tick is available",
    ):
        provider.get_quote(
            "EURUSD"
        )


def test_get_quote_rejects_invalid_prices(
    fake_mt5,
    provider,
):
    """
    Zero or negative bid/ask prices
    must not be returned to Market Watch.
    """

    fake_mt5.ticks["EURUSD"] = (
        SimpleNamespace(
            bid=0.0,
            ask=1.16062,
            time=1789372800,
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Invalid MT5 bid/ask prices",
    ):
        provider.get_quote(
            "EURUSD"
        )


def test_get_quote_rejects_negative_spread(
    fake_mt5,
    provider,
):
    """
    Ask below bid represents an invalid
    quote and should be rejected.
    """

    fake_mt5.ticks["EURUSD"] = (
        SimpleNamespace(
            bid=1.16070,
            ask=1.16060,
            time=1789372800,
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Invalid MT5 quote spread",
    ):
        provider.get_quote(
            "EURUSD"
        )


# ==========================================================
# ACCOUNT RISK INFORMATION
# ==========================================================


def test_get_account_risk_info_returns_required_fields(
    fake_mt5,
    provider,
):
    """
    Risk account data should expose the read-only
    account values required by the RiskService.
    """

    result = provider.get_account_risk_info()

    assert result == {
        "equity": 10_250.50,
        "balance": 10_000.00,
        "margin": 500.00,
        "margin_free": 9_750.50,
    }

    assert fake_mt5.initialized is True
    assert provider.connected is True


def test_get_account_risk_info_rejects_missing_account(
    fake_mt5,
    provider,
):
    """
    Missing MT5 account information should fail safely.
    """

    fake_mt5.account = None

    with pytest.raises(
        RuntimeError,
        match="Unable to retrieve MT5 account information",
    ):
        provider.get_account_risk_info()


@pytest.mark.parametrize(
    "equity",
    [
        0.0,
        -1.0,
    ],
)
def test_get_account_risk_info_rejects_invalid_equity(
    fake_mt5,
    provider,
    equity,
):
    """
    Risk sizing must not continue with zero or
    negative account equity.
    """

    fake_mt5.account = SimpleNamespace(
        equity=equity,
        balance=10_000.00,
        margin=500.00,
        margin_free=9_500.00,
    )

    with pytest.raises(
        RuntimeError,
        match="Invalid MT5 account equity",
    ):
        provider.get_account_risk_info()


# ==========================================================
# SYMBOL RISK INFORMATION
# ==========================================================


def test_get_symbol_risk_info_returns_required_fields(
    fake_mt5,
    provider,
):
    """
    Symbol risk data should expose the broker values
    required for deterministic position sizing.
    """

    result = provider.get_symbol_risk_info(
        "EUR/USD"
    )

    assert result == {
        "symbol": "EURUSD",
        "broker_symbol": "EURUSD",
        "trade_tick_size": 0.00001,
        "trade_tick_value": 1.0,
        "volume_min": 0.01,
        "volume_max": 100.0,
        "volume_step": 0.01,
    }

    assert (
        "EURUSD"
        in fake_mt5.selected_symbols
    )


def test_get_symbol_risk_info_resolves_xauusd_to_gold(
    fake_mt5,
    provider,
):
    """
    Risk specifications should use the same broker
    symbol resolution as the quote/candle provider.
    """

    result = provider.get_symbol_risk_info(
        "XAU/USD"
    )

    assert result["symbol"] == "XAUUSD"
    assert result["broker_symbol"] == "GOLD"
    assert result["trade_tick_size"] == 0.01
    assert result["trade_tick_value"] == 1.0
    assert result["volume_min"] == 0.01
    assert result["volume_max"] == 50.0
    assert result["volume_step"] == 0.01

    assert (
        "GOLD"
        in fake_mt5.selected_symbols
    )


def test_get_symbol_risk_info_rejects_missing_symbol_info(
    fake_mt5,
    provider,
    monkeypatch,
):
    """
    A broker symbol that disappears after resolution
    should fail instead of returning incomplete specs.
    """

    original_symbol_info = fake_mt5.symbol_info
    calls = {"count": 0}

    def disappearing_symbol_info(symbol):
        calls["count"] += 1

        # Resolver can see the symbol first; the provider's
        # subsequent specification read then returns None.
        if calls["count"] >= 2:
            return None

        return original_symbol_info(symbol)

    monkeypatch.setattr(
        fake_mt5,
        "symbol_info",
        disappearing_symbol_info,
    )

    with pytest.raises(
        RuntimeError,
        match="Unable to retrieve MT5 symbol information",
    ):
        provider.get_symbol_risk_info(
            "EURUSD"
        )


@pytest.mark.parametrize(
    (
        "field",
        "value",
        "message",
    ),
    [
        (
            "trade_tick_size",
            0.0,
            "Invalid MT5 trade tick size",
        ),
        (
            "trade_tick_value",
            0.0,
            "Invalid MT5 trade tick value",
        ),
        (
            "volume_min",
            0.0,
            "Invalid MT5 minimum volume",
        ),
        (
            "volume_max",
            0.0,
            "Invalid MT5 maximum volume",
        ),
        (
            "volume_step",
            0.0,
            "Invalid MT5 volume step",
        ),
    ],
)
def test_get_symbol_risk_info_rejects_non_positive_specs(
    fake_mt5,
    provider,
    field,
    value,
    message,
):
    """
    Non-positive broker sizing specifications
    must be rejected before RiskService receives them.
    """

    setattr(
        fake_mt5.symbols["EURUSD"],
        field,
        value,
    )

    with pytest.raises(
        RuntimeError,
        match=message,
    ):
        provider.get_symbol_risk_info(
            "EURUSD"
        )


def test_get_symbol_risk_info_rejects_invalid_volume_range(
    fake_mt5,
    provider,
):
    """
    Broker minimum volume must never exceed
    broker maximum volume.
    """

    fake_mt5.symbols[
        "EURUSD"
    ].volume_min = 2.0

    fake_mt5.symbols[
        "EURUSD"
    ].volume_max = 1.0

    with pytest.raises(
        RuntimeError,
        match="Invalid MT5 volume range",
    ):
        provider.get_symbol_risk_info(
            "EURUSD"
        )


# ==========================================================
# CONNECTION REUSE
# ==========================================================


def test_risk_info_methods_reuse_provider_connection(
    fake_mt5,
    provider,
):
    """
    Account and symbol risk reads should reuse the same
    connected provider session instead of creating a
    second MT5 provider/session.
    """

    account = provider.get_account_risk_info()

    symbol = provider.get_symbol_risk_info(
        "EURUSD"
    )

    assert account["equity"] == 10_250.50
    assert symbol["broker_symbol"] == "EURUSD"
    assert provider.connected is True
    assert fake_mt5.initialized is True


# ==========================================================
# CONNECTION CLEANUP
# ==========================================================


def test_disconnect_closes_mt5_connection(
    fake_mt5,
):
    """
    Disconnect should call MT5 shutdown
    after a provider connection was opened.
    """

    provider = MT5DataProvider()

    try:
        provider.get_quote(
            "EURUSD"
        )

        assert provider.connected is True

        provider.disconnect()

        assert provider.connected is False
        assert fake_mt5.shutdown_called is True

    finally:
        provider.disconnect()
