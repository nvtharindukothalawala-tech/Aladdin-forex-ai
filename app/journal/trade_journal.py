"""
trade_journal.py

Stores completed trade information.

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

    def __init__(self):

        self.trades = []

    def add_trade(
        self,
        trade,
    ):
        """
        Add completed trade
        to journal.
        """

        self.trades.append(trade)

    def get_all_trades(self):
        """
        Return all stored trades.
        """

        return self.trades

    def total_trades(self):
        """
        Count recorded trades.
        """

        return len(self.trades)

    def winning_trades(self):
        """
        Return profitable trades.
        """

        return [trade for trade in self.trades if trade.result == "WIN"]
