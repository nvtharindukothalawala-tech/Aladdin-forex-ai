"""
test_execution_service.py

Tests execution service workflow.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from uuid import uuid4

import pytest

from app.database.connection import SessionLocal

from app.execution.repository import (
    ExecutionRepository,
)

from app.execution.execution_manager import (
    ExecutionManager,
)

from app.services.execution_service import (
    ExecutionIdempotencyConflictError,
    ExecutionService,
)

from app.mt5.mt5_connector import (
    MT5ExecutionResult,
)


def create_idempotency_key(
    prefix: str,
) -> str:
    """
    Create a unique test idempotency key.

    The execution tests use the project's normal
    development database, so unique keys prevent
    one test run from conflicting with another.
    """

    return f"{prefix}-{uuid4()}"


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

    assert request.execution_id == execution.id

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

    captured_execution_id = {
        "value": None,
    }

    def fake_execute_with_mt5(
        execution_request
    ):
        captured_execution_id[
            "value"
        ] = execution_request.execution_id

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

    assert (
        captured_execution_id["value"]
        == execution.id
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

    captured_execution_id = {
        "value": None,
    }

    def fake_execute_with_mt5(
        execution_request
    ):
        captured_execution_id[
            "value"
        ] = execution_request.execution_id

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

    assert (
        captured_execution_id["value"]
        == execution.id
    )

    session.close()


def test_execution_service_creates_pending_before_broker_call(
    monkeypatch,
):
    """
    Verify that the execution audit record
    exists before the broker is contacted
    and that its ID is passed into the
    execution request.
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

    correlation_matches_pending = {
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

        if pending_records:
            latest_pending = (
                pending_records[-1]
            )

            correlation_matches_pending[
                "value"
            ] = (
                execution_request.execution_id
                == latest_pending.id
            )

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

    assert (
        correlation_matches_pending["value"]
        is True
    )

    assert execution.status == "EXECUTED"

    assert (
        execution.broker_order_id
        == "MOCK_ORDER_PENDING_TEST"
    )

    assert request.execution_id == execution.id

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

    assert request.execution_id is None


def test_idempotent_execution_replay_contacts_broker_once(
    monkeypatch,
):
    """
    Repeating the same execution request with the
    same idempotency key must return the existing
    record without sending another broker order.
    """

    session = SessionLocal()

    repository = ExecutionRepository(session)

    service = ExecutionService(repository)

    idempotency_key = create_idempotency_key(
        "same-request"
    )

    broker_call_count = {
        "value": 0,
    }

    def fake_execute_with_mt5(
        execution_request
    ):
        broker_call_count["value"] += 1

        return MT5ExecutionResult(
            success=True,
            message="Idempotent broker success.",
            order_id="IDEMPOTENT_ORDER_001",
        )

    monkeypatch.setattr(
        ExecutionManager,
        "execute_with_mt5",
        fake_execute_with_mt5,
    )

    first_request = (
        ExecutionManager.prepare_execution(
            symbol="EUR/USD",
            direction="BUY",
            lot_size=0.10,
            approved=True,
        )
    )

    first_execution = service.execute_trade(
        user_id=900001,
        execution_request=first_request,
        idempotency_key=idempotency_key,
    )

    second_request = (
        ExecutionManager.prepare_execution(
            symbol="EUR/USD",
            direction="BUY",
            lot_size=0.10,
            approved=True,
        )
    )

    second_execution = service.execute_trade(
        user_id=900001,
        execution_request=second_request,
        idempotency_key=idempotency_key,
    )

    assert broker_call_count["value"] == 1

    assert (
        second_execution.id
        == first_execution.id
    )

    assert (
        second_execution.status
        == "EXECUTED"
    )

    assert (
        second_execution.broker_order_id
        == "IDEMPOTENT_ORDER_001"
    )

    assert (
        second_execution.idempotency_key
        == idempotency_key
    )

    assert (
        second_execution.request_fingerprint
        == first_execution.request_fingerprint
    )

    session.close()


def test_failed_execution_replay_does_not_retry_broker(
    monkeypatch,
):
    """
    Replaying a FAILED execution with the same key
    must return the existing FAILED record instead
    of automatically retrying MT5.
    """

    session = SessionLocal()

    repository = ExecutionRepository(session)

    service = ExecutionService(repository)

    idempotency_key = create_idempotency_key(
        "failed-request"
    )

    broker_call_count = {
        "value": 0,
    }

    def fake_execute_with_mt5(
        execution_request
    ):
        broker_call_count["value"] += 1

        return MT5ExecutionResult(
            success=False,
            message="Controlled broker failure.",
            order_id=None,
        )

    monkeypatch.setattr(
        ExecutionManager,
        "execute_with_mt5",
        fake_execute_with_mt5,
    )

    first_request = (
        ExecutionManager.prepare_execution(
            symbol="GBP/USD",
            direction="SELL",
            lot_size=0.20,
            approved=True,
        )
    )

    first_execution = service.execute_trade(
        user_id=900002,
        execution_request=first_request,
        idempotency_key=idempotency_key,
    )

    assert first_execution.status == "FAILED"

    second_request = (
        ExecutionManager.prepare_execution(
            symbol="GBP/USD",
            direction="SELL",
            lot_size=0.20,
            approved=True,
        )
    )

    second_execution = service.execute_trade(
        user_id=900002,
        execution_request=second_request,
        idempotency_key=idempotency_key,
    )

    assert broker_call_count["value"] == 1

    assert (
        second_execution.id
        == first_execution.id
    )

    assert second_execution.status == "FAILED"

    assert (
        second_execution.execution_message
        == "Controlled broker failure."
    )

    session.close()


def test_pending_execution_replay_does_not_contact_broker(
    monkeypatch,
):
    """
    A matching PENDING record may represent an
    uncertain broker outcome.

    Replaying the same idempotency key must return
    that PENDING record and must not send another
    broker order. Reconciliation is responsible
    for resolving the uncertain execution.
    """

    session = SessionLocal()

    repository = ExecutionRepository(session)

    service = ExecutionService(repository)

    idempotency_key = create_idempotency_key(
        "pending-request"
    )

    request = ExecutionManager.prepare_execution(
        symbol="AUD/USD",
        direction="BUY",
        lot_size=0.30,
        approved=True,
    )

    request_fingerprint = (
        service._create_request_fingerprint(
            request
        )
    )

    pending_execution = (
        repository.save_execution(
            user_id=900003,
            symbol=request.symbol,
            direction=request.order_type,
            volume=request.volume,
            status="PENDING",
            broker_order_id=None,
            execution_message=(
                "Execution started. "
                "Awaiting broker result."
            ),
            idempotency_key=idempotency_key,
            request_fingerprint=(
                request_fingerprint
            ),
        )
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
            message="Should not execute.",
            order_id="SHOULD_NOT_EXIST",
        )

    monkeypatch.setattr(
        ExecutionManager,
        "execute_with_mt5",
        fake_execute_with_mt5,
    )

    replay_request = (
        ExecutionManager.prepare_execution(
            symbol="AUD/USD",
            direction="BUY",
            lot_size=0.30,
            approved=True,
        )
    )

    replay_execution = service.execute_trade(
        user_id=900003,
        execution_request=replay_request,
        idempotency_key=idempotency_key,
    )

    assert broker_called["value"] is False

    assert (
        replay_execution.id
        == pending_execution.id
    )

    assert (
        replay_execution.status
        == "PENDING"
    )

    assert replay_request.execution_id is None

    session.close()


def test_idempotency_key_reuse_with_different_payload_is_rejected(
    monkeypatch,
):
    """
    The same user must not reuse an idempotency
    key for a different broker execution payload.
    """

    session = SessionLocal()

    repository = ExecutionRepository(session)

    service = ExecutionService(repository)

    idempotency_key = create_idempotency_key(
        "conflict-request"
    )

    broker_call_count = {
        "value": 0,
    }

    def fake_execute_with_mt5(
        execution_request
    ):
        broker_call_count["value"] += 1

        return MT5ExecutionResult(
            success=True,
            message="Initial execution completed.",
            order_id="CONFLICT_TEST_ORDER",
        )

    monkeypatch.setattr(
        ExecutionManager,
        "execute_with_mt5",
        fake_execute_with_mt5,
    )

    first_request = (
        ExecutionManager.prepare_execution(
            symbol="USD/JPY",
            direction="BUY",
            lot_size=0.10,
            approved=True,
        )
    )

    service.execute_trade(
        user_id=900004,
        execution_request=first_request,
        idempotency_key=idempotency_key,
    )

    different_request = (
        ExecutionManager.prepare_execution(
            symbol="USD/JPY",
            direction="BUY",
            lot_size=0.20,
            approved=True,
        )
    )

    with pytest.raises(
        ExecutionIdempotencyConflictError,
        match=(
            "idempotency key has already been used"
        ),
    ):
        service.execute_trade(
            user_id=900004,
            execution_request=different_request,
            idempotency_key=idempotency_key,
        )

    assert broker_call_count["value"] == 1

    session.close()


def test_same_idempotency_key_is_allowed_for_different_users(
    monkeypatch,
):
    """
    Idempotency keys are scoped by authenticated
    user identity.

    Two different users may therefore use the same
    key without sharing execution records.
    """

    session = SessionLocal()

    repository = ExecutionRepository(session)

    service = ExecutionService(repository)

    idempotency_key = create_idempotency_key(
        "different-users"
    )

    broker_call_count = {
        "value": 0,
    }

    def fake_execute_with_mt5(
        execution_request
    ):
        broker_call_count["value"] += 1

        return MT5ExecutionResult(
            success=True,
            message="User-specific execution.",
            order_id=(
                f"USER_ORDER_"
                f"{broker_call_count['value']}"
            ),
        )

    monkeypatch.setattr(
        ExecutionManager,
        "execute_with_mt5",
        fake_execute_with_mt5,
    )

    first_request = (
        ExecutionManager.prepare_execution(
            symbol="EUR/USD",
            direction="BUY",
            lot_size=0.10,
            approved=True,
        )
    )

    first_execution = service.execute_trade(
        user_id=900005,
        execution_request=first_request,
        idempotency_key=idempotency_key,
    )

    second_request = (
        ExecutionManager.prepare_execution(
            symbol="EUR/USD",
            direction="BUY",
            lot_size=0.10,
            approved=True,
        )
    )

    second_execution = service.execute_trade(
        user_id=900006,
        execution_request=second_request,
        idempotency_key=idempotency_key,
    )

    assert broker_call_count["value"] == 2

    assert (
        first_execution.id
        != second_execution.id
    )

    assert (
        first_execution.user_id
        != second_execution.user_id
    )

    assert (
        first_execution.idempotency_key
        == second_execution.idempotency_key
        == idempotency_key
    )

    session.close()