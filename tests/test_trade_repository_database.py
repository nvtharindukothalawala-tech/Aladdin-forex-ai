"""
test_trade_repository_database.py

Tests database trade repository.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.database.connection import (
    SessionLocal,
)


from app.database.repository import (
    TradeRepository,
)


from app.journal.trade_journal import (
    JournalTrade,
)


def test_save_trade_to_database():

    session = SessionLocal()

    repository = TradeRepository(session)

    trade = JournalTrade(
        symbol="EUR/USD",
        direction="BUY",
        result="WIN",
        profit_loss=100,
        risk_reward=2,
    )

    saved = repository.save_trade(trade)

    assert saved.symbol == "EUR/USD"

    assert saved.profit_loss == 100

    session.close()


def test_get_trade_count():

    session = SessionLocal()

    repository = TradeRepository(session)

    count = repository.count_trades()

    assert count >= 1

    session.close()
