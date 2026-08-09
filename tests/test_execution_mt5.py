"""
test_execution_mt5.py

Tests MT5 execution workflow.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.execution.execution_manager import (
    ExecutionManager,
    ExecutionRequest,
)


def test_execute_with_mt5():
    """
    Test successful MT5 execution.
    """

    request = ExecutionManager.prepare_execution(
        symbol="EUR/USD",
        direction="BUY",
        lot_size=0.10,
        approved=True,
    )

    result = ExecutionManager.execute_with_mt5(
        request
    )

    assert result.success is True

    assert result.order_id == "MOCK_ORDER_001"


def test_execute_with_mt5_rejects_non_ready_request():
    """
    Test that MT5 execution rejects
    requests that are not ready.
    """

    request = ExecutionRequest(
        symbol="EUR/USD",
        order_type="BUY",
        volume=0.10,
        status="PENDING",
    )

    try:
        ExecutionManager.execute_with_mt5(
            request
        )

        assert False

    except ValueError:
        assert True