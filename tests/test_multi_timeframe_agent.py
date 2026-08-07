"""
test_multi_timeframe_agent.py

Tests Multi-Timeframe Analysis Agent.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.intelligence.multi_timeframe_agent import (
    MultiTimeframeAgent,
)


def test_full_bullish_timeframe_alignment():
    """
    Test when H4, H1, and M15 all agree
    with a bullish market direction.
    """

    result = MultiTimeframeAgent.analyze(
        higher_timeframe_bias="BULLISH",
        middle_timeframe_bias="BULLISH",
        entry_timeframe_bias="BULLISH",
    )

    assert result.higher_timeframe_bias == "BULLISH"

    assert result.middle_timeframe_bias == "BULLISH"

    assert result.entry_timeframe_bias == "BULLISH"

    assert result.alignment == "FULL"

    assert result.confidence == 100.0

    assert result.summary == (
        "All monitored timeframes are aligned BULLISH"
    )

def test_partial_timeframe_alignment():
    """
    Test when higher and middle timeframes agree,
    but the entry timeframe moves differently.
    """

    result = MultiTimeframeAgent.analyze(
        higher_timeframe_bias="BULLISH",
        middle_timeframe_bias="BULLISH",
        entry_timeframe_bias="BEARISH",
    )

    assert result.higher_timeframe_bias == "BULLISH"

    assert result.middle_timeframe_bias == "BULLISH"

    assert result.entry_timeframe_bias == "BEARISH"

    assert result.alignment == "PARTIAL"

    assert result.confidence == 75.0

    assert result.summary == (
        "Higher and middle timeframes agree, "
        "but entry timeframe differs"
    )

def test_weak_timeframe_alignment():
    """
    Test when middle and entry timeframes agree,
    but the higher timeframe differs.
    """

    result = MultiTimeframeAgent.analyze(
        higher_timeframe_bias="BULLISH",
        middle_timeframe_bias="BEARISH",
        entry_timeframe_bias="BEARISH",
    )

    assert result.higher_timeframe_bias == "BULLISH"

    assert result.middle_timeframe_bias == "BEARISH"

    assert result.entry_timeframe_bias == "BEARISH"

    assert result.alignment == "WEAK"

    assert result.confidence == 60.0

    assert result.summary == (
        "Middle and entry timeframes agree, "
        "but higher timeframe differs"
    )

def test_no_timeframe_alignment():
    """
    Test when all monitored timeframes
    show different market directions.
    """

    result = MultiTimeframeAgent.analyze(
        higher_timeframe_bias="BULLISH",
        middle_timeframe_bias="BEARISH",
        entry_timeframe_bias="NEUTRAL",
    )

    assert result.higher_timeframe_bias == "BULLISH"

    assert result.middle_timeframe_bias == "BEARISH"

    assert result.entry_timeframe_bias == "NEUTRAL"

    assert result.alignment == "NONE"

    assert result.confidence == 40.0

    assert result.summary == (
        "Timeframes are not aligned"
    )