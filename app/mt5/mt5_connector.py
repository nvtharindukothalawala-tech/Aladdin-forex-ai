"""
mt5_connector.py

Handles MetaTrader 5 connection
and order preparation.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from dataclasses import dataclass


@dataclass
class MT5OrderRequest:
    """
    Represents an MT5 order request.
    """

    symbol: str

    order_type: str

    volume: float

    status: str


@dataclass
class MT5ExecutionResult:
    """
    Represents execution result.
    """

    success: bool

    message: str

    order_id: str | None = None


class MT5Connector:
    """
    Handles MT5 communication.

    Currently uses a mock implementation.
    Real MT5 API connection will be added later.
    """

    def __init__(self):

        self.connected = False

    def connect(self):
        """
        Simulate MT5 connection.
        """

        self.connected = True

        return True

    def disconnect(self):
        """
        Close MT5 connection.
        """

        self.connected = False

    def prepare_order(
        self,
        symbol,
        order_type,
        volume,
    ):
        """
        Prepare order request.
        """

        if not self.connected:

            raise ConnectionError("MT5 is not connected.")

        if volume <= 0:
            
            raise ValueError("Order volume must be greater than zero.")

        return MT5OrderRequest(
            symbol=symbol,
            order_type=order_type,
            volume=volume,
            status="READY",
        )

    def send_order(
        self,
        order_request,
    ):
        """
        Send order to MT5.

        Currently simulated.
        """

        if not self.connected:

            raise ConnectionError("MT5 is not connected.")

        return MT5ExecutionResult(
            success=True,
            message="Order executed successfully.",
            order_id="MOCK_ORDER_001",
        )
