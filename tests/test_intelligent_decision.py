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

    intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=85,
        technical_summary=("Bullish EMA trend"),
        news_summary=("USD strength expected"),
        risk_level="LOW",
        recommendation=("Consider BUY opportunities"),
    )

    result = DecisionEngine.make_intelligent_decision(intelligence)

    assert result.action == "BUY"

    assert result.confidence == 85

    assert "BUY" in result.reason


def test_intelligent_sell_decision():

    intelligence = MarketIntelligenceResult(
        market_bias="BEARISH",
        confidence=80,
        technical_summary=("Bearish EMA trend"),
        news_summary=("EUR weakness expected"),
        risk_level="LOW",
        recommendation=("Consider SELL opportunities"),
    )

    result = DecisionEngine.make_intelligent_decision(intelligence)

    assert result.action == "SELL"

    assert result.confidence == 80


def test_intelligent_hold_decision():

    intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=60,
        technical_summary=("Weak confirmation"),
        news_summary=("Unclear news impact"),
        risk_level="HIGH",
        recommendation=("Wait"),
    )

    result = DecisionEngine.make_intelligent_decision(intelligence)

    assert result.action == "HOLD"
