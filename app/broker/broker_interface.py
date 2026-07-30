"""
broker_interface.py

Defines common broker operations.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from abc import ABC, abstractmethod


class BrokerInterface(ABC):
    """
    Abstract broker interface.

    Every broker connector must
    implement these methods.
    """

    @abstractmethod
    def connect(self):
        """
        Connect to broker.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnect from broker.
        """
        pass

    @abstractmethod
    def place_order(
        self,
        symbol,
        order_type,
        volume,
    ):
        """
        Place trading order.
        """
        pass
