from app.trade import Trade
from app.trade_repository import TradeRepository
from app.trade_service import TradeService


class FakeTradeRepository:
    def load_trades(self):
        return []

    def save_trades(self, trades):
        self.saved_trades = trades


def create_sample_trade():
    return Trade(
        symbol="EURUSD",
        direction="Buy",
        entry_price=1.1000,
        lot_size=1.0,
        stop_loss=1.0950,
        take_profit=1.1100,
    )


def test_add_trade():
    repository = FakeTradeRepository()
    service = TradeService(repository)

    trade = create_sample_trade()

    service.add_trade(trade)

    assert len(service.trades) == 1
    assert service.trades[0] == trade


def test_save_trades():
    repository = FakeTradeRepository()
    service = TradeService(repository)

    trade = create_sample_trade()

    service.add_trade(trade)
    service.save_trades()

    assert repository.saved_trades == service.trades


def test_load_trades():
    repository = TradeRepository("data/trades.json")
    service = TradeService(repository)

    trades = service.load_trades()

    assert len(trades) > 0


def test_find_trade():
    repository = FakeTradeRepository()
    service = TradeService(repository)

    trade = create_sample_trade()

    service.add_trade(trade)

    found_trade = service.find_trade(trade.trade_id)

    assert found_trade == trade


def test_find_trade_not_found():
    repository = FakeTradeRepository()
    service = TradeService(repository)

    found_trade = service.find_trade(9999)

    assert found_trade is None
