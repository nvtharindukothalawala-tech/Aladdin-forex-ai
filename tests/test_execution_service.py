"""
test_execution_service.py

Tests execution service workflow.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.database.connection import SessionLocal

from app.execution.repository import (
    ExecutionRepository,
)

from app.execution.execution_manager import (
    ExecutionManager,
)

from app.services.execution_service import (
    ExecutionService,
)

from app.mt5.mt5_connector import (
    MT5ExecutionResult,
)

def test_execute_trade_service():

    session = SessionLocal()

    repository = ExecutionRepository(session)

    service = ExecutionService(repository)

    request = ExecutionManager.prepare_execution(
        symbol="EUR/USD",
        direction="BUY",
        lot_size=0.10,
        approved=True,
    )

    execution = service.execute_trade(
        user_id=1,
        execution_request=request,
    )

    assert execution.symbol == "EUR/USD"

    assert execution.direction == "BUY"

    assert execution.volume == 0.10

    assert execution.status == "EXECUTED"

    assert execution.broker_order_id == "MOCK_ORDER_001"

    assert (
        execution.execution_message
        == "Order executed successfully."
    )

    session.close()

def test_execution_service_saves_failed_broker_execution(
    monkeypatch,
):
    """
    Test that failed broker execution
    is stored as FAILED.
    """

    session = SessionLocal()

    repository = ExecutionRepository(session)

    service = ExecutionService(repository)

    request = ExecutionManager.prepare_execution(
        symbol="EUR/USD",
        direction="BUY",
        lot_size=0.10,
        approved=True,
    )

    def fake_execute_with_mt5(execution_request):
        return MT5ExecutionResult(
            success=False,
            message="Broker execution failed.",
            order_id=None,
        )

    monkeypatch.setattr(
        ExecutionManager,
        "execute_with_mt5",
        fake_execute_with_mt5,
    )

    execution = service.execute_trade(
        user_id=1,
        execution_request=request,
    )

    assert execution.status == "FAILED"

    assert execution.broker_order_id is None

    assert (
        execution.execution_message
        == "Broker execution failed."
    )

    session.close()