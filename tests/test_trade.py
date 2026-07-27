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
