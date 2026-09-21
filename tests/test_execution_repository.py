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

import json

import pytest
from sqlalchemy.exc import IntegrityError

from app.execution.models import (
    ExecutionReconciliationAuditModel,
    ExecutionSafetyAuditModel,
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

# ======================================================
# EXECUTION SAFETY AUDIT TESTS
# ======================================================


def test_save_execution_safety_audit():
    """
    An approved deterministic safety decision can be
    persisted against an existing execution.
    """

    session = SessionLocal()
    repository = ExecutionRepository(session)

    test_user_id = (
        uuid4().int % 2_000_000_000
    ) + 1

    execution = None
    audit = None

    try:
        execution = repository.save_execution(
            user_id=test_user_id,
            symbol="EURUSD",
            direction="BUY",
            volume=0.10,
            status="PENDING",
        )

        checks = {
            "trade_setup_valid": True,
            "risk_approved": True,
            "spread_valid": True,
        }

        reasons = [
            "Trade setup approved.",
            "Risk validation approved.",
        ]

        limits = {
            "max_volume": 1.0,
            "max_spread_points": 30.0,
        }

        audit = repository.save_safety_audit(
            execution_id=execution.id,
            user_id=test_user_id,
            safety_status="APPROVED",
            safety_engine="DETERMINISTIC",
            execution_mode="MOCK",
            symbol="EURUSD",
            direction="BUY",
            volume=0.10,
            entry_price=1.1000,
            stop_loss=1.0950,
            take_profit=1.1100,
            checks_json=json.dumps(
                checks,
                sort_keys=True,
            ),
            reasons_json=json.dumps(
                reasons,
            ),
            limits_json=json.dumps(
                limits,
                sort_keys=True,
            ),
        )

        assert audit.id is not None

        assert (
            audit.execution_id
            == execution.id
        )

        assert (
            audit.user_id
            == test_user_id
        )

        assert (
            audit.safety_status
            == "APPROVED"
        )

        assert (
            audit.safety_engine
            == "DETERMINISTIC"
        )

        assert (
            audit.execution_mode
            == "MOCK"
        )

        assert audit.symbol == "EURUSD"
        assert audit.direction == "BUY"
        assert audit.volume == 0.10

        assert audit.entry_price == 1.1000
        assert audit.stop_loss == 1.0950
        assert audit.take_profit == 1.1100

        assert (
            json.loads(audit.checks_json)
            == checks
        )

        assert (
            json.loads(audit.reasons_json)
            == reasons
        )

        assert (
            json.loads(audit.limits_json)
            == limits
        )

        assert audit.created_at is not None

    finally:
        if audit is not None:
            session.delete(audit)

        if execution is not None:
            session.delete(execution)

        session.commit()
        session.close()


def test_get_safety_audit_by_execution_id():
    """
    Safety audit lookup returns the snapshot belonging
    to the requested execution.
    """

    session = SessionLocal()
    repository = ExecutionRepository(session)

    test_user_id = (
        uuid4().int % 2_000_000_000
    ) + 1

    execution = None
    audit = None

    try:
        execution = repository.save_execution(
            user_id=test_user_id,
            symbol="GBPUSD",
            direction="SELL",
            volume=0.20,
            status="PENDING",
        )

        audit = repository.save_safety_audit(
            execution_id=execution.id,
            user_id=test_user_id,
            safety_status="APPROVED",
            safety_engine="DETERMINISTIC",
            execution_mode="MOCK",
            symbol="GBPUSD",
            direction="SELL",
            volume=0.20,
            entry_price=1.2500,
            stop_loss=1.2550,
            take_profit=1.2400,
            checks_json=json.dumps(
                {"approved": True}
            ),
            reasons_json=json.dumps(
                ["Safety gate approved."]
            ),
            limits_json=json.dumps(
                {"max_volume": 1.0}
            ),
        )

        loaded_audit = (
            repository
            .get_safety_audit_by_execution_id(
                execution.id
            )
        )

        assert loaded_audit is not None

        assert loaded_audit.id == audit.id

        assert (
            loaded_audit.execution_id
            == execution.id
        )

        assert (
            loaded_audit.user_id
            == test_user_id
        )

        assert loaded_audit.symbol == "GBPUSD"

        assert (
            loaded_audit.direction
            == "SELL"
        )

    finally:
        if audit is not None:
            session.delete(audit)

        if execution is not None:
            session.delete(execution)

        session.commit()
        session.close()


def test_get_missing_safety_audit_returns_none():
    """
    An execution without a safety audit returns None.
    """

    session = SessionLocal()
    repository = ExecutionRepository(session)

    test_user_id = (
        uuid4().int % 2_000_000_000
    ) + 1

    execution = None

    try:
        execution = repository.save_execution(
            user_id=test_user_id,
            symbol="AUDUSD",
            direction="BUY",
            volume=0.05,
            status="PENDING",
        )

        audit = (
            repository
            .get_safety_audit_by_execution_id(
                execution.id
            )
        )

        assert audit is None

    finally:
        if execution is not None:
            session.delete(execution)

        session.commit()
        session.close()


def test_get_user_safety_audits_is_user_scoped():
    """
    Safety audit history must return only records
    belonging to the requested user.
    """

    session = SessionLocal()
    repository = ExecutionRepository(session)

    first_user_id = (
        uuid4().int % 1_000_000_000
    ) + 1

    second_user_id = (
        first_user_id
        + 1_000_000_000
    )

    executions = []
    audits = []

    try:
        first_execution = (
            repository.save_execution(
                user_id=first_user_id,
                symbol="EURUSD",
                direction="BUY",
                volume=0.10,
                status="PENDING",
            )
        )

        executions.append(first_execution)

        second_execution = (
            repository.save_execution(
                user_id=first_user_id,
                symbol="USDJPY",
                direction="SELL",
                volume=0.20,
                status="PENDING",
            )
        )

        executions.append(second_execution)

        other_execution = (
            repository.save_execution(
                user_id=second_user_id,
                symbol="GBPUSD",
                direction="BUY",
                volume=0.30,
                status="PENDING",
            )
        )

        executions.append(other_execution)

        for execution in executions:
            audit = repository.save_safety_audit(
                execution_id=execution.id,
                user_id=execution.user_id,
                safety_status="APPROVED",
                safety_engine="DETERMINISTIC",
                execution_mode="MOCK",
                symbol=execution.symbol,
                direction=execution.direction,
                volume=execution.volume,
                entry_price=1.1000,
                stop_loss=1.0950,
                take_profit=1.1100,
                checks_json=json.dumps(
                    {"approved": True}
                ),
                reasons_json=json.dumps(
                    ["Approved."]
                ),
                limits_json=json.dumps(
                    {"max_volume": 1.0}
                ),
            )

            audits.append(audit)

        user_audits = (
            repository.get_user_safety_audits(
                first_user_id
            )
        )

        assert len(user_audits) == 2

        assert all(
            audit.user_id
            == first_user_id
            for audit in user_audits
        )

        assert [
            audit.execution_id
            for audit in user_audits
        ] == [
            first_execution.id,
            second_execution.id,
        ]

    finally:
        for audit in audits:
            session.delete(audit)

        session.commit()

        for execution in executions:
            session.delete(execution)

        session.commit()
        session.close()


def test_count_user_safety_audits():
    """
    Safety audit count must be scoped to the
    requested user.
    """

    session = SessionLocal()
    repository = ExecutionRepository(session)

    test_user_id = (
        uuid4().int % 2_000_000_000
    ) + 1

    executions = []
    audits = []

    try:
        for index in range(2):
            execution = (
                repository.save_execution(
                    user_id=test_user_id,
                    symbol=(
                        "EURUSD"
                        if index == 0
                        else "GBPUSD"
                    ),
                    direction=(
                        "BUY"
                        if index == 0
                        else "SELL"
                    ),
                    volume=0.10,
                    status="PENDING",
                )
            )

            executions.append(execution)

            audit = (
                repository.save_safety_audit(
                    execution_id=execution.id,
                    user_id=test_user_id,
                    safety_status="APPROVED",
                    safety_engine="DETERMINISTIC",
                    execution_mode="MOCK",
                    symbol=execution.symbol,
                    direction=execution.direction,
                    volume=execution.volume,
                    entry_price=1.1000,
                    stop_loss=1.0950,
                    take_profit=1.1100,
                    checks_json="{}",
                    reasons_json="[]",
                    limits_json="{}",
                )
            )

            audits.append(audit)

        count = (
            repository.count_user_safety_audits(
                test_user_id
            )
        )

        assert count == 2

    finally:
        for audit in audits:
            session.delete(audit)

        session.commit()

        for execution in executions:
            session.delete(execution)

        session.commit()
        session.close()


def test_execution_allows_only_one_safety_audit():
    """
    The database must reject a second safety snapshot
    for the same execution.

    This protects the audit record from accidental
    replacement or duplication.
    """

    session = SessionLocal()
    repository = ExecutionRepository(session)

    test_user_id = (
        uuid4().int % 2_000_000_000
    ) + 1

    execution = None
    first_audit = None

    try:
        execution = repository.save_execution(
            user_id=test_user_id,
            symbol="EURUSD",
            direction="BUY",
            volume=0.10,
            status="PENDING",
        )

        first_audit = (
            repository.save_safety_audit(
                execution_id=execution.id,
                user_id=test_user_id,
                safety_status="APPROVED",
                safety_engine="DETERMINISTIC",
                execution_mode="MOCK",
                symbol="EURUSD",
                direction="BUY",
                volume=0.10,
                entry_price=1.1000,
                stop_loss=1.0950,
                take_profit=1.1100,
                checks_json="{}",
                reasons_json="[]",
                limits_json="{}",
            )
        )

        with pytest.raises(
            IntegrityError
        ):
            repository.save_safety_audit(
                execution_id=execution.id,
                user_id=test_user_id,
                safety_status="APPROVED",
                safety_engine="DETERMINISTIC",
                execution_mode="MOCK",
                symbol="EURUSD",
                direction="BUY",
                volume=0.10,
                entry_price=1.1000,
                stop_loss=1.0950,
                take_profit=1.1100,
                checks_json="{}",
                reasons_json="[]",
                limits_json="{}",
            )

        # save_safety_audit() rolls back the failed
        # transaction, so the first audit remains valid.
        loaded_audit = (
            repository
            .get_safety_audit_by_execution_id(
                execution.id
            )
        )

        assert loaded_audit is not None

        assert (
            loaded_audit.id
            == first_audit.id
        )

    finally:
        # Query again because rollback may expire
        # previously loaded ORM state.
        if execution is not None:
            stored_audit = (
                session.query(
                    ExecutionSafetyAuditModel
                )
                .filter(
                    ExecutionSafetyAuditModel.execution_id
                    == execution.id
                )
                .one_or_none()
            )

            if stored_audit is not None:
                session.delete(stored_audit)

            stored_execution = (
                session.get(
                    type(execution),
                    execution.id,
                )
            )

            if stored_execution is not None:
                session.delete(stored_execution)

        session.commit()
        session.close()

# ======================================================
# EXECUTION RECONCILIATION AUDIT TESTS
# ======================================================


def test_save_execution_reconciliation_audit():
    """
    One reconciliation outcome can be persisted
    against an existing execution.
    """

    session = SessionLocal()
    repository = ExecutionRepository(session)

    test_user_id = (
        uuid4().int % 2_000_000_000
    ) + 1

    execution = None
    audit = None

    try:
        execution = repository.save_execution(
            user_id=test_user_id,
            symbol="EURUSD",
            direction="BUY",
            volume=0.10,
            status="PENDING",
        )

        details = {
            "errors": [
                "Symbol does not match.",
            ],
        }

        audit = (
            repository.save_reconciliation_audit(
                execution_id=execution.id,
                user_id=test_user_id,
                outcome="CONFLICT",
                reason=(
                    "Broker evidence did not match "
                    "the local execution."
                ),
                evidence_source="OPEN_POSITION",
                broker_order_id="123456",
                symbol="EURUSD",
                direction="BUY",
                volume=0.10,
                details_json=json.dumps(
                    details,
                    sort_keys=True,
                ),
            )
        )

        assert audit.id is not None
        assert audit.execution_id == execution.id
        assert audit.user_id == test_user_id
        assert audit.outcome == "CONFLICT"

        assert audit.reason == (
            "Broker evidence did not match "
            "the local execution."
        )

        assert (
            audit.evidence_source
            == "OPEN_POSITION"
        )

        assert audit.broker_order_id == "123456"
        assert audit.symbol == "EURUSD"
        assert audit.direction == "BUY"
        assert audit.volume == 0.10

        assert (
            json.loads(audit.details_json)
            == details
        )

        assert audit.created_at is not None

    finally:
        if audit is not None:
            session.delete(audit)

        if execution is not None:
            session.delete(execution)

        session.commit()
        session.close()


def test_reconciliation_allows_multiple_audits_per_execution():
    """
    Reconciliation history is append-only.

    The same execution may be checked repeatedly
    while it remains unresolved.
    """

    session = SessionLocal()
    repository = ExecutionRepository(session)

    test_user_id = (
        uuid4().int % 2_000_000_000
    ) + 1

    execution = None
    audits = []

    try:
        execution = repository.save_execution(
            user_id=test_user_id,
            symbol="EURUSD",
            direction="BUY",
            volume=0.10,
            status="PENDING",
        )

        first_audit = (
            repository.save_reconciliation_audit(
                execution_id=execution.id,
                user_id=test_user_id,
                outcome="UNMATCHED",
                reason=(
                    "No exact MT5 broker "
                    "correlation was found."
                ),
                evidence_source=None,
                broker_order_id=None,
                symbol=execution.symbol,
                direction=execution.direction,
                volume=execution.volume,
                details_json="{}",
            )
        )

        audits.append(first_audit)

        second_audit = (
            repository.save_reconciliation_audit(
                execution_id=execution.id,
                user_id=test_user_id,
                outcome="CONFLICT",
                reason=(
                    "Execution safety audit "
                    "is missing."
                ),
                evidence_source="OPEN_POSITION",
                broker_order_id="123456",
                symbol=execution.symbol,
                direction=execution.direction,
                volume=execution.volume,
                details_json="{}",
            )
        )

        audits.append(second_audit)

        loaded = (
            repository
            .get_reconciliation_audits_by_execution_id(
                execution.id
            )
        )

        assert len(loaded) == 2

        assert [
            item.id
            for item in loaded
        ] == [
            first_audit.id,
            second_audit.id,
        ]

        assert [
            item.outcome
            for item in loaded
        ] == [
            "UNMATCHED",
            "CONFLICT",
        ]

    finally:
        for audit in audits:
            session.delete(audit)

        session.commit()

        if execution is not None:
            session.delete(execution)

        session.commit()
        session.close()


def test_get_user_reconciliation_audits_is_user_scoped():
    """
    Reconciliation history must not leak records
    belonging to another user.
    """

    session = SessionLocal()
    repository = ExecutionRepository(session)

    first_user_id = (
        uuid4().int % 1_000_000_000
    ) + 1

    second_user_id = (
        first_user_id
        + 1_000_000_000
    )

    executions = []
    audits = []

    try:
        for user_id, symbol in (
            (first_user_id, "EURUSD"),
            (first_user_id, "GBPUSD"),
            (second_user_id, "USDJPY"),
        ):
            execution = repository.save_execution(
                user_id=user_id,
                symbol=symbol,
                direction="BUY",
                volume=0.10,
                status="PENDING",
            )

            executions.append(execution)

            audit = (
                repository.save_reconciliation_audit(
                    execution_id=execution.id,
                    user_id=user_id,
                    outcome="UNMATCHED",
                    reason=(
                        "No exact MT5 broker "
                        "correlation was found."
                    ),
                    evidence_source=None,
                    broker_order_id=None,
                    symbol=execution.symbol,
                    direction=execution.direction,
                    volume=execution.volume,
                    details_json="{}",
                )
            )

            audits.append(audit)

        user_audits = (
            repository
            .get_user_reconciliation_audits(
                first_user_id
            )
        )

        assert len(user_audits) == 2

        assert all(
            audit.user_id == first_user_id
            for audit in user_audits
        )

        assert [
            audit.execution_id
            for audit in user_audits
        ] == [
            executions[0].id,
            executions[1].id,
        ]

    finally:
        for audit in audits:
            session.delete(audit)

        session.commit()

        for execution in executions:
            session.delete(execution)

        session.commit()
        session.close()


def test_count_user_reconciliation_audits():
    """
    Reconciliation audit count must be scoped
    to the requested user.
    """

    session = SessionLocal()
    repository = ExecutionRepository(session)

    test_user_id = (
        uuid4().int % 2_000_000_000
    ) + 1

    execution = None
    audits = []

    try:
        execution = repository.save_execution(
            user_id=test_user_id,
            symbol="EURUSD",
            direction="BUY",
            volume=0.10,
            status="PENDING",
        )

        for outcome in (
            "UNMATCHED",
            "CONFLICT",
        ):
            audit = (
                repository.save_reconciliation_audit(
                    execution_id=execution.id,
                    user_id=test_user_id,
                    outcome=outcome,
                    reason="Test reconciliation outcome.",
                    evidence_source=None,
                    broker_order_id=None,
                    symbol=execution.symbol,
                    direction=execution.direction,
                    volume=execution.volume,
                    details_json="{}",
                )
            )

            audits.append(audit)

        count = (
            repository
            .count_user_reconciliation_audits(
                test_user_id
            )
        )

        assert count == 2

    finally:
        for audit in audits:
            session.delete(audit)

        session.commit()

        if execution is not None:
            session.delete(execution)

        session.commit()
        session.close()