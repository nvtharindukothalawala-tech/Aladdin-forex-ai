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


def test_invalid_entry_price_is_rejected():
    with pytest.raises(ValueError, match="Entry price must be greater than zero"):
        Trade(
            symbol="EURUSD",
            direction="Buy",
            entry_price=0,
            lot_size=1.0,
            stop_loss=1.0950,
            take_profit=1.1100,
        )


def test_invalid_stop_loss_is_rejected():
    with pytest.raises(ValueError, match="Stop loss must be greater than zero"):
        Trade(
            symbol="EURUSD",
            direction="Buy",
            entry_price=1.1000,
            lot_size=1.0,
            stop_loss=0,
            take_profit=1.1100,
        )


def test_invalid_take_profit_is_rejected():
    with pytest.raises(ValueError, match="Take profit must be greater than zero"):
        Trade(
            symbol="EURUSD",
            direction="Buy",
            entry_price=1.1000,
            lot_size=1.0,
            stop_loss=1.0950,
            take_profit=0,
        )


def test_cannot_close_trade_twice():
    trade = Trade(
        symbol="EURUSD",
        direction="Buy",
        entry_price=1.1000,
        lot_size=1.0,
        stop_loss=1.0950,
        take_profit=1.1100,
    )

    trade.close_trade(1.1050)

    with pytest.raises(ValueError, match="Trade is already closed"):
        trade.close_trade(1.1100)


def test_invalid_exit_price_is_rejected():
    trade = Trade(
        symbol="EURUSD",
        direction="Buy",
        entry_price=1.1000,
        lot_size=1.0,
        stop_loss=1.0950,
        take_profit=1.1100,
    )

    with pytest.raises(ValueError, match="Exit price must be greater than zero"):
        trade.close_trade(0)


def test_is_open_returns_true_for_open_trade():
    trade = Trade(
        symbol="EURUSD",
        direction="Buy",
        entry_price=1.1000,
        lot_size=1.0,
        stop_loss=1.0950,
        take_profit=1.1100,
    )

    assert trade.is_open() is True


def test_is_open_returns_false_for_closed_trade():
    trade = Trade(
        symbol="EURUSD",
        direction="Buy",
        entry_price=1.1000,
        lot_size=1.0,
        stop_loss=1.0950,
        take_profit=1.1100,
    )

    trade.close_trade(1.1050)

    assert trade.is_open() is False


def test_is_closed_returns_false_for_open_trade():
    trade = Trade(
        symbol="EURUSD",
        direction="Buy",
        entry_price=1.1000,
        lot_size=1.0,
        stop_loss=1.0950,
        take_profit=1.1100,
    )

    assert trade.is_closed() is False


def test_is_closed_returns_true_for_closed_trade():
    trade = Trade(
        symbol="EURUSD",
        direction="Buy",
        entry_price=1.1000,
        lot_size=1.0,
        stop_loss=1.0950,
        take_profit=1.1100,
    )

    trade.close_trade(1.1050)

    assert trade.is_closed() is True
