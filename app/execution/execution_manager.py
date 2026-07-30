"""
execution_manager.py

Prepares trades for future broker execution.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from dataclasses import dataclass


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

        Trade can only be prepared
        if risk validation is approved.
        """

        if not approved:

            raise ValueError("Trade is not approved for execution.")

        return ExecutionRequest(
            symbol=symbol,
            order_type=direction,
            volume=lot_size,
            status="READY",
        )
