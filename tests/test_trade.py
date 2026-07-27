import pytest

from app.trade import Trade


def test_create_trade():

    trade = Trade("EUR/USD", "Buy", 1.0800, 0.10, 1.0750, 1.0900)

    assert trade.symbol == "EUR/USD"

    assert trade.direction == "Buy"

    assert trade.status == "Open"

    assert trade.entry_price == 1.0800


def test_close_trade():

    trade = Trade("EUR/USD", "Buy", 1.0800, 0.10, 1.0750, 1.0900)

    trade.close_trade(1.0850)

    assert trade.status == "Closed"

    assert trade.exit_price == 1.0850


def test_profit_calculation():

    trade = Trade("EUR/USD", "Buy", 1.0800, 0.10, 1.0750, 1.0900)

    trade.close_trade(1.0850)

    profit = trade.calculate_profit()

    assert profit > 0


def test_risk_reward_ratio():

    trade = Trade("EUR/USD", "Buy", 1.0800, 0.10, 1.0750, 1.0900)

    ratio = trade.calculate_risk_reward_ratio()

    assert ratio == 2


def test_direction_normalization():
    trade = Trade(
        symbol="EURUSD",
        direction="BUY",
        entry_price=1.1000,
        lot_size=1.0,
        stop_loss=1.0950,
        take_profit=1.1100,
    )

    assert trade.direction == "Buy"


import pytest


def test_empty_symbol_is_rejected():
    with pytest.raises(ValueError, match="Symbol cannot be empty"):
        Trade(
            symbol="",
            direction="Buy",
            entry_price=1.1000,
            lot_size=1.0,
            stop_loss=1.0950,
            take_profit=1.1100,
        )
