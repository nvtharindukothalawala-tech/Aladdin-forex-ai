"""
test_mt5_connector.py

Tests MT5 connector.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.broker.mt5_connector import (
    MT5Connector,
)


def test_mt5_connection():

    broker = MT5Connector()

    result = broker.connect()

    assert result["status"] == "connected"


def test_prepare_order():

    broker = MT5Connector()

    broker.connect()

    order = broker.place_order(
        symbol="EUR/USD",
        order_type="BUY",
        volume=0.10,
    )

    assert order["status"] == "ORDER_READY"


def test_order_requires_connection():

    broker = MT5Connector()

    try:

        broker.place_order(
            symbol="EUR/USD",
            order_type="BUY",
            volume=0.10,
        )

        assert False

    except ConnectionError:

        assert True
