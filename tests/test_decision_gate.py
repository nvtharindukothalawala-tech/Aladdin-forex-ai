"""
test_decision_gate.py

Unit tests for the Aladdin Decision Gate.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.intelligence.technical_agent import (
    TechnicalAgent,
)

from app.intelligence.news_agent import (
    NewsAgent,
)

from app.intelligence.market_structure_agent import (
    MarketStructureAgent,
)

from app.intelligence.market_intelligence import (
    MarketIntelligenceAgent,
)

from app.decision.decision_engine import (
    DecisionEngine,
)


def create_bullish_market_intelligence():
    """
    Create a strong bullish market intelligence
    result for Decision Gate testing.
    """

    technical_result = TechnicalAgent.analyze(
        ema_signal="BULLISH",
        rsi_value=60,
        adx_value=30,
        volatility="NORMAL",
    )

    news_result = NewsAgent.analyze(
        currency="EUR",
        event_type="Interest Rate Decision",
        importance="MEDIUM",
        sentiment="BULLISH",
    )

    structure_result = MarketStructureAgent.analyze(
        price_structure="BOS_BULLISH",
        liquidity_sweep=True,
        order_block="BULLISH",
        fair_value_gap=True,
    )

    market_result = MarketIntelligenceAgent.analyze(
        technical_result=technical_result,
        news_result=news_result,
        structure_result=structure_result,
    )

    return market_result


def test_full_mtf_bullish_setup_returns_buy():
    """
    A fully aligned bullish setup should
    produce an approved BUY decision.
    """

    market_intelligence = (
        create_bullish_market_intelligence()
    )

    market_intelligence.timeframe_alignment = "FULL"
    market_intelligence.timeframe_confidence = 100

    decision = (
        DecisionEngine.make_intelligent_decision(
            market_intelligence
        )
    )

    assert decision.action == "BUY"
    assert decision.approved is True
    assert decision.decision_confidence == 87.4

def test_none_mtf_blocks_trade():
    """
    A NONE multi-timeframe alignment should
    block the trade.
    """

    market_intelligence = (
        create_bullish_market_intelligence()
    )

    market_intelligence.timeframe_alignment = "NONE"
    market_intelligence.timeframe_confidence = 40

    decision = (
        DecisionEngine.make_intelligent_decision(
            market_intelligence
        )
    )

    assert decision.action == "HOLD"
    assert decision.approved is False
    assert "multi_timeframe_alignment" in (
        decision.gates_failed
    )

def test_low_market_session_blocks_trade():
    """
    Low market session activity should
    block the trade.
    """

    market_intelligence = (
        create_bullish_market_intelligence()
    )

    market_intelligence.timeframe_alignment = "FULL"
    market_intelligence.timeframe_confidence = 100

    market_intelligence.market_session = "OTHER"
    market_intelligence.session_activity = "LOW"
    market_intelligence.session_condition = "NEUTRAL"

    decision = (
        DecisionEngine.make_intelligent_decision(
            market_intelligence
        )
    )

    assert decision.action == "HOLD"
    assert decision.approved is False
    assert "market_session" in (
        decision.gates_failed
    )

def test_high_opportunity_session_adds_confidence_bonus():
    """
    A high-opportunity market session should add
    the session confidence bonus.
    """

    market_intelligence = (
        create_bullish_market_intelligence()
    )

    market_intelligence.timeframe_alignment = "FULL"
    market_intelligence.timeframe_confidence = 100

    market_intelligence.market_session = (
        "LONDON_NEW_YORK_OVERLAP"
    )

    market_intelligence.session_activity = "VERY_HIGH"

    market_intelligence.session_condition = (
        "HIGH_OPPORTUNITY"
    )

    decision = (
        DecisionEngine.make_intelligent_decision(
            market_intelligence
        )
    )

    assert decision.action == "BUY"
    assert decision.approved is True
    assert decision.decision_confidence == 92.4

def test_bullish_bias_with_bearish_structure_blocks_trade():
    """
    Bullish market bias with bearish market structure
    should block the BUY decision.
    """

    market_intelligence = (
        create_bullish_market_intelligence()
    )

    market_intelligence.timeframe_alignment = "FULL"
    market_intelligence.timeframe_confidence = 100

    market_intelligence.structure_direction = "BEARISH"
    market_intelligence.structure_confirmation = (
        "BOS_BEARISH"
    )

    decision = (
        DecisionEngine.make_intelligent_decision(
            market_intelligence
        )
    )

    assert decision.action == "HOLD"
    assert decision.approved is False
    assert "market_structure_direction" in (
        decision.gates_failed
    )

def test_low_confidence_blocks_trade():
    """
    Decision confidence below 70% should
    block the trade.
    """

    market_intelligence = (
        create_bullish_market_intelligence()
    )

    market_intelligence.timeframe_alignment = "FULL"
    market_intelligence.timeframe_confidence = 50

    market_intelligence.confidence = 50

    decision = (
        DecisionEngine.make_intelligent_decision(
            market_intelligence
        )
    )

    assert decision.action == "HOLD"
    assert decision.approved is False
    assert "confidence" in (
        decision.gates_failed
    )