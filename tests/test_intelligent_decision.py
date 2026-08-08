"""
test_intelligent_decision.py

Tests AI based decision generation.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.decision.decision_engine import (
    DecisionEngine,
)

from app.intelligence.market_result import (
    MarketIntelligenceResult,
)


def test_intelligent_buy_decision():
    """
    Test intelligent BUY decision.
    """

    intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=85,
        technical_summary="Bullish EMA trend",
        news_summary="USD strength expected",
        risk_level="LOW",
        recommendation="Consider BUY opportunities",
    )

    result = DecisionEngine.make_intelligent_decision(
        intelligence
    )

    assert result.action == "BUY"

    assert result.confidence == 85

    assert "BUY" in result.reason


def test_intelligent_sell_decision():
    """
    Test intelligent SELL decision.
    """

    intelligence = MarketIntelligenceResult(
        market_bias="BEARISH",
        confidence=80,
        technical_summary="Bearish EMA trend",
        news_summary="EUR weakness expected",
        risk_level="LOW",
        recommendation="Consider SELL opportunities",
    )

    result = DecisionEngine.make_intelligent_decision(
        intelligence
    )

    assert result.action == "SELL"

    assert result.confidence == 80


def test_intelligent_hold_decision():
    """
    Test intelligent HOLD decision.
    """

    intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=60,
        technical_summary="Weak confirmation",
        news_summary="Unclear news impact",
        risk_level="HIGH",
        recommendation="Wait",
    )

    result = DecisionEngine.make_intelligent_decision(
        intelligence
    )

    assert result.action == "HOLD"


def test_intelligent_decision_holds_when_timeframes_not_aligned():
    """
    Test that Aladdin does not generate a BUY
    when the monitored timeframes are not aligned.
    """

    intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=85,
        technical_summary="Bullish EMA trend",
        news_summary="USD strength expected",
        risk_level="LOW",
        recommendation="Consider BUY opportunities",
        timeframe_alignment="NONE",
        timeframe_confidence=40.0,
        timeframe_summary="Timeframes are not aligned",
    )

    result = DecisionEngine.make_intelligent_decision(
        intelligence
    )

    assert result.action == "HOLD"

    assert result.confidence == 85

    assert result.reason == (
        "Trade blocked because multi-timeframe "
        "analysis is not aligned."
    )


def test_intelligent_decision_adjusts_confidence_with_timeframes():
    """
    Test that timeframe confidence influences
    the final intelligent decision confidence.
    """

    intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=85,
        technical_summary="Bullish EMA trend",
        news_summary="USD strength expected",
        risk_level="LOW",
        recommendation="Consider BUY opportunities",
        timeframe_alignment="PARTIAL",
        timeframe_confidence=75.0,
        timeframe_summary=(
            "Higher and middle timeframes agree, "
            "but entry timeframe differs"
        ),
    )

    result = DecisionEngine.make_intelligent_decision(
        intelligence
    )

    assert result.action == "BUY"

    assert result.confidence == 82.0

    assert result.reason == (
        "Bullish market intelligence supports BUY. "
        "Timeframe alignment: PARTIAL. "
        "Decision confidence: 82.0%."
    )

def test_intelligent_sell_decision_explains_timeframe_alignment():
    """
    Test that an intelligent SELL decision
    explains multi-timeframe alignment
    and adjusted confidence.
    """

    intelligence = MarketIntelligenceResult(
        market_bias="BEARISH",
        confidence=80,
        technical_summary="Bearish EMA trend",
        news_summary="EUR weakness expected",
        risk_level="LOW",
        recommendation="Consider SELL opportunities",
        timeframe_alignment="PARTIAL",
        timeframe_confidence=70.0,
        timeframe_summary=(
            "Higher and middle timeframes agree, "
            "but entry timeframe differs"
        ),
    )

    result = DecisionEngine.make_intelligent_decision(
        intelligence
    )

    assert result.action == "SELL"

    # 80 * 0.70 + 70 * 0.30 = 77.0
    assert result.confidence == 77.0

    assert result.reason == (
        "Bearish market intelligence supports SELL. "
        "Timeframe alignment: PARTIAL. "
        "Decision confidence: 77.0%."
    )

def test_intelligent_decision_holds_during_low_activity_session():
    """
    Test that Aladdin blocks a trade
    during a low-activity market period.
    """

    intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=85,
        technical_summary="Bullish EMA trend",
        news_summary="USD strength expected",
        risk_level="LOW",
        recommendation="Consider BUY opportunities",
        timeframe_alignment="FULL",
        timeframe_confidence=100.0,
        timeframe_summary=(
            "All monitored timeframes are aligned BULLISH"
        ),
        market_session="OTHER",
        session_activity="LOW",
        session_condition="NEUTRAL",
        session_summary=(
            "Major Forex trading sessions "
            "are currently less active."
        ),
    )

    result = DecisionEngine.make_intelligent_decision(
        intelligence
    )

    assert result.action == "HOLD"

    assert result.reason == (
        "Trade blocked because market session "
        "activity is too low."
    )

def test_intelligent_decision_boosts_confidence_during_high_opportunity_session():
    """
    Test that a high-opportunity Forex session
    slightly increases decision confidence.
    """

    intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=85,
        technical_summary="Bullish EMA trend",
        news_summary="USD strength expected",
        risk_level="LOW",
        recommendation="Consider BUY opportunities",
        timeframe_alignment="FULL",
        timeframe_confidence=100.0,
        timeframe_summary=(
            "All monitored timeframes are aligned BULLISH"
        ),
        market_session="LONDON_NEW_YORK_OVERLAP",
        session_activity="VERY_HIGH",
        session_condition="HIGH_OPPORTUNITY",
        session_summary=(
            "London and New York sessions overlap "
            "with very high market activity."
        ),
    )

    result = DecisionEngine.make_intelligent_decision(
        intelligence
    )

    assert result.action == "BUY"

    # Timeframe-adjusted confidence:
    # 85 * 0.70 + 100 * 0.30 = 89.5
    #
    # High-opportunity session bonus:
    # 89.5 + 5 = 94.5
    assert result.confidence == 94.5

def test_intelligent_decision_confidence_never_exceeds_100():
    """
    Test that session confidence bonus
    cannot increase confidence above 100%.
    """

    intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=100,
        technical_summary="Strong bullish analysis",
        news_summary="Strong bullish news",
        risk_level="LOW",
        recommendation="Consider BUY opportunities",
        timeframe_alignment="FULL",
        timeframe_confidence=100.0,
        timeframe_summary=(
            "All monitored timeframes are aligned BULLISH"
        ),
        market_session="LONDON_NEW_YORK_OVERLAP",
        session_activity="VERY_HIGH",
        session_condition="HIGH_OPPORTUNITY",
        session_summary=(
            "London and New York sessions overlap "
            "with very high market activity."
        ),
    )

    result = DecisionEngine.make_intelligent_decision(
        intelligence
    )

    assert result.action == "BUY"

    assert result.confidence == 100.0