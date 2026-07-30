"""
test_market_analyzer.py

Tests for MarketAnalyzer.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.analysis.market_analyzer import MarketAnalyzer


def test_bullish_market_analysis():

    signal = MarketAnalyzer.analyze(
        symbol="EUR/USD",
        current_price=1.0850,
        sma=1.0800,
        rsi=60,
        atr=0.0015,
    )

    assert signal.trend == "Bullish"

    assert signal.momentum == "Positive"

    assert signal.volatility == "Normal"


def test_bearish_market_analysis():

    signal = MarketAnalyzer.analyze(
        symbol="EUR/USD",
        current_price=1.0750,
        sma=1.0800,
        rsi=40,
        atr=0.0030,
    )

    assert signal.trend == "Bearish"

    assert signal.momentum == "Negative"

    assert signal.volatility == "High"
