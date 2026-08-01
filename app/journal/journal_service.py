"""
journal_service.py

Manages AI trading memories.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.journal.trade_record import (
    TradeRecord,
)


class JournalService:
    """
    Stores and retrieves trade memories.
    """

    _records = []

    @staticmethod
    def save_trade(
        trade_record: TradeRecord,
    ):
        """
        Save completed trade.
        """

        JournalService._records.append(trade_record)

        return trade_record

    @staticmethod
    def get_all_trades():
        """
        Return all stored trades.
        """

        return JournalService._records

    @staticmethod
    def get_trade_count():
        """
        Return number of trades.
        """

        return len(JournalService._records)
