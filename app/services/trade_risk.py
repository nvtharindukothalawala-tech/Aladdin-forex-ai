"""
trade_risk.py

Contains the TradeRisk class used by the
Aladdin Forex Trading Assistant.

This class calculates trade-related risk statistics.

Author: Tharindu Kothalwala
Project: Aladdin
"""


class TradeRisk:
    """
    Calculate risk and streak statistics from trades.

    The class receives a list of Trade objects and calculates
    values such as the largest win, largest loss, average
    risk-reward ratio, maximum drawdown, and winning or losing streaks.
    """

    # ==========================================
    # Constructor
    # ==========================================

    def __init__(self, trades):
        """
        Create a trade risk analytics object.

        Args:
            trades: List of Trade objects used for calculations.
        """

        # Store the trades that will be analysed.
        self.trades = trades

    # ==========================================
    # Largest Trade Results
    # ==========================================

    def largest_winning_trade(self):
        """
        Find the largest profit among all closed trades.

        Returns:
            float: Largest winning trade profit.
            0: When there are no winning trades.
        """

        largest_profit = 0

        for trade in self.trades:
            profit = trade.calculate_profit()

            # Ignore open trades and update only for a larger profit.
            if profit is not None and profit > largest_profit:
                largest_profit = profit

        return largest_profit

    def largest_losing_trade(self):
        """
        Find the largest loss among all closed trades.

        Returns:
            float: Largest losing trade as a negative value.
            0: When there are no losing trades.
        """

        largest_loss = 0

        for trade in self.trades:
            profit = trade.calculate_profit()

            # A more negative value represents a larger loss.
            if profit is not None and profit < largest_loss:
                largest_loss = profit

        return largest_loss

    # ==========================================
    # Risk-Reward Analysis
    # ==========================================

    def average_risk_reward(self):
        """
        Calculate the average risk-reward ratio of all trades.

        Returns:
            float: Average risk-reward ratio.
            0: When there are no valid ratios.
        """

        total_ratio = 0
        count = 0

        for trade in self.trades:
            ratio = trade.calculate_risk_reward_ratio()

            if ratio is not None:
                total_ratio += ratio
                count += 1

        # Avoid division by zero when no valid trade ratios exist.
        if count == 0:
            return 0

        return total_ratio / count

    # ==========================================
    # Drawdown Analysis
    # ==========================================

    def maximum_drawdown(self):
        """
        Calculate the largest drop from a previous profit peak.

        The calculation starts from a balance of zero and adds
        the result of each closed trade in list order.

        Returns:
            float: Maximum drawdown amount.
        """

        balance = 0
        peak = 0
        max_drawdown = 0

        for trade in self.trades:
            profit = trade.calculate_profit()

            # Ignore open trades because they have no completed result.
            if profit is not None:
                balance += profit

                # Record a new highest balance.
                if balance > peak:
                    peak = balance

                # Measure how far the balance has fallen from the peak.
                drawdown = peak - balance

                if drawdown > max_drawdown:
                    max_drawdown = drawdown

        return max_drawdown

    # ==========================================
    # Winning and Losing Streaks
    # ==========================================

    def maximum_consecutive_wins(self):
        """
        Find the longest sequence of winning trades.

        Returns:
            int: Highest number of consecutive wins.
        """

        current_wins = 0
        maximum_wins = 0

        for trade in self.trades:
            result = trade.get_trade_result()

            if result == "Win":
                current_wins += 1

                if current_wins > maximum_wins:
                    maximum_wins = current_wins
            else:
                # Any non-winning result ends the winning streak.
                current_wins = 0

        return maximum_wins

    def maximum_consecutive_losses(self):
        """
        Find the longest sequence of losing trades.

        Returns:
            int: Highest number of consecutive losses.
        """

        current_losses = 0
        maximum_losses = 0

        for trade in self.trades:
            result = trade.get_trade_result()

            if result == "Loss":
                current_losses += 1

                if current_losses > maximum_losses:
                    maximum_losses = current_losses
            else:
                # Any non-losing result ends the losing streak.
                current_losses = 0

        return maximum_losses
