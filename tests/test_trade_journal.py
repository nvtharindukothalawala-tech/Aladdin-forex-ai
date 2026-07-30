"""
test_trade_journal.py

Tests trade journal.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.journal.trade_journal import (
    TradeJournal,
    JournalTrade,
)


def test_add_trade_to_journal():

    journal = TradeJournal()

    trade = JournalTrade(
        symbol="EUR/USD",
        direction="BUY",
        result="WIN",
        profit_loss=100,
        risk_reward=2,
    )

    journal.add_trade(trade)

    assert journal.total_trades() == 1


def test_get_winning_trades():

    journal = TradeJournal()

    journal.add_trade(
        JournalTrade(
            symbol="EUR/USD",
            direction="BUY",
            result="WIN",
            profit_loss=100,
            risk_reward=2,
        )
    )

    journal.add_trade(
        JournalTrade(
            symbol="GBP/USD",
            direction="SELL",
            result="LOSS",
            profit_loss=-50,
            risk_reward=1,
        )
    )

    winners = journal.winning_trades()

    assert len(winners) == 1

    assert winners[0].symbol == "EUR/USD"
