from app.schemas.trade_schema import TradeCreateSchema


def test_trade_schema():

    trade = TradeCreateSchema(
        symbol="EUR/USD",
        direction="Buy",
        entry_price=1.0800,
        lot_size=0.10,
        stop_loss=1.0750,
        take_profit=1.0900,
    )

    assert trade.symbol == "EUR/USD"
    assert trade.direction == "Buy"
