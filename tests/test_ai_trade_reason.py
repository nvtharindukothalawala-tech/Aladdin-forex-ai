"""
test_ai_trade_reason.py

Tests AI trade reasoning generator.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.journal.ai_trade_reason import (
    AITradeReasonGenerator,
)


from app.intelligence.market_result import (
    MarketIntelligenceResult,
)


from app.risk.risk_validator import (
    RiskValidationResult,
)


from app.decision.decision_result import (
    DecisionResult,
)


def test_ai_trade_reason_generation():

    decision = DecisionResult(
        action="BUY",
        confidence=85,
        reason=("Bullish conditions confirmed"),
    )

    market_intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=85,
        technical_summary=("EMA and RSI confirm bullish momentum"),
        news_summary=("USD news sentiment is positive"),
        structure_summary=("Bullish BOS with liquidity sweep"),
        risk_level="LOW",
        recommendation=("Consider BUY opportunities"),
    )

    risk_validation = RiskValidationResult(
        approved=True,
        reason=("Trade risk is within allowed limit."),
    )

    result = AITradeReasonGenerator.generate(
        decision=decision,
        market_intelligence=market_intelligence,
        risk_validation=risk_validation,
    )

    assert result.decision == "BUY"

    assert result.confidence == 85

    assert "EMA" in result.technical_reason

    assert "USD" in result.news_reason

    assert "BOS" in result.structure_reason

    assert result.risk_reason == "Trade risk is within allowed limit."

    assert "technical analysis" in result.final_reason
