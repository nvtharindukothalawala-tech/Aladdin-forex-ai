"""
execution_manager.py

Prepares approved trades for broker execution.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from dataclasses import dataclass

from app.mt5.mt5_connector import (
    MT5Connector,
)


@dataclass
class ExecutionRequest:
    """
    Represents a prepared execution request.
    """

    symbol: str
    order_type: str
    volume: float
    status: str

    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None

    # Database execution ID used to correlate
    # the local PENDING audit record with the
    # corresponding MT5 broker order.
    execution_id: int | None = None


class ExecutionManager:
    """
    Prepare approved trades for execution.
    """

    @staticmethod
    def prepare_execution(
        symbol,
        direction,
        lot_size,
        approved,
        entry_price=None,
        stop_loss=None,
        take_profit=None,
    ):
        """
        Create an execution request.

        When price levels are supplied,
        Entry, Stop Loss and Take Profit
        are validated before execution.
        """

        # ==========================================
        # Approval Check
        # ==========================================

        if not approved:
            raise ValueError(
                "Trade is not approved "
                "for execution."
            )

        # ==========================================
        # Symbol Check
        # ==========================================

        if (
            not symbol
            or not symbol.strip()
        ):
            raise ValueError(
                "Symbol is required."
            )

        # ==========================================
        # Direction Check
        # ==========================================

        direction = (
            direction
            .strip()
            .upper()
        )

        if direction not in {
            "BUY",
            "SELL",
        }:
            raise ValueError(
                "Invalid trade direction."
            )

        # ==========================================
        # Lot Size Check
        # ==========================================

        if lot_size <= 0:
            raise ValueError(
                "Lot size must be positive."
            )

        # ==========================================
        # Price Parameter Validation
        # ==========================================

        supplied_prices = [
            entry_price is not None,
            stop_loss is not None,
            take_profit is not None,
        ]

        if (
            any(supplied_prices)
            and not all(supplied_prices)
        ):
            raise ValueError(
                "Entry price, stop loss and "
                "take profit must be supplied "
                "together."
            )

        # ==========================================
        # Price Structure Validation
        # ==========================================

        if all(supplied_prices):

            if (
                entry_price <= 0
                or stop_loss <= 0
                or take_profit <= 0
            ):
                raise ValueError(
                    "Trade prices must be "
                    "greater than zero."
                )

            # BUY:
            #
            # Stop Loss < Entry < Take Profit

            if direction == "BUY":

                if not (
                    stop_loss
                    < entry_price
                    < take_profit
                ):
                    raise ValueError(
                        "Invalid BUY price structure. "
                        "Required: "
                        "stop_loss < entry_price "
                        "< take_profit."
                    )

            # SELL:
            #
            # Take Profit < Entry < Stop Loss

            elif direction == "SELL":

                if not (
                    take_profit
                    < entry_price
                    < stop_loss
                ):
                    raise ValueError(
                        "Invalid SELL price structure. "
                        "Required: "
                        "take_profit < entry_price "
                        "< stop_loss."
                    )

        # ==========================================
        # Build Execution Request
        # ==========================================

        return ExecutionRequest(
            symbol=symbol.upper(),
            order_type=direction,
            volume=lot_size,
            status="READY",
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            execution_id=None,
        )

    @staticmethod
    def execute_with_mt5(
        execution_request,
    ):
        """
        Execute the prepared trade through MT5.

        MOCK mode:
            Returns a fake successful execution.

        DEMO mode:
            Passes Entry, SL, TP and the local
            execution ID into the MT5 connector.

        The execution ID is used to create an
        MT5 comment such as:

            ALADDIN E123

        This allows a PENDING database execution
        to be correlated with broker information
        if the final database update fails.
        """

        if (
            execution_request.status
            != "READY"
        ):
            raise ValueError(
                "Execution request is not ready."
            )

        connector = MT5Connector()

        try:

            connector.connect()

            order = connector.prepare_order(
                symbol=execution_request.symbol,
                order_type=(
                    execution_request.order_type
                ),
                volume=execution_request.volume,
                entry_price=(
                    execution_request.entry_price
                ),
                stop_loss=(
                    execution_request.stop_loss
                ),
                take_profit=(
                    execution_request.take_profit
                ),
                execution_id=(
                    execution_request.execution_id
                ),
            )

            return connector.send_order(
                order
            )

        finally:

            connector.disconnect()