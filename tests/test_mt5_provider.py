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
    Minimal fake MetaTrader5 module required
    for MT5DataProvider quote tests.
    """

    def __init__(self):
        self.initialized = False
        self.shutdown_called = False
        self.selected_symbols = []

        self.symbols = {
            "EURUSD": SimpleNamespace(
                name="EURUSD",
                point=0.00001,
                digits=5,
            ),
            "USDJPY": SimpleNamespace(
                name="USDJPY",
                point=0.001,
                digits=3,
            ),
            "GOLD": SimpleNamespace(
                name="GOLD",
                point=0.01,
                digits=2,
            ),
        }

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