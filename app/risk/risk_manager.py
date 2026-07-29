"""
risk_manager.py

Contains the RiskManager class used by the
Aladdin Forex Trading Assistant.

This class provides reusable calculations for trade risk,
position sizing, pip size, and pip distance.

Author: Tharindu Kothalwala
Project: Aladdin
"""


class RiskManager:
    """
    Provide risk-management calculations for Forex trades.

    All methods are static because the class does not need
    to store account or trade information inside an object.
    """

    # ==========================================
    # Risk Amount
    # ==========================================

    @staticmethod
    def calculate_risk_amount(account_balance, risk_percent):
        """
        Calculate the amount of money allowed to risk on a trade.

        Args:
            account_balance (float): Current trading account balance.
            risk_percent (float): Percentage of the balance to risk.

        Returns:
            float: Amount of money allowed to risk.

        Raises:
            ValueError: If the account balance is zero or negative.
            ValueError: If the risk percentage is outside 0 to 100.
        """

        # A valid account balance must be greater than zero.
        if account_balance <= 0:
            raise ValueError("Account balance must be greater than zero.")

        # Risk percentage must be positive and cannot exceed 100%.
        if risk_percent <= 0 or risk_percent > 100:
            raise ValueError("Risk percentage must be between 0 and 100.")

        return account_balance * risk_percent / 100

    # ==========================================
    # Position Size
    # ==========================================

    @staticmethod
    def calculate_position_size(risk_amount, stop_loss_distance):
        """
        Calculate position size using risk amount and stop-loss distance.

        Formula:
            position size = risk amount / stop-loss distance

        Args:
            risk_amount (float): Maximum amount of money to risk.
            stop_loss_distance (float): Distance between entry and stop loss.

        Returns:
            float: Calculated position size.

        Raises:
            ValueError: If the stop-loss distance is zero or negative.
        """

        # Division by zero or a negative distance is not valid.
        if stop_loss_distance <= 0:
            raise ValueError("Stop loss distance must be greater than zero.")

        return risk_amount / stop_loss_distance

    # ==========================================
    # Pip Calculations
    # ==========================================

    @staticmethod
    def get_pip_size(symbol):
        """
        Return the standard pip size for a Forex symbol.

        Most Forex pairs use 0.0001 as one pip.
        Japanese yen pairs normally use 0.01 as one pip.

        Examples:
            EUR/USD -> 0.0001
            USD/JPY -> 0.01

        Args:
            symbol (str): Forex pair such as EUR/USD or USDJPY.

        Returns:
            float: Pip size for the symbol.
        """

        # Remove the slash and use uppercase for consistent checking.
        normalized_symbol = symbol.replace("/", "").upper()

        # Yen pairs use two decimal places for a standard pip.
        if normalized_symbol.endswith("JPY"):
            return 0.01

        return 0.0001

    @staticmethod
    def calculate_pips(symbol, price_distance):
        """
        Convert a price distance into pips.

        Args:
            symbol (str): Forex pair such as EUR/USD or USD/JPY.
            price_distance (float): Difference between two prices.

        Returns:
            float: Price distance measured in pips.
        """

        pip_size = RiskManager.get_pip_size(symbol)

        return price_distance / pip_size
