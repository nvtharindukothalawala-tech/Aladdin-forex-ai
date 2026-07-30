"""
journal_service.py

Handles journal business logic.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.database.repository import TradeRepository


class JournalService:
    """
    Provides journal operations.
    """

    def __init__(self, repository):

        self.repository = repository

    def get_trades(self):

        return self.repository.get_all_trades()

    def get_trade_count(self):

        return self.repository.count_trades()
