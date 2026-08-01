"""
test_journal_service.py

Tests trade journal memory.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.journal.trade_record import (
    TradeRecord,
)


from app.journal.journal_service import (
    JournalService,
)


def test_save_trade_record():

    trade = TradeRecord(
        symbol="EUR/USD",
        decision="BUY",
        entry_price=1.1000,
        exit_price=1.1150,
        profit_loss=150,
        confidence=85,
        reasoning="Bullish BOS confirmed",
    )

    result = JournalService.save_trade(trade)

    assert result.symbol == "EUR/USD"

    assert result.decision == "BUY"

    assert result.profit_loss == 150

    assert JournalService.get_trade_count() == 1
