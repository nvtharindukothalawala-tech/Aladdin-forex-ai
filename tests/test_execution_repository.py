"""
test_execution_repository.py

Tests execution repository.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from uuid import uuid4

from app.database.connection import SessionLocal

from app.execution.repository import (
    ExecutionRepository,
)


def test_save_execution():

    session = SessionLocal()

    repository = ExecutionRepository(session)

    execution = repository.save_execution(
        user_id=1,
        symbol="EUR/USD",
        direction="BUY",
        volume=0.10,
        status="EXECUTED",
        broker_order_id="MOCK_ORDER_001",
    )

    assert execution.symbol == "EUR/USD"

    assert execution.direction == "BUY"

    assert execution.volume == 0.10

    assert execution.status == "EXECUTED"

    assert execution.broker_order_id == "MOCK_ORDER_001"

    session.close()


def test_update_pending_execution_to_executed():

    session = SessionLocal()

    repository = ExecutionRepository(session)

    execution = repository.save_execution(
        user_id=1,
        symbol="EUR/USD",
        direction="BUY",
        volume=0.10,
        status="PENDING",
        broker_order_id=None,
        execution_message=(
            "Execution started. "
            "Awaiting broker result."
        ),
    )

    execution_id = execution.id

    execution = repository.update_execution(
        execution=execution,
        status="EXECUTED",
        broker_order_id="MOCK_ORDER_002",
        execution_message=(
            "Mock order executed successfully."
        ),
    )

    assert execution.id == execution_id

    assert execution.status == "EXECUTED"

    assert (
        execution.broker_order_id
        == "MOCK_ORDER_002"
    )

    assert (
        execution.execution_message
        == "Mock order executed successfully."
    )

    session.close()


def test_update_pending_execution_to_failed():

    session = SessionLocal()

    repository = ExecutionRepository(session)

    execution = repository.save_execution(
        user_id=1,
        symbol="GBP/USD",
        direction="SELL",
        volume=0.10,
        status="PENDING",
    )

    execution_id = execution.id

    execution = repository.update_execution(
        execution=execution,
        status="FAILED",
        broker_order_id=None,
        execution_message="Broker execution failed.",
    )

    assert execution.id == execution_id

    assert execution.status == "FAILED"

    assert execution.broker_order_id is None

    assert (
        execution.execution_message
        == "Broker execution failed."
    )

    session.close()


def test_get_user_executions():

    session = SessionLocal()

    repository = ExecutionRepository(session)

    executions = repository.get_user_executions(
        user_id=1
    )

    assert isinstance(
        executions,
        list,
    )

    session.close()


def test_get_pending_executions():

    session = SessionLocal()

    repository = ExecutionRepository(session)

    # Use a unique user ID so records left by
    # previous test runs cannot affect this test.
    test_user_id = (
        uuid4().int % 2_000_000_000
    ) + 1

    created_executions = []

    try:

        first_pending = (
            repository.save_execution(
                user_id=test_user_id,
                symbol="EURUSD",
                direction="BUY",
                volume=0.01,
                status="PENDING",
            )
        )

        created_executions.append(
            first_pending
        )

        executed = (
            repository.save_execution(
                user_id=test_user_id,
                symbol="GBPUSD",
                direction="SELL",
                volume=0.02,
                status="EXECUTED",
                broker_order_id="TEST_ORDER",
            )
        )

        created_executions.append(
            executed
        )

        second_pending = (
            repository.save_execution(
                user_id=test_user_id,
                symbol="USDJPY",
                direction="SELL",
                volume=0.03,
                status="PENDING",
            )
        )

        created_executions.append(
            second_pending
        )

        other_user_pending = (
            repository.save_execution(
                user_id=test_user_id + 1,
                symbol="AUDUSD",
                direction="BUY",
                volume=0.04,
                status="PENDING",
            )
        )

        created_executions.append(
            other_user_pending
        )

        executions = (
            repository
            .get_pending_executions(
                user_id=test_user_id
            )
        )

        assert len(executions) == 2

        assert (
            executions[0].id
            == first_pending.id
        )

        assert (
            executions[1].id
            == second_pending.id
        )

        assert all(
            execution.user_id
            == test_user_id
            for execution in executions
        )

        assert all(
            execution.status
            == "PENDING"
            for execution in executions
        )

    finally:

        for execution in created_executions:
            session.delete(execution)

        session.commit()

        session.close()


def test_count_user_executions():

    session = SessionLocal()

    repository = ExecutionRepository(session)

    count = repository.count_user_executions(
        user_id=1
    )

    assert count >= 0

    session.close()


def test_save_failed_execution():
    """
    Test that failed executions
    can be stored in history.
    """

    session = SessionLocal()

    repository = ExecutionRepository(session)

    execution = repository.save_execution(
        user_id=1,
        symbol="EUR/USD",
        direction="BUY",
        volume=0.10,
        status="FAILED",
        broker_order_id=None,
    )

    assert execution.status == "FAILED"

    assert execution.broker_order_id is None

    session.close()