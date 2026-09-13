"""
test_execution_service.py

Tests execution service workflow.

Author: Tharindu Kothalawala
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

    assert (
        execution.broker_order_id
        == "MOCK_ORDER_001"
    )

    assert (
        execution.execution_message
        == "Mock order executed successfully."
    )

    session.close()


def test_execution_service_saves_failed_broker_execution(
    monkeypatch,
):
    """
    Test that a failed broker execution
    finalizes the pending audit record
    as FAILED.
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

    def fake_execute_with_mt5(
        execution_request
    ):
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


def test_execution_service_saves_broker_exception_as_failed(
    monkeypatch,
):
    """
    Test that a broker exception finalizes
    the pending record as FAILED.
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

    def fake_execute_with_mt5(
        execution_request
    ):
        raise RuntimeError(
            "MT5 connection error."
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
        == "MT5 connection error."
    )

    session.close()


def test_execution_service_creates_pending_before_broker_call(
    monkeypatch,
):
    """
    Verify that the execution audit record
    exists before the broker is contacted.
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

    broker_checked_pending_record = {
        "value": False,
    }

    def fake_execute_with_mt5(
        execution_request
    ):
        executions = (
            repository.get_user_executions(
                user_id=1
            )
        )

        pending_records = [
            execution
            for execution in executions
            if (
                execution.symbol == "EUR/USD"
                and execution.status == "PENDING"
            )
        ]

        broker_checked_pending_record[
            "value"
        ] = bool(pending_records)

        return MT5ExecutionResult(
            success=True,
            message=(
                "Mock order executed successfully."
            ),
            order_id="MOCK_ORDER_PENDING_TEST",
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

    assert (
        broker_checked_pending_record["value"]
        is True
    )

    assert execution.status == "EXECUTED"

    assert (
        execution.broker_order_id
        == "MOCK_ORDER_PENDING_TEST"
    )

    session.close()


def test_execution_service_does_not_contact_broker_when_pending_save_fails(
    monkeypatch,
):
    """
    If the initial audit record cannot be
    saved, the broker must not be contacted.
    """

    class FailingRepository:
        def save_execution(
            self,
            **kwargs,
        ):
            raise RuntimeError(
                "Database unavailable."
            )

    broker_called = {
        "value": False,
    }

    def fake_execute_with_mt5(
        execution_request
    ):
        broker_called["value"] = True

        return MT5ExecutionResult(
            success=True,
            message=(
                "This should not execute."
            ),
            order_id="SHOULD_NOT_EXIST",
        )

    monkeypatch.setattr(
        ExecutionManager,
        "execute_with_mt5",
        fake_execute_with_mt5,
    )

    service = ExecutionService(
        FailingRepository()
    )

    request = ExecutionManager.prepare_execution(
        symbol="EUR/USD",
        direction="BUY",
        lot_size=0.10,
        approved=True,
    )

    try:
        service.execute_trade(
            user_id=1,
            execution_request=request,
        )

        assert False, (
            "Expected database failure "
            "was not raised."
        )

    except RuntimeError as error:
        assert (
            str(error)
            == "Database unavailable."
        )

    assert broker_called["value"] is False