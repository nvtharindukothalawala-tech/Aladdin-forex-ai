"""
mt5_connector.py

MetaTrader 5 broker connector.

Currently simulated.
Real MT5 API integration
will be added later.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.broker.broker_interface import (
    BrokerInterface,
)


class MT5Connector(BrokerInterface):
    """
    Simulated MetaTrader 5 connector.
    """

    def __init__(self):

        self.connected = False

    def connect(self):

        self.connected = True

        return {
            "status": "connected",
            "broker": "MT5",
        }

    def disconnect(self):

        self.connected = False

        return {
            "status": "disconnected",
            "broker": "MT5",
        }

    def place_order(
        self,
        symbol,
        order_type,
        volume,
    ):

        if not self.connected:

            raise ConnectionError("MT5 is not connected.")

        return {
            "symbol": symbol,
            "order_type": order_type,
            "volume": volume,
            "status": "ORDER_READY",
        }
