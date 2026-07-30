"""
trade_journal.py

Stores completed trade information
with database persistence support.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from dataclasses import dataclass


@dataclass
class JournalTrade:
    """
    Represents a recorded trade.
    """

    symbol: str

    direction: str

    result: str

    profit_loss: float

    risk_reward: float


class TradeJournal:
    """
    Stores and manages trade history.
    """

    def __init__(
        self,
        repository=None,
    ):

        self.repository = repository

        self.trades = []

    def add_trade(
        self,
        trade,
    ):
        """
        Add trade.

        If repository exists,
        save to database.
        """

        self.trades.append(trade)

        if self.repository:

            self.repository.save_trade(trade)

    def get_all_trades(self):
        """
        Return all trades.
        """

        if self.repository:

            return self.repository.get_all_trades()

        return self.trades

    def total_trades(self):
        """
        Count trades.
        """

        return len(self.get_all_trades())

    def winning_trades(self):
        """
        Return winning trades.
        """

        return [trade for trade in self.get_all_trades() if trade.result == "WIN"]
