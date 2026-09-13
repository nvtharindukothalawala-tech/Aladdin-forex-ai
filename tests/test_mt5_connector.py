"""
test_mt5_connector.py

Tests MetaTrader 5 connector behavior,
validation and execution correlation.

Author: Tharindu Kothalawala
Project: Aladdin
"""

import pytest

from app.mt5.mt5_connector import (
    MT5Connector,
)


def test_mock_connector_connects():
    """
    MOCK mode should connect without
    requiring the MetaTrader5 package.
    """

    connector = MT5Connector(
        mode="MOCK"
    )

    result = connector.connect()

    assert result is True
    assert connector.connected is True

    connector.disconnect()

    assert connector.connected is False


def test_prepare_mock_order():
    """
    MOCK mode should prepare a valid order.
    """

    connector = MT5Connector(
        mode="MOCK"
    )

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

    assert order.mt5_symbol is None
    assert order.execution_id is None

    connector.disconnect()


def test_prepare_order_requires_connection():
    """
    Order preparation must fail when
    the connector is not connected.
    """

    connector = MT5Connector(
        mode="MOCK"
    )

    with pytest.raises(
        ConnectionError
    ):
        connector.prepare_order(
            symbol="EUR/USD",
            order_type="BUY",
            volume=0.10,
        )


def test_prepare_order_rejects_invalid_volume():
    """
    Volume must be greater than zero.
    """

    connector = MT5Connector(
        mode="MOCK"
    )

    connector.connect()

    with pytest.raises(
        ValueError
    ):
        connector.prepare_order(
            symbol="EUR/USD",
            order_type="BUY",
            volume=0,
        )

    connector.disconnect()


def test_prepare_order_rejects_invalid_order_type():
    """
    Only BUY and SELL are allowed.
    """

    connector = MT5Connector(
        mode="MOCK"
    )

    connector.connect()

    with pytest.raises(
        ValueError
    ):
        connector.prepare_order(
            symbol="EUR/USD",
            order_type="HOLD",
            volume=0.10,
        )

    connector.disconnect()


def test_prepare_order_rejects_empty_symbol():
    """
    Symbol cannot be empty.
    """

    connector = MT5Connector(
        mode="MOCK"
    )

    connector.connect()

    with pytest.raises(
        ValueError
    ):
        connector.prepare_order(
            symbol="",
            order_type="BUY",
            volume=0.10,
        )

    connector.disconnect()


def test_send_order_rejects_non_ready_order():
    """
    Only READY orders may be sent.
    """

    connector = MT5Connector(
        mode="MOCK"
    )

    connector.connect()

    order = connector.prepare_order(
        symbol="EUR/USD",
        order_type="BUY",
        volume=0.10,
    )

    order.status = "BLOCKED"

    with pytest.raises(
        ValueError
    ):
        connector.send_order(
            order
        )

    connector.disconnect()


def test_prepare_order_preserves_execution_id():
    """
    The local execution database ID
    must remain attached to the prepared
    MT5 order.
    """

    connector = MT5Connector(
        mode="MOCK"
    )

    connector.connect()

    order = connector.prepare_order(
        symbol="EUR/USD",
        order_type="BUY",
        volume=0.10,
        execution_id=123,
    )

    assert order.execution_id == 123

    connector.disconnect()


def test_prepare_order_rejects_invalid_execution_id():
    """
    When supplied, execution_id must be
    a positive integer.
    """

    connector = MT5Connector(
        mode="MOCK"
    )

    connector.connect()

    invalid_ids = [
        0,
        -1,
        1.5,
        "123",
        True,
    ]

    for invalid_id in invalid_ids:

        with pytest.raises(
            ValueError
        ):
            connector.prepare_order(
                symbol="EUR/USD",
                order_type="BUY",
                volume=0.10,
                execution_id=invalid_id,
            )

    connector.disconnect()


def test_build_execution_comment_with_execution_id():
    """
    Correlated orders should use the
    deterministic ALADDIN execution comment.
    """

    comment = (
        MT5Connector._build_execution_comment(
            123
        )
    )

    assert comment == "ALADDIN E123"


def test_build_execution_comment_without_execution_id():
    """
    Direct connector usage without a
    local execution ID should preserve
    the existing fallback comment.
    """

    comment = (
        MT5Connector._build_execution_comment(
            None
        )
    )

    assert comment == "ALADDIN DEMO"