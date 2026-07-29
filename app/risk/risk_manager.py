"""
risk_manager.py

Contains the RiskManager class used by the
Aladdin Forex Trading Assistant.

This class provides reusable calculations for trade risk,
position sizing, pip size, and pip distance.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.core.exceptions import RiskError
from app.core.logger import get_logger


class RiskManager:
    """
    Provide risk-management calculations for Forex trades.

    All methods are static because the class does not need
    to store account or trade information inside an object.

    Risk validation errors use RiskError.
    """

    logger = get_logger(__name__)

    # ==========================================
    # Risk Amount
    # ==========================================

    @staticmethod
    def calculate_risk_amount(account_balance, risk_percent):
        """
        Calculate the amount of money allowed to risk on a trade.

        Args:
            account_balance:
                Current trading account balance.

            risk_percent:
                Percentage of the balance to risk.

        Returns:
            float:
                Amount of money allowed to risk.

        Raises:
            RiskError:
                If the account balance or risk percentage is invalid.
        """

        # A valid account balance must be greater than zero.
        if account_balance <= 0:
            RiskManager.logger.warning(
                "Invalid account balance: %s",
                account_balance,
            )

            raise RiskError("Account balance must be greater than zero.")

        # Risk percentage must be positive and cannot exceed 100%.
        if risk_percent <= 0 or risk_percent > 100:
            RiskManager.logger.warning(
                "Invalid risk percentage: %s",
                risk_percent,
            )

            raise RiskError("Risk percentage must be between 0 and 100.")

        risk_amount = account_balance * risk_percent / 100

        RiskManager.logger.info(
            "Risk amount calculated successfully: %s",
            risk_amount,
        )

        return risk_amount

    # ==========================================
    # Position Size
    # ==========================================

    @staticmethod
    def calculate_position_size(risk_amount, stop_loss_distance):
        """
        Calculate position size using risk amount and stop-loss distance.

        Formula:
            position size = risk amount / stop-loss distance

        Raises:
            RiskError:
                If the stop-loss distance is invalid.
        """

        # Division by zero or negative distance is not valid.
        if stop_loss_distance <= 0:
            RiskManager.logger.warning(
                "Invalid stop loss distance: %s",
                stop_loss_distance,
            )

            raise RiskError("Stop loss distance must be greater than zero.")

        position_size = risk_amount / stop_loss_distance

        RiskManager.logger.info(
            "Position size calculated successfully: %s",
            position_size,
        )

        return position_size

    # ==========================================
    # Pip Calculations
    # ==========================================

    @staticmethod
    def get_pip_size(symbol):
        """
        Return the standard pip size for a Forex symbol.

        Most Forex pairs use 0.0001 as one pip.
        Japanese yen pairs normally use 0.01 as one pip.
        """

        # Remove slash and convert to uppercase.
        normalized_symbol = symbol.replace("/", "").upper()

        # Yen pairs use two decimal places.
        if normalized_symbol.endswith("JPY"):
            return 0.01

        return 0.0001

    @staticmethod
    def calculate_pips(symbol, price_distance):
        """
        Convert price distance into pips.
        """

        pip_size = RiskManager.get_pip_size(symbol)

        pips = price_distance / pip_size

        RiskManager.logger.info(
            "Pip calculation completed: %s pips for %s",
            pips,
            symbol,
        )

        return pips
