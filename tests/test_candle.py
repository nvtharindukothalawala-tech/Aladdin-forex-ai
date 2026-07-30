"""
test_candle.py

Tests for Candle model.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from datetime import datetime

from app.market.candle import Candle


def test_create_candle():

    candle = Candle(
        symbol="EUR/USD",
        timeframe="1H",
        open_price=1.0800,
        high_price=1.0850,
        low_price=1.0780,
        close_price=1.0830,
        volume=1000,
        timestamp=datetime.now(),
    )

    assert candle.symbol == "EUR/USD"


def test_bullish_candle():

    candle = Candle(
        symbol="EUR/USD",
        timeframe="1H",
        open_price=1.0800,
        high_price=1.0850,
        low_price=1.0780,
        close_price=1.0830,
        volume=1000,
        timestamp=datetime.now(),
    )

    assert candle.is_bullish() is True


def test_price_range():

    candle = Candle(
        symbol="EUR/USD",
        timeframe="1H",
        open_price=1.0800,
        high_price=1.0850,
        low_price=1.0780,
        close_price=1.0830,
        volume=1000,
        timestamp=datetime.now(),
    )

    assert candle.price_range() == 0.007
