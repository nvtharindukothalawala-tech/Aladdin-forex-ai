"""
test_risk_validator.py

Tests risk validation.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.risk.risk_validator import RiskValidator


def test_trade_is_approved_when_risk_is_safe():

    result = RiskValidator.validate(
        account_balance=10000,
        risk_percent=1,
        trade_risk_amount=100,
    )

    assert result.approved is True


def test_trade_is_rejected_when_risk_is_high():

    result = RiskValidator.validate(
        account_balance=10000,
        risk_percent=1,
        trade_risk_amount=200,
    )

    assert result.approved is False


def test_reject_negative_balance():

    result = RiskValidator.validate(
        account_balance=-1000,
        risk_percent=1,
        trade_risk_amount=10,
    )

    assert result.approved is False


def test_reject_invalid_risk_percent():

    result = RiskValidator.validate(
        account_balance=1000,
        risk_percent=200,
        trade_risk_amount=10,
    )

    assert result.approved is False


def test_reject_zero_trade_risk():

    result = RiskValidator.validate(
        account_balance=1000,
        risk_percent=1,
        trade_risk_amount=0,
    )

    assert result.approved is False
