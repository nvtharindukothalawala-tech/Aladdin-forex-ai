"""
test_execution_repository.py

Tests execution repository.

Author: Tharindu Kothalwala
Project: Aladdin
"""

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


def test_get_user_executions():

    session = SessionLocal()

    repository = ExecutionRepository(session)

    executions = repository.get_user_executions(user_id=1)

    assert isinstance(
        executions,
        list,
    )

    session.close()


def test_count_user_executions():

    session = SessionLocal()

    repository = ExecutionRepository(session)

    count = repository.count_user_executions(user_id=1)

    assert count >= 0

    session.close()
