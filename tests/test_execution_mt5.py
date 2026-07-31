"""
test_execution_mt5.py

Tests MT5 execution workflow.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.execution.execution_manager import (
    ExecutionManager,
)


def test_execute_with_mt5():

    request = ExecutionManager.prepare_execution(
        symbol="EUR/USD",
        direction="BUY",
        lot_size=0.10,
        approved=True,
    )

    result = ExecutionManager.execute_with_mt5(request)

    assert result.success is True

    assert result.order_id == "MOCK_ORDER_001"
