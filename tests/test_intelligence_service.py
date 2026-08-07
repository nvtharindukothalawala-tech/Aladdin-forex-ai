"""
test_intelligence_service.py

Tests complete intelligence pipeline.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.intelligence_service import (
    IntelligenceService,
)


def test_complete_bullish_market_analysis():

    result = IntelligenceService.analyze_market(
        ema_signal="BULLISH",
        rsi_value=65,
        adx_value=30,
        volatility="NORMAL",
        currency="USD",
        event_type="Interest Rate Decision",
        importance="HIGH",
        sentiment="BULLISH",
        price_structure="BOS_BULLISH",
        liquidity_sweep=True,
        order_block="BULLISH",
        fair_value_gap=True,
    )

    assert result.market_bias == "BULLISH"

    assert result.risk_level == "LOW"

    assert result.recommendation == "Consider BUY opportunities"

    assert "BOS" in result.structure_summary

    assert result.confidence > 70


def test_conflicting_market_analysis():

    result = IntelligenceService.analyze_market(
        ema_signal="BULLISH",
        rsi_value=50,
        adx_value=15,
        volatility="HIGH",
        currency="USD",
        event_type="Economic Report",
        importance="HIGH",
        sentiment="BEARISH",
        price_structure="RANGE",
        liquidity_sweep=False,
        order_block="BEARISH",
        fair_value_gap=False,
    )

    assert result.market_bias == "NEUTRAL"

    assert result.recommendation == "Wait for stronger confirmation"

def test_intelligence_service_includes_multi_timeframe_analysis():
    """
    Test that the intelligence service
    includes multi-timeframe alignment.
    """

    result = IntelligenceService.analyze_market(
        ema_signal="BULLISH",
        rsi_value=65,
        adx_value=30,
        volatility="NORMAL",
        currency="USD",
        event_type="Interest Rate Decision",
        importance="HIGH",
        sentiment="BULLISH",
        price_structure="BOS_BULLISH",
        liquidity_sweep=True,
        order_block="BULLISH",
        fair_value_gap=True,
        higher_timeframe_bias="BULLISH",
        middle_timeframe_bias="BULLISH",
        entry_timeframe_bias="BULLISH",
    )

    assert result.timeframe_alignment == "FULL"

    assert result.timeframe_confidence == 100.0

    assert result.timeframe_summary == (
        "All monitored timeframes are aligned BULLISH"
    )