"""
test_trading_service.py

Tests trading workflow service.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.services.trading_service import TradingService

# ==========================================
# BUY Trade Workflow Test
# ==========================================


def test_generate_buy_trade_setup():

    result = TradingService.generate_trade_setup(
        symbol="EUR/USD",
        trend="Bullish",
        momentum="Positive",
        risk_reward=3,
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1100,
        account_balance=10000,
        risk_percent=1,
        trade_risk_amount=100,
    )

    # Check decision result

    assert result["decision"].action == "BUY"

    # Check trade plan

    assert result["trade_plan"].direction == "BUY"

    assert result["trade_plan"].risk_reward == 2.0

    # Check risk validation

    assert result["risk_validation"].approved is True


# ==========================================
# Risk Rejection Test
# ==========================================


def test_reject_trade_when_risk_is_high():

    result = TradingService.generate_trade_setup(
        symbol="EUR/USD",
        trend="Bullish",
        momentum="Positive",
        risk_reward=3,
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1100,
        account_balance=10000,
        risk_percent=1,
        trade_risk_amount=500,
    )

    # Decision should still be BUY

    assert result["decision"].action == "BUY"

    # Risk validator should reject

    assert result["risk_validation"].approved is False


# ==========================================
# HOLD Decision Test
# ==========================================


def test_generate_hold_setup():

    result = TradingService.generate_trade_setup(
        symbol="EUR/USD",
        trend="Bullish",
        momentum="Negative",
        risk_reward=1,
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1100,
        account_balance=10000,
        risk_percent=1,
        trade_risk_amount=100,
    )

    assert result["decision"].action == "HOLD"

    assert "trade_plan" not in result
