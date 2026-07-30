"""
test_data_provider.py

Tests for MarketDataProvider.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from datetime import datetime

from app.market.candle import Candle
from app.market.data_provider import MarketDataProvider


def create_test_candle():
    return Candle(
        symbol="EUR/USD",
        timeframe="1H",
        open_price=1.0800,
        high_price=1.0850,
        low_price=1.0780,
        close_price=1.0830,
        volume=1000,
        timestamp=datetime.now(),
    )


def test_add_candle():

    provider = MarketDataProvider()

    candle = create_test_candle()

    provider.add_candle(candle)

    assert len(provider.get_all_candles()) == 1


def test_get_latest_candle():

    provider = MarketDataProvider()

    candle = create_test_candle()

    provider.add_candle(candle)

    latest = provider.get_latest(
        "EUR/USD",
        "1H",
    )

    assert latest == candle


def test_get_history():

    provider = MarketDataProvider()

    candle = create_test_candle()

    provider.add_candle(candle)

    history = provider.get_history(
        "EUR/USD",
        "1H",
    )

    assert len(history) == 1


def test_get_latest_returns_none():

    provider = MarketDataProvider()

    result = provider.get_latest(
        "GBP/USD",
        "1H",
    )

    assert result is None
