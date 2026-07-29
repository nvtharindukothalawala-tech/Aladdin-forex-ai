from app.models.trade import Trade
from app.repositories.trade_repository import TradeRepository


def test_save_and_load_trades(tmp_path):

    file_path = tmp_path / "test_trades.json"

    repository = TradeRepository(str(file_path))

    trade = Trade("EUR/USD", "Buy", 1.0800, 0.10, 1.0750, 1.0900)

    repository.save_trades([trade])

    loaded_trades = repository.load_trades()

    assert len(loaded_trades) == 1

    loaded_trade = loaded_trades[0]

    assert loaded_trade.symbol == "EUR/USD"

    assert loaded_trade.direction == "Buy"

    assert loaded_trade.status == "Open"
