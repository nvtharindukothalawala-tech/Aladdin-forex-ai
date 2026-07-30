"""
test_trading_service.py

Tests trading workflow service.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.services.trading_service import TradingService


def test_generate_buy_trade_setup():

    result = TradingService.generate_trade_setup(
        symbol="EUR/USD",
        trend="Bullish",
        momentum="Positive",
        risk_reward=3,
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1100,
    )

    assert result["decision"].action == "BUY"

    assert result["trade_plan"].direction == "BUY"

    assert result["trade_plan"].risk_reward == 2.0


def test_generate_hold_setup():

    result = TradingService.generate_trade_setup(
        symbol="EUR/USD",
        trend="Bullish",
        momentum="Negative",
        risk_reward=1,
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1100,
    )

    assert result["decision"].action == "HOLD"

    assert "trade_plan" not in result
