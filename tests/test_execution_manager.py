"""
test_execution_manager.py

Tests execution preparation.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.execution.execution_manager import (
    ExecutionManager,
)


def test_prepare_execution_request():

    request = ExecutionManager.prepare_execution(
        symbol="EUR/USD",
        direction="BUY",
        lot_size=0.10,
        approved=True,
    )

    assert request.symbol == "EUR/USD"

    assert request.order_type == "BUY"

    assert request.volume == 0.10

    assert request.status == "READY"


def test_reject_unapproved_trade():

    try:

        ExecutionManager.prepare_execution(
            symbol="EUR/USD",
            direction="BUY",
            lot_size=0.10,
            approved=False,
        )

        assert False

    except ValueError:

        assert True
