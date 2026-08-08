"""
test_technical_agent.py

Tests Technical Analysis Agent.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.technical_agent import (
    TechnicalAgent,
)


def test_bullish_technical_analysis():

    result = TechnicalAgent.analyze(
        ema_signal="BULLISH",
        rsi_value=65,
        adx_value=30,
        volatility="NORMAL",
    )

    assert result.trend == "BULLISH"

    assert result.momentum == "STRONG"

    assert result.volatility == "NORMAL"

    assert result.confidence > 50

    assert len(result.signals) > 0


def test_bearish_technical_analysis():

    result = TechnicalAgent.analyze(
        ema_signal="BEARISH",
        rsi_value=35,
        adx_value=30,
        volatility="HIGH",
    )

    assert result.trend == "BEARISH"

    assert result.momentum == "WEAK"

    assert result.volatility == "HIGH"

def test_high_volatility_reduces_technical_confidence():
    """
    Test that high market volatility
    reduces technical analysis confidence.
    """

    result = TechnicalAgent.analyze(
        ema_signal="BULLISH",
        rsi_value=65,
        adx_value=30,
        volatility="HIGH",
    )

    # Base confidence = 50
    # Bullish EMA = +15
    # Strong RSI = +10
    # Strong ADX = +10
    #
    # Before volatility adjustment = 85
    # HIGH volatility penalty = -10
    #
    # Final confidence = 75

    assert result.trend == "BULLISH"

    assert result.volatility == "HIGH"

    assert result.confidence == 75

    assert "High volatility reduces confidence" in result.signals

def test_technical_confidence_never_below_zero():
    """
    Test that technical confidence
    never becomes negative.
    """

    result = TechnicalAgent.analyze(
        ema_signal="NEUTRAL",
        rsi_value=35,
        adx_value=10,
        volatility="HIGH",
    )

    assert result.confidence >= 0