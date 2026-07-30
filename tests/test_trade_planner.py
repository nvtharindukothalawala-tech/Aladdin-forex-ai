"""
test_trade_planner.py

Tests for TradePlanner.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.planning.trade_planner import TradePlanner


def test_create_buy_trade_plan():

    plan = TradePlanner.create_plan(
        symbol="EUR/USD",
        direction="BUY",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1100,
    )

    assert plan.direction == "BUY"

    assert plan.risk_reward == 2.0


def test_create_sell_trade_plan():

    plan = TradePlanner.create_plan(
        symbol="EUR/USD",
        direction="SELL",
        entry_price=1.1000,
        stop_loss=1.1050,
        take_profit=1.0900,
    )

    assert plan.direction == "SELL"

    assert plan.risk_reward == 2.0


def test_reject_invalid_stop_loss():

    try:

        TradePlanner.create_plan(
            symbol="EUR/USD",
            direction="BUY",
            entry_price=1.1000,
            stop_loss=1.1010,
            take_profit=1.1100,
        )

        assert False

    except ValueError:

        assert True
