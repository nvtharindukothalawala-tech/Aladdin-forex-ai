"""
test_mt5_connector.py

Tests MT5 connector.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.mt5.mt5_connector import (
    MT5Connector,
)


def test_mt5_connection():

    connector = MT5Connector()

    result = connector.connect()

    assert result is True

    assert connector.connected is True


def test_prepare_order():

    connector = MT5Connector()

    connector.connect()

    order = connector.prepare_order(
        symbol="EUR/USD",
        order_type="BUY",
        volume=0.10,
    )

    assert order.symbol == "EUR/USD"

    assert order.order_type == "BUY"

    assert order.volume == 0.10

    assert order.status == "READY"


def test_order_requires_connection():

    connector = MT5Connector()

    try:

        connector.prepare_order(
            symbol="EUR/USD",
            order_type="BUY",
            volume=0.10,
        )

        assert False

    except ConnectionError:

        assert True
