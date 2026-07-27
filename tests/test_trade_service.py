from app.trade_repository import TradeRepository
from app.trade_service import TradeService


def test_load_trades():

    repository = TradeRepository("data/trades.json")

    service = TradeService(repository)

    trades = service.load_trades()

    assert len(trades) > 0
