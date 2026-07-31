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
