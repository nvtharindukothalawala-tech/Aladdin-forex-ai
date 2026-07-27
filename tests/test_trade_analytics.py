from app.trade import Trade
from app.trade_analytics import TradeAnalytics


def create_sample_trades():

    trade1 = Trade("EUR/USD", "Buy", 1.0800, 0.10, 1.0750, 1.0900)

    trade1.close_trade(1.0850)

    trade2 = Trade("GBP/USD", "Sell", 1.2500, 0.20, 1.2550, 1.2400)

    trade2.close_trade(1.2450)

    trade3 = Trade("USD/JPY", "Buy", 150.000, 0.10, 149.000, 151.000)

    trade3.close_trade(149.500)

    return [trade1, trade2, trade3]


def test_total_trades():

    trades = create_sample_trades()

    analytics = TradeAnalytics(trades)

    assert analytics.total_trades() == 3


def test_winning_and_losing_trades():

    trades = create_sample_trades()

    analytics = TradeAnalytics(trades)

    assert analytics.winning_trades() == 2

    assert analytics.losing_trades() == 1


def test_total_profit():

    trades = create_sample_trades()

    analytics = TradeAnalytics(trades)

    profit = analytics.total_profit()

    assert round(profit, 4) == -0.0485
