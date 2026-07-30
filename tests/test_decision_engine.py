"""
test_decision_engine.py

Tests for DecisionEngine.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.decision.decision_engine import DecisionEngine


def test_buy_decision():

    result = DecisionEngine.make_decision(
        trend="Bullish",
        momentum="Positive",
        risk_reward=3,
    )

    assert result.action == "BUY"

    assert result.confidence == 75


def test_sell_decision():

    result = DecisionEngine.make_decision(
        trend="Bearish",
        momentum="Negative",
        risk_reward=2.5,
    )

    assert result.action == "SELL"


def test_hold_decision():

    result = DecisionEngine.make_decision(
        trend="Bullish",
        momentum="Negative",
        risk_reward=1,
    )

    assert result.action == "HOLD"
