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

from app.intelligence.reasoning_engine import (
    ReasoningEngine,
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

def test_ai_trade_reason_uses_actual_risk_rejection_reason():
    """
    Test that AI reasoning uses the real
    risk validation rejection reason.
    """

    decision = DecisionResult(
        action="BUY",
        confidence=85,
        reason="Bullish conditions confirmed",
    )

    market_intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=85,
        technical_summary="EMA and RSI confirm bullish momentum",
        news_summary="USD news sentiment is positive",
        structure_summary="Bullish BOS with liquidity sweep",
        risk_level="LOW",
        recommendation="Consider BUY opportunities",
    )

    risk_validation = RiskValidationResult(
        approved=False,
        reason=(
            "Trade risk reward is below "
            "minimum required ratio."
        ),
    )

    result = AITradeReasonGenerator.generate(
        decision=decision,
        market_intelligence=market_intelligence,
        risk_validation=risk_validation,
    )

    assert result.risk_reason == (
        "Trade risk reward is below "
        "minimum required ratio."
    )

def test_generate_buy_trade_reasoning():

    result = ReasoningEngine.generate(
        decision="BUY",
        confidence=85,
        ema_signal="BULLISH",
        rsi_value=65,
        adx_value=30,
        price_structure="BOS_BULLISH",
        liquidity_sweep=True,
        risk_approved=True,
    )

    assert result.decision == "BUY"

    assert result.confidence == 85

    assert (
        "EMA trend confirms bullish momentum."
        in result.technical_reasons
    )

    assert (
        "RSI confirms buying momentum."
        in result.technical_reasons
    )

    assert (
        "ADX confirms strong trend strength."
        in result.technical_reasons
    )

    assert (
        "Liquidity sweep detected."
        in result.structure_reasons
    )

    assert (
        "Risk validation passed."
        in result.risk_reasons
    )


def test_generate_hold_reasoning():

    result = ReasoningEngine.generate(
        decision="HOLD",
        confidence=40,
        ema_signal="NEUTRAL",
        rsi_value=50,
        adx_value=10,
        price_structure="RANGE",
        liquidity_sweep=False,
        risk_approved=False,
    )

    assert result.decision == "HOLD"

    assert (
        "Risk validation failed."
        in result.risk_reasons
    )