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

from app.decision.decision_gate_result import (
    DecisionGateResult,
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

def test_ai_trade_reason_includes_full_timeframe_reasoning():

    decision = DecisionResult(
        action="BUY",
        confidence=90,
        reason="Bullish conditions confirmed",
    )

    market_intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=90,
        technical_summary="Bullish technical conditions",
        news_summary="Bullish news sentiment",
        structure_summary="Bullish market structure",
        risk_level="LOW",
        recommendation="Consider BUY opportunities",
        timeframe_alignment="FULL",
        timeframe_confidence=100,
        timeframe_summary=(
            "All monitored timeframes are aligned BULLISH"
        ),
    )

    risk_validation = RiskValidationResult(
        approved=True,
        reason="Trade risk is within allowed limit.",
    )

    result = AITradeReasonGenerator.generate(
        decision=decision,
        market_intelligence=market_intelligence,
        risk_validation=risk_validation,
    )

    assert (
        "All monitored timeframes are aligned BULLISH"
        in result.timeframe_reason
    )

    assert (
        "Multi-timeframe confirmation supports"
        in result.timeframe_reason
    )


def test_ai_trade_reason_includes_high_opportunity_session():

    decision = DecisionResult(
        action="BUY",
        confidence=90,
        reason="Bullish conditions confirmed",
    )

    market_intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=90,
        technical_summary="Bullish technical conditions",
        news_summary="Bullish news sentiment",
        structure_summary="Bullish market structure",
        risk_level="LOW",
        recommendation="Consider BUY opportunities",
        market_session="LONDON_NEW_YORK_OVERLAP",
        session_activity="VERY_HIGH",
        session_condition="HIGH_OPPORTUNITY",
        session_summary=(
            "London and New York sessions are active."
        ),
    )

    risk_validation = RiskValidationResult(
        approved=True,
        reason="Trade risk is within allowed limit.",
    )

    result = AITradeReasonGenerator.generate(
        decision=decision,
        market_intelligence=market_intelligence,
        risk_validation=risk_validation,
    )

    assert (
        "London and New York sessions are active."
        in result.session_reason
    )

    assert (
        "high-opportunity trading environment"
        in result.session_reason
    )

def test_ai_trade_reason_includes_decision_gate_information():

    decision = DecisionGateResult(
        action="BUY",
        approved=True,
        reason="All decision gates passed.",
        market_confidence=87.4,
        timeframe_confidence=100,
        decision_confidence=87.4,
        gates_passed=[
            "market_bias",
            "multi_timeframe_alignment",
            "market_session",
        ],
        gates_failed=[],
    )

    market_intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=87.4,
        technical_summary="Bullish technical conditions",
        news_summary="Bullish news sentiment",
        structure_summary="Bullish market structure",
        risk_level="LOW",
        recommendation="Consider BUY opportunities",
        timeframe_alignment="FULL",
        timeframe_confidence=100,
        timeframe_summary=(
            "All monitored timeframes are aligned BULLISH"
        ),
        market_session="LONDON_NEW_YORK_OVERLAP",
        session_activity="VERY_HIGH",
        session_condition="HIGH_OPPORTUNITY",
        session_summary=(
            "London and New York sessions are active."
        ),
    )

    risk_validation = RiskValidationResult(
        approved=True,
        reason="Trade risk is within allowed limit.",
    )

    result = AITradeReasonGenerator.generate(
        decision=decision,
        market_intelligence=market_intelligence,
        risk_validation=risk_validation,
    )

    assert result.gate_reason == (
        "All decision gates passed."
    )

    assert "market_bias" in result.gates_passed

    assert (
        "multi_timeframe_alignment"
        in result.gates_passed
    )

    assert result.gates_failed == []

    assert result.confidence == 87.4


def test_ai_trade_reason_includes_failed_decision_gates():

    decision = DecisionGateResult(
        action="HOLD",
        approved=False,
        reason="Multi-timeframe alignment is not sufficient.",
        market_confidence=80,
        timeframe_confidence=40,
        decision_confidence=64,
        gates_passed=[
            "market_bias",
        ],
        gates_failed=[
            "multi_timeframe_alignment",
            "market_session",
        ],
    )

    market_intelligence = MarketIntelligenceResult(
        market_bias="BULLISH",
        confidence=80,
        technical_summary="Bullish technical conditions",
        news_summary="Bullish news sentiment",
        structure_summary="Bullish market structure",
        risk_level="MEDIUM",
        recommendation="Wait for stronger confirmation",
        timeframe_alignment="NONE",
        timeframe_confidence=40,
        timeframe_summary=(
            "Timeframes are not aligned."
        ),
        market_session="OTHER",
        session_activity="LOW",
        session_condition="NEUTRAL",
        session_summary=(
            "Market session activity is low."
        ),
    )

    risk_validation = RiskValidationResult(
        approved=False,
        reason="Trade should not be executed.",
    )

    result = AITradeReasonGenerator.generate(
        decision=decision,
        market_intelligence=market_intelligence,
        risk_validation=risk_validation,
    )

    assert result.decision == "HOLD"

    assert result.gate_reason == (
        "Multi-timeframe alignment is not sufficient."
    )

    assert (
        "multi_timeframe_alignment"
        in result.gates_failed
    )

    assert "market_session" in result.gates_failed

    assert result.confidence == 64