"""
test_journal_database_integration.py

Tests journal database integration.

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
    TradeJournal,
    JournalTrade,
)


def test_journal_saves_trade_to_database():

    session = SessionLocal()

    repository = TradeRepository(session)

    journal = TradeJournal(repository)

    trade = JournalTrade(
        symbol="GBP/USD",
        direction="SELL",
        result="WIN",
        profit_loss=150,
        risk_reward=3,
    )

    journal.add_trade(trade)

    trades = repository.get_all_trades()

    assert len(trades) >= 1

    assert trades[-1].symbol == "GBP/USD"

    session.close()
