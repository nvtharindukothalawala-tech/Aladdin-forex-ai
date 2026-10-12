from app.models.trade import Trade
from app.repositories.trade_repository import TradeRepository
from app.services.trade_service import TradeService


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


def test_load_trades(tmp_path):
    # Create a temporary trade history file.
    test_file = tmp_path / "test_trades.json"

    repository = TradeRepository(str(test_file))
    service = TradeService(repository)

    # Create sample trade data.
    trade = create_sample_trade()

    # Save sample trade to temporary file.
    service.add_trade(trade)
    service.save_trades()

    # Load trades using a new service instance.
    new_service = TradeService(
        TradeRepository(str(test_file))
    )

    trades = new_service.load_trades()

    # Verify the saved trade was loaded.
    assert len(trades) == 1
    assert trades[0].symbol == "EURUSD"
    assert trades[0].direction == "Buy"


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
