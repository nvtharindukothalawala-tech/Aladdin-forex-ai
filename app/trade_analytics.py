"""
trade_analytics.py

Contains the TradeAnalytics class used by the
Aladdin Forex Trading Assistant.

This class calculates general trade performance statistics.

Author: Tharindu Kothalwala
Project: Aladdin
"""


class TradeAnalytics:
    """
    Calculate general performance statistics from trades.

    The class receives a list of Trade objects and calculates
    values such as win rate, total profit, average profit,
    gross profit, gross loss, and profit factor.
    """

    # ==========================================
    # Constructor
    # ==========================================

    def __init__(self, trades):
        """
        Create a trade analytics object.

        Args:
            trades: List of Trade objects used for calculations.
        """

        # Store the trades that will be analysed.
        self.trades = trades

    # ==========================================
    # Trade Counts
    # ==========================================

    def total_trades(self):
        """
        Return the total number of trades.
        """

        return len(self.trades)

    def winning_trades(self):
        """
        Count all closed trades with a positive profit.

        Returns:
            int: Number of winning trades.
        """

        count = 0

        for trade in self.trades:
            profit = trade.calculate_profit()

            # An open trade returns None, so it is not counted.
            if profit is not None and profit > 0:
                count += 1

        return count

    def losing_trades(self):
        """
        Count all closed trades with a negative profit.

        Returns:
            int: Number of losing trades.
        """

        count = 0

        for trade in self.trades:
            profit = trade.calculate_profit()

            # An open trade returns None, so it is not counted.
            if profit is not None and profit < 0:
                count += 1

        return count

    def open_trades(self):
        """
        Count all trades that are still open.

        Returns:
            int: Number of open trades.
        """

        count = 0

        for trade in self.trades:
            if trade.status == "Open":
                count += 1

        return count

    # ==========================================
    # Performance Percentages
    # ==========================================

    def win_rate(self):
        """
        Calculate the percentage of closed trades that won.

        Breakeven trades are not included because the current
        calculation only counts winning and losing trades.

        Returns:
            float: Win rate as a percentage.
        """

        winning_count = self.winning_trades()
        losing_count = self.losing_trades()
        closed_trades = winning_count + losing_count

        # Avoid division by zero when there are no completed results.
        if closed_trades == 0:
            return 0

        return (winning_count / closed_trades) * 100

    # ==========================================
    # Profit Calculations
    # ==========================================

    def total_profit(self):
        """
        Calculate the combined profit and loss of all closed trades.

        Returns:
            float: Net profit from all closed trades.
        """

        total = 0

        for trade in self.trades:
            profit = trade.calculate_profit()

            # Open trades are ignored because their profit is None.
            if profit is not None:
                total += profit

        return total

    def average_profit(self):
        """
        Calculate the average result of all closed trades.

        Returns:
            float: Average profit or loss per closed trade.
            0: When there are no closed trades.
        """

        closed_trade_profits = []

        for trade in self.trades:
            profit = trade.calculate_profit()

            if profit is not None:
                closed_trade_profits.append(profit)

        if len(closed_trade_profits) == 0:
            return 0

        return sum(closed_trade_profits) / len(closed_trade_profits)

    def gross_profit(self):
        """
        Calculate the total profit from winning trades only.

        Returns:
            float: Combined value of all profitable trades.
        """

        total = 0

        for trade in self.trades:
            profit = trade.calculate_profit()

            if profit is not None and profit > 0:
                total += profit

        return total

    def gross_loss(self):
        """
        Calculate the total loss from losing trades only.

        The result is returned as a positive value.

        Returns:
            float: Combined absolute value of all losing trades.
        """

        total = 0

        for trade in self.trades:
            profit = trade.calculate_profit()

            if profit is not None and profit < 0:
                total += abs(profit)

        return total

    def profit_factor(self):
        """
        Calculate the ratio between gross profit and gross loss.

        Formula:
            gross profit / gross loss

        Returns:
            float: Profit factor.
            0: When there are no losing trades.
        """

        gross_loss = self.gross_loss()

        # Avoid division by zero when there are no losing trades.
        if gross_loss == 0:
            return 0

        return self.gross_profit() / gross_loss
