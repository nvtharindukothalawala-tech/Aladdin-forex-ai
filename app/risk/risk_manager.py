"""
risk_manager.py

Contains the RiskManager class used by the
Aladdin Forex Trading Assistant.

This class provides reusable calculations for trade risk,
position sizing, pip size, pip distance,
and risk-to-reward ratio.

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

        if account_balance <= 0:
            RiskManager.logger.warning(
                "Invalid account balance: %s",
                account_balance,
            )

            raise RiskError("Account balance must be greater than zero.")

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
    def calculate_position_size(
        risk_amount,
        stop_loss_distance,
    ):
        """
        Calculate position size using risk amount and
        stop-loss distance.

        Formula:
            position size = risk amount / stop-loss distance

        Raises:
            RiskError:
                If the stop-loss distance is invalid.
        """

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
    # Risk-to-Reward Ratio
    # ==========================================

    @staticmethod
    def calculate_risk_reward_ratio(
        entry_price,
        stop_loss_price,
        take_profit_price,
    ):
        """
        Calculate the risk-to-reward ratio.

        Formula:
            risk = |entry - stop loss|
            reward = |take profit - entry|

            ratio = reward / risk

        Args:
            entry_price:
                Trade entry price.

            stop_loss_price:
                Stop-loss price.

            take_profit_price:
                Take-profit price.

        Returns:
            float:
                Risk-to-reward ratio.

        Raises:
            RiskError:
                If the risk distance is zero.
        """

        risk_distance = abs(entry_price - stop_loss_price)

        reward_distance = abs(take_profit_price - entry_price)

        if risk_distance == 0:
            RiskManager.logger.warning("Entry price equals stop loss price.")

            raise RiskError("Entry price and stop loss cannot be equal.")

        ratio = reward_distance / risk_distance

        RiskManager.logger.info(
            "Risk reward ratio calculated successfully: %s",
            ratio,
        )

        return ratio

    # ==========================================
    # Pip Calculations
    # ==========================================

    @staticmethod
    def get_pip_size(symbol):
        """
        Return the standard pip size for a Forex symbol.

        Most Forex pairs use 0.0001.
        Japanese Yen pairs use 0.01.
        """

        normalized_symbol = symbol.replace("/", "").upper()

        if normalized_symbol.endswith("JPY"):
            return 0.01

        return 0.0001

    @staticmethod
    def calculate_pips(
        symbol,
        price_distance,
    ):
        """
        Convert a price movement into pips.

        Args:
            symbol:
                Forex pair.

            price_distance:
                Difference between two prices.

        Returns:
            float:
                Number of pips.
        """

        pip_size = RiskManager.get_pip_size(symbol)

        pips = price_distance / pip_size

        RiskManager.logger.info(
            "Pip calculation completed: %s pips for %s",
            pips,
            symbol,
        )

        return pips

        # ==========================================

    # Forex Lot Size Calculation
    # ==========================================

    @staticmethod
    def calculate_forex_lot_size(
        risk_amount,
        stop_loss_pips,
        pip_value,
    ):
        """
        Calculate Forex lot size using professional
        position sizing formula.

        Formula:

            lot size =
            risk amount / (stop loss pips × pip value)

        Args:
            risk_amount:
                Amount of money willing to lose.

            stop_loss_pips:
                Distance between entry and stop loss.

            pip_value:
                Value of one pip for one standard lot.

        Returns:
            float:
                Recommended lot size.

        Raises:
            RiskError:
                If input values are invalid.
        """

        # Validate risk amount.
        if risk_amount <= 0:
            RiskManager.logger.warning(
                "Invalid risk amount: %s",
                risk_amount,
            )

            raise RiskError("Risk amount must be greater than zero.")

        # Validate stop loss distance.
        if stop_loss_pips <= 0:
            RiskManager.logger.warning(
                "Invalid stop loss pips: %s",
                stop_loss_pips,
            )

            raise RiskError("Stop loss pips must be greater than zero.")

        # Validate pip value.
        if pip_value <= 0:
            RiskManager.logger.warning(
                "Invalid pip value: %s",
                pip_value,
            )

            raise RiskError("Pip value must be greater than zero.")

        lot_size = risk_amount / (stop_loss_pips * pip_value)

        RiskManager.logger.info(
            "Forex lot size calculated successfully: %s",
            lot_size,
        )

        return lot_size
