"""
risk_manager.py

Contains the RiskManager class used by the
Aladdin Forex Trading Assistant.

Supports:
- Forex pairs
- JPY pairs
- XAU/USD Gold
- Risk amount
- Position sizing
- Pip size
- Pip distance
- Actual trade risk
- Risk-to-reward ratio

Author: Tharindu Kothalawala
Project: Aladdin
"""

from app.core.exceptions import RiskError
from app.core.logger import get_logger

from app.config.instrument_config import (
    get_pip_size,
)


class RiskManager:
    """
    Provide reusable risk-management calculations.
    """

    logger = get_logger(__name__)

    # ==========================================
    # Risk Amount
    # ==========================================

    @staticmethod
    def calculate_risk_amount(
        account_balance,
        risk_percent,
    ):
        """
        Calculate maximum allowed money risk.
        """

        if account_balance <= 0:
            RiskManager.logger.warning(
                "Invalid account balance: %s",
                account_balance,
            )

            raise RiskError(
                "Account balance must be greater than zero."
            )

        if risk_percent <= 0 or risk_percent > 100:
            RiskManager.logger.warning(
                "Invalid risk percentage: %s",
                risk_percent,
            )

            raise RiskError(
                "Risk percentage must be between 0 and 100."
            )

        risk_amount = (
            account_balance
            * risk_percent
            / 100
        )

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
        Calculate generic position size.
        """

        if risk_amount <= 0:
            raise RiskError(
                "Risk amount must be greater than zero."
            )

        if stop_loss_distance <= 0:
            RiskManager.logger.warning(
                "Invalid stop loss distance: %s",
                stop_loss_distance,
            )

            raise RiskError(
                "Stop loss distance must be greater than zero."
            )

        position_size = (
            risk_amount
            / stop_loss_distance
        )

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
        Calculate risk-to-reward ratio.

        Risk:
            |entry - stop|

        Reward:
            |take profit - entry|

        Ratio:
            reward / risk
        """

        risk_distance = abs(
            entry_price
            - stop_loss_price
        )

        reward_distance = abs(
            take_profit_price
            - entry_price
        )

        if risk_distance <= 0:
            RiskManager.logger.warning(
                "Entry price equals stop loss price."
            )

            raise RiskError(
                "Entry price and stop loss cannot be equal."
            )

        ratio = (
            reward_distance
            / risk_distance
        )

        RiskManager.logger.info(
            "Risk reward ratio calculated successfully: %s",
            ratio,
        )

        return ratio

    # ==========================================
    # Pip Size
    # ==========================================

    @staticmethod
    def get_pip_size(symbol):
        """
        Return instrument pip size.

        Examples:

        EUR/USD:
            0.0001

        USD/JPY:
            0.01

        XAU/USD:
            0.01
        """

        try:
            pip_size = get_pip_size(
                symbol
            )

        except ValueError as error:

            RiskManager.logger.warning(
                "Unsupported symbol for pip size: %s",
                symbol,
            )

            raise RiskError(
                str(error)
            ) from error

        return pip_size

    # ==========================================
    # Pip Calculation
    # ==========================================

    @staticmethod
    def calculate_pips(
        symbol,
        price_distance,
    ):
        """
        Convert price movement into pips.
        """

        if price_distance <= 0:
            raise RiskError(
                "Price distance must be greater than zero."
            )

        pip_size = (
            RiskManager.get_pip_size(
                symbol
            )
        )

        pips = (
            price_distance
            / pip_size
        )

        RiskManager.logger.info(
            "Pip calculation completed: %s pips for %s",
            pips,
            symbol,
        )

        return pips

    # ==========================================
    # Actual Trade Risk
    # ==========================================

    @staticmethod
    def calculate_trade_risk(
        stop_loss_pips,
        pip_value,
        lot_size,
    ):
        """
        Calculate actual monetary risk.

        Formula:

            actual risk =
                stop loss pips
                × pip value
                × lot size
        """

        if stop_loss_pips <= 0:
            raise RiskError(
                "Stop loss pips must be greater than zero."
            )

        if pip_value <= 0:
            raise RiskError(
                "Pip value must be greater than zero."
            )

        if lot_size <= 0:
            raise RiskError(
                "Lot size must be greater than zero."
            )

        actual_risk = (
            stop_loss_pips
            * pip_value
            * lot_size
        )

        RiskManager.logger.info(
            "Actual trade risk calculated successfully: %s",
            actual_risk,
        )

        return actual_risk

    # ==========================================
    # Forex / Instrument Lot Size
    # ==========================================

    @staticmethod
    def calculate_forex_lot_size(
        risk_amount,
        stop_loss_pips,
        pip_value,
    ):
        """
        Calculate lot size.

        Formula:

            lot size =
                risk amount
                /
                (stop loss pips × pip value)
        """

        if risk_amount <= 0:
            raise RiskError(
                "Risk amount must be greater than zero."
            )

        if stop_loss_pips <= 0:
            raise RiskError(
                "Stop loss pips must be greater than zero."
            )

        if pip_value <= 0:
            raise RiskError(
                "Pip value must be greater than zero."
            )

        lot_size = (
            risk_amount
            /
            (
                stop_loss_pips
                * pip_value
            )
        )

        RiskManager.logger.info(
            "Forex lot size calculated successfully: %s",
            lot_size,
        )

        return lot_size