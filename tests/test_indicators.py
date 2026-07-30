"""
test_indicators.py

Tests for technical indicators.

Author: Tharindu Kothalwala
Project: Aladdin
"""

import pytest

from app.market.indicators import TechnicalIndicators

from datetime import datetime

from app.market.candle import Candle


def test_calculate_sma():

    prices = [
        1.0800,
        1.0820,
        1.0840,
    ]

    sma = TechnicalIndicators.calculate_sma(
        prices,
        3,
    )

    assert sma == 1.082


def test_calculate_sma_with_larger_period():

    prices = [
        1.0700,
        1.0800,
        1.0900,
        1.1000,
    ]

    sma = TechnicalIndicators.calculate_sma(
        prices,
        4,
    )

    assert sma == 1.085


def test_sma_rejects_insufficient_data():

    prices = [
        1.0800,
        1.0820,
    ]

    with pytest.raises(
        ValueError,
        match="Not enough price data for SMA calculation.",
    ):

        TechnicalIndicators.calculate_sma(
            prices,
            3,
        )


def test_calculate_rsi():

    prices = [
        1.1000,
        1.1020,
        1.1040,
        1.1060,
    ]

    rsi = TechnicalIndicators.calculate_rsi(
        prices,
        3,
    )

    assert rsi == 100.0


def test_rsi_rejects_insufficient_data():

    prices = [
        1.1000,
        1.1020,
    ]

    with pytest.raises(
        ValueError,
        match="Not enough price data for RSI calculation.",
    ):

        TechnicalIndicators.calculate_rsi(
            prices,
            3,
        )


def test_calculate_atr():

    candles = [
        Candle(
            symbol="EUR/USD",
            timeframe="1H",
            open_price=1.1000,
            high_price=1.1050,
            low_price=1.0950,
            close_price=1.1020,
            volume=1000,
            timestamp=datetime.now(),
        ),
        Candle(
            symbol="EUR/USD",
            timeframe="1H",
            open_price=1.1020,
            high_price=1.1080,
            low_price=1.1000,
            close_price=1.1060,
            volume=1000,
            timestamp=datetime.now(),
        ),
        Candle(
            symbol="EUR/USD",
            timeframe="1H",
            open_price=1.1060,
            high_price=1.1100,
            low_price=1.1040,
            close_price=1.1080,
            volume=1000,
            timestamp=datetime.now(),
        ),
    ]

    atr = TechnicalIndicators.calculate_atr(
        candles,
        2,
    )

    assert atr == 0.007


def test_atr_rejects_insufficient_data():

    candles = []

    with pytest.raises(
        ValueError,
        match="Not enough candle data for ATR calculation.",
    ):

        TechnicalIndicators.calculate_atr(
            candles,
            3,
        )
