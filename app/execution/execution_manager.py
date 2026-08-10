"""
execution_manager.py

Prepares trades for future broker execution.

Author: Tharindu Kothalwala
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
    ):
        """
        Create execution request.
        """

        if not approved:

            raise ValueError("Trade is not approved for execution.")

        if not symbol or not symbol.strip():

            raise ValueError("Symbol is required.")

        if direction not in [
            "BUY",
            "SELL",
        ]:

            raise ValueError("Invalid trade direction.")

        if lot_size <= 0:

            raise ValueError("Lot size must be positive.")

        return ExecutionRequest(
            symbol=symbol.upper(),
            order_type=direction,
            volume=lot_size,
            status="READY",
        )

    @staticmethod
    def execute_with_mt5(
        execution_request,
    ):
        """
        Execute prepared trade through MT5.
        """

        if execution_request.status != "READY":

            raise ValueError("Execution request is not ready.")

        connector = MT5Connector()

        connector.connect()

        order = connector.prepare_order(
            symbol=execution_request.symbol,
            order_type=execution_request.order_type,
            volume=execution_request.volume,
        )

        return connector.send_order(order)
