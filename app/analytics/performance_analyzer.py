"""
performance_analyzer.py

Analyzes trading performance.

Author: Tharindu Kothalwala
Project: Aladdin
"""


class PerformanceAnalyzer:
    """
    Calculates trading statistics
    from journal trades.
    """

    def __init__(self, trades):

        self.trades = trades

    def total_trades(self):
        """
        Return total number of trades.
        """

        return len(self.trades)

    def winning_trades(self):
        """
        Count winning trades.
        """

        return len([trade for trade in self.trades if trade.result == "WIN"])

    def losing_trades(self):
        """
        Count losing trades.
        """

        return len([trade for trade in self.trades if trade.result == "LOSS"])

    def win_rate(self):
        """
        Calculate win percentage.
        """

        if not self.trades:
            return 0

        return self.winning_trades() / self.total_trades() * 100

    def total_profit(self):
        """
        Calculate total profit/loss.
        """

        return sum(trade.profit_loss for trade in self.trades)

    def average_risk_reward(self):
        """
        Calculate average risk reward.
        """

        if not self.trades:
            return 0

        return sum(trade.risk_reward for trade in self.trades) / len(self.trades)
