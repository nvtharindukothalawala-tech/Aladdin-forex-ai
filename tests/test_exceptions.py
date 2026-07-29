"""
Test custom exceptions used by Aladdin.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.core.exceptions import (
    AccountError,
    AladdinError,
    RiskError,
    TradeError,
)


def test_aladdin_error_structure():

    error = AladdinError("System error")

    assert str(error) == "System error"


def test_account_error():

    error = AccountError("Account problem")

    assert isinstance(error, AladdinError)


def test_trade_error():

    error = TradeError("Trade problem")

    assert isinstance(error, AladdinError)


def test_risk_error():

    error = RiskError("Risk problem")

    assert isinstance(error, AladdinError)
