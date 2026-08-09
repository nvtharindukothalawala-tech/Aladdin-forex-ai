"""
test_mt5_connector.py

Tests MT5 connector.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.mt5.mt5_connector import (
    MT5Connector,
    MT5OrderRequest,
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


def test_prepare_order_rejects_invalid_volume():
    """
    Test that MT5 order preparation
    rejects zero or negative volume.
    """

    connector = MT5Connector()

    connector.connect()

    try:
        connector.prepare_order(
            symbol="EUR/USD",
            order_type="BUY",
            volume=0,
        )

        assert False

    except ValueError:
        assert True


def test_prepare_order_rejects_invalid_order_type():
    """
    Test that MT5 order preparation
    rejects invalid order directions.
    """

    connector = MT5Connector()

    connector.connect()

    try:
        connector.prepare_order(
            symbol="EUR/USD",
            order_type="HOLD",
            volume=0.10,
        )

        assert False

    except ValueError:
        assert True


def test_prepare_order_rejects_empty_symbol():
    """
    Test that MT5 order preparation
    rejects an empty trading symbol.
    """

    connector = MT5Connector()

    connector.connect()

    try:
        connector.prepare_order(
            symbol="",
            order_type="BUY",
            volume=0.10,
        )

        assert False

    except ValueError:
        assert True


def test_send_order_rejects_non_ready_order():
    """
    Test that MT5 refuses to send
    an order that is not ready.
    """

    connector = MT5Connector()

    connector.connect()

    order = MT5OrderRequest(
        symbol="EUR/USD",
        order_type="BUY",
        volume=0.10,
        status="CANCELLED",
    )

    try:
        connector.send_order(order)

        assert False

    except ValueError:
        assert True