from app.trade import Trade
from app.trade_risk import TradeRisk


def create_risk_sample_trades():

    trade1 = Trade("GBP/JPY", "Buy", 200.50, 0.10, 199.50, 202.00)

    trade1.close_trade(201.50)

    trade2 = Trade("USD/JPY", "Buy", 150.000, 0.10, 149.000, 151.000)

    trade2.close_trade(149.500)

    trade3 = Trade("EUR/USD", "Buy", 1.0800, 0.10, 1.0750, 1.0900)

    trade3.close_trade(1.0850)

    return [trade1, trade2, trade3]


def test_largest_winning_trade():

    trades = create_risk_sample_trades()

    risk = TradeRisk(trades)

    largest_win = risk.largest_winning_trade()

    assert largest_win == 0.10000


def test_largest_losing_trade():

    trades = create_risk_sample_trades()

    risk = TradeRisk(trades)

    largest_loss = risk.largest_losing_trade()

    assert largest_loss == -0.05000


def test_average_risk_reward():

    trades = create_risk_sample_trades()

    risk = TradeRisk(trades)

    ratio = risk.average_risk_reward()

    assert ratio > 0


def test_maximum_drawdown():

    trades = create_risk_sample_trades()

    risk = TradeRisk(trades)

    drawdown = risk.maximum_drawdown()

    assert drawdown >= 0
