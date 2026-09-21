"""
test_execution_reconciliation_service.py

Tests MT5 execution reconciliation.

These tests use fake broker evidence only.
No real MT5 account is accessed and no
real broker order is created or modified.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from types import SimpleNamespace

import pytest

from app.services.broker_service import (
    BrokerService,
)

from app.services.execution_reconciliation_service import (
    ExecutionReconciliationService,
)


class FakeExecutionRepository:
    """
    Minimal repository used for reconciliation
    unit tests.
    """

    def __init__(
        self,
        pending_executions=None,
    ):
        self.pending_executions = (
            pending_executions
            or []
        )

        self.updated_executions = []

    def get_safety_audit_by_execution_id(
        self,
        execution_id: int,
    ):
        """
        Return an APPROVED deterministic safety audit
        for existing reconciliation tests.

        Safety-gate tests can override this method on
        the repository instance to simulate missing or
        rejected audit records.
        """

        execution = next(
            (
                item
                for item in self.pending_executions
                if item.id == execution_id
            ),
            None,
        )

        if execution is None:
            return None

        return SimpleNamespace(
            execution_id=execution.id,
            user_id=execution.user_id,
            safety_status="APPROVED",
            safety_engine="DETERMINISTIC",
            execution_mode="DEMO",
            symbol=execution.symbol,
            direction=execution.direction,
            volume=execution.volume,
        )

    def get_pending_executions(
        self,
        user_id: int,
    ):
        return [
            execution
            for execution
            in self.pending_executions
            if execution.user_id == user_id
            and execution.status == "PENDING"
        ]

    def update_execution(
        self,
        execution,
        status: str,
        broker_order_id=None,
        execution_message=None,
    ):
        execution.status = status
        execution.broker_order_id = (
            broker_order_id
        )
        execution.execution_message = (
            execution_message
        )

        self.updated_executions.append(
            execution
        )

        return execution


def make_pending_execution(
    *,
    execution_id=849,
    user_id=1,
    symbol="EURUSD",
    direction="BUY",
    volume=0.01,
):
    """
    Create a lightweight PENDING execution.
    """

    return SimpleNamespace(
        id=execution_id,
        user_id=user_id,
        symbol=symbol,
        direction=direction,
        volume=volume,
        status="PENDING",
        broker_order_id=None,
        execution_message=(
            "Execution started. "
            "Awaiting broker result."
        ),
    )


def set_demo_mode(
    monkeypatch,
):
    """
    Force reconciliation tests into fake DEMO mode.
    """

    monkeypatch.setattr(
        BrokerService,
        "get_execution_mode",
        lambda: "DEMO",
    )


def test_extract_execution_id_from_exact_comment():
    """
    Deterministic execution comments should
    produce the embedded execution ID.
    """

    execution_id = (
        ExecutionReconciliationService
        .extract_execution_id(
            "ALADDIN E849"
        )
    )

    assert execution_id == 849


@pytest.mark.parametrize(
    "comment",
    [
        "",
        None,
        "ALADDIN DEMO",
        "ALADDIN",
        "E849",
        "ALADDIN E0",
        "ALADDIN E-1",
        "ALADDIN E849 EXTRA",
    ],
)
def test_extract_execution_id_rejects_invalid_comments(
    comment,
):
    """
    Legacy or malformed comments must not be
    used for deterministic reconciliation.
    """

    execution_id = (
        ExecutionReconciliationService
        .extract_execution_id(
            comment
        )
    )

    assert execution_id is None


def test_reconciliation_requires_demo_mode(
    monkeypatch,
):
    """
    MOCK mode must never claim that real MT5
    reconciliation occurred.
    """

    repository = (
        FakeExecutionRepository(
            [
                make_pending_execution()
            ]
        )
    )

    service = (
        ExecutionReconciliationService(
            repository
        )
    )

    monkeypatch.setattr(
        BrokerService,
        "get_execution_mode",
        lambda: "MOCK",
    )

    with pytest.raises(
        PermissionError,
        match=(
            "MT5 execution reconciliation "
            "requires DEMO mode."
        ),
    ):
        service.reconcile_pending_executions(
            user_id=1
        )

    assert (
        repository.updated_executions
        == []
    )


def test_reconciliation_returns_early_when_no_pending(
    monkeypatch,
):
    """
    If there are no PENDING executions,
    broker positions/history should not
    need to be loaded.
    """

    repository = (
        FakeExecutionRepository()
    )

    service = (
        ExecutionReconciliationService(
            repository
        )
    )

    set_demo_mode(
        monkeypatch
    )

    def fail_open_positions():
        raise AssertionError(
            "Broker positions should not "
            "be loaded."
        )

    def fail_trade_history(
        days=None,
    ):
        raise AssertionError(
            "Broker history should not "
            "be loaded."
        )

    monkeypatch.setattr(
        BrokerService,
        "get_open_positions",
        fail_open_positions,
    )

    monkeypatch.setattr(
        BrokerService,
        "get_trade_history",
        fail_trade_history,
    )

    result = (
        service
        .reconcile_pending_executions(
            user_id=1
        )
    )

    assert result[
        "scanned_pending"
    ] == 0

    assert result[
        "reconciled_count"
    ] == 0

    assert result[
        "unmatched_count"
    ] == 0

    assert result[
        "conflict_count"
    ] == 0


def test_reconciles_exact_open_position_match(
    monkeypatch,
):
    """
    An exact ALADDIN E<ID> open-position
    correlation with matching execution data
    should finalize the local record.
    """

    execution = make_pending_execution(
        execution_id=850
    )

    repository = (
        FakeExecutionRepository(
            [execution]
        )
    )

    service = (
        ExecutionReconciliationService(
            repository
        )
    )

    set_demo_mode(
        monkeypatch
    )

    monkeypatch.setattr(
        BrokerService,
        "get_open_positions",
        lambda: {
            "execution_mode": "DEMO",
            "connected": True,
            "position_count": 1,
            "total_profit": 0.0,
            "positions": [
                {
                    "ticket": 123456,
                    "identifier": 654321,
                    "symbol": "EURUSD",
                    "direction": "BUY",
                    "volume": 0.01,
                    "comment": (
                        "ALADDIN E850"
                    ),
                }
            ],
        },
    )

    monkeypatch.setattr(
        BrokerService,
        "get_trade_history",
        lambda days=None: {
            "execution_mode": "DEMO",
            "connected": True,
            "history_days": days,
            "closed_trade_count": 0,
            "closed_trades": [],
        },
    )

    result = (
        service
        .reconcile_pending_executions(
            user_id=1
        )
    )

    assert result[
        "scanned_pending"
    ] == 1

    assert result[
        "reconciled_count"
    ] == 1

    assert result[
        "unmatched_count"
    ] == 0

    assert result[
        "conflict_count"
    ] == 0

    assert execution.status == "EXECUTED"

    assert (
        execution.broker_order_id
        == "123456"
    )

    assert (
        result["reconciled"][0][
            "evidence_source"
        ]
        == "OPEN_POSITION"
    )


def test_reconciles_closed_trade_using_opening_order_ticket(
    monkeypatch,
):
    """
    Completed MT5 history should restore the
    original opening order ticket rather than
    the final closing order ticket.
    """

    execution = make_pending_execution(
        execution_id=851,
        symbol="GBPUSD",
        direction="SELL",
        volume=0.02,
    )

    repository = (
        FakeExecutionRepository(
            [execution]
        )
    )

    service = (
        ExecutionReconciliationService(
            repository
        )
    )

    set_demo_mode(
        monkeypatch
    )

    monkeypatch.setattr(
        BrokerService,
        "get_open_positions",
        lambda: {
            "execution_mode": "DEMO",
            "connected": True,
            "position_count": 0,
            "positions": [],
        },
    )

    monkeypatch.setattr(
        BrokerService,
        "get_trade_history",
        lambda days=None: {
            "execution_mode": "DEMO",
            "connected": True,
            "history_days": days,
            "closed_trade_count": 1,
            "closed_trades": [
                {
                    "deal_ticket": 9004,
                    "order_ticket": 9003,
                    "opening_deal_ticket": 9001,
                    "opening_order_ticket": 9002,
                    "position_id": 9005,
                    "symbol": "GBPUSD",
                    "direction": "SELL",
                    "volume": 0.02,
                    "comment": (
                        "ALADDIN E851"
                    ),
                }
            ],
        },
    )

    result = (
        service
        .reconcile_pending_executions(
            user_id=1
        )
    )

    assert result[
        "reconciled_count"
    ] == 1

    assert execution.status == "EXECUTED"

    assert (
        execution.broker_order_id
        == "9002"
    )

    assert (
        execution.broker_order_id
        != "9003"
    )

    assert (
        result["reconciled"][0][
            "evidence_source"
        ]
        == "CLOSED_TRADE"
    )


def test_closed_trade_uses_opening_deal_ticket_as_fallback(
    monkeypatch,
):
    """
    If the opening order ticket is unavailable,
    the opening deal ticket should be used.
    """

    execution = make_pending_execution(
        execution_id=852
    )

    repository = (
        FakeExecutionRepository(
            [execution]
        )
    )

    service = (
        ExecutionReconciliationService(
            repository
        )
    )

    set_demo_mode(
        monkeypatch
    )

    monkeypatch.setattr(
        BrokerService,
        "get_open_positions",
        lambda: {
            "execution_mode": "DEMO",
            "connected": True,
            "position_count": 0,
            "positions": [],
        },
    )

    monkeypatch.setattr(
        BrokerService,
        "get_trade_history",
        lambda days=None: {
            "execution_mode": "DEMO",
            "connected": True,
            "history_days": days,
            "closed_trade_count": 1,
            "closed_trades": [
                {
                    "deal_ticket": 9104,
                    "order_ticket": 9103,
                    "opening_deal_ticket": 9101,
                    "opening_order_ticket": None,
                    "position_id": 9105,
                    "symbol": "EURUSD",
                    "direction": "BUY",
                    "volume": 0.01,
                    "comment": (
                        "ALADDIN E852"
                    ),
                }
            ],
        },
    )

    result = (
        service
        .reconcile_pending_executions(
            user_id=1
        )
    )

    assert result[
        "reconciled_count"
    ] == 1

    assert (
        execution.broker_order_id
        == "9101"
    )


def test_unmatched_execution_remains_pending(
    monkeypatch,
):
    """
    Missing broker evidence must not convert
    a PENDING execution into FAILED.
    """

    execution = make_pending_execution(
        execution_id=853
    )

    repository = (
        FakeExecutionRepository(
            [execution]
        )
    )

    service = (
        ExecutionReconciliationService(
            repository
        )
    )

    set_demo_mode(
        monkeypatch
    )

    monkeypatch.setattr(
        BrokerService,
        "get_open_positions",
        lambda: {
            "execution_mode": "DEMO",
            "connected": True,
            "position_count": 0,
            "positions": [],
        },
    )

    monkeypatch.setattr(
        BrokerService,
        "get_trade_history",
        lambda days=None: {
            "execution_mode": "DEMO",
            "connected": True,
            "history_days": days,
            "closed_trade_count": 0,
            "closed_trades": [],
        },
    )

    result = (
        service
        .reconcile_pending_executions(
            user_id=1
        )
    )

    assert result[
        "reconciled_count"
    ] == 0

    assert result[
        "unmatched_count"
    ] == 1

    assert result[
        "conflict_count"
    ] == 0

    assert execution.status == "PENDING"

    assert execution.broker_order_id is None

    assert (
        repository.updated_executions
        == []
    )


def test_mismatched_broker_data_remains_pending(
    monkeypatch,
):
    """
    The execution ID alone is not enough.
    Symbol, direction, and volume must also
    agree with the local execution.
    """

    execution = make_pending_execution(
        execution_id=854,
        symbol="EURUSD",
        direction="BUY",
        volume=0.01,
    )

    repository = (
        FakeExecutionRepository(
            [execution]
        )
    )

    service = (
        ExecutionReconciliationService(
            repository
        )
    )

    set_demo_mode(
        monkeypatch
    )

    monkeypatch.setattr(
        BrokerService,
        "get_open_positions",
        lambda: {
            "execution_mode": "DEMO",
            "connected": True,
            "position_count": 1,
            "positions": [
                {
                    "ticket": 9201,
                    "identifier": 9202,
                    "symbol": "GBPUSD",
                    "direction": "SELL",
                    "volume": 0.50,
                    "comment": (
                        "ALADDIN E854"
                    ),
                }
            ],
        },
    )

    monkeypatch.setattr(
        BrokerService,
        "get_trade_history",
        lambda days=None: {
            "execution_mode": "DEMO",
            "connected": True,
            "history_days": days,
            "closed_trade_count": 0,
            "closed_trades": [],
        },
    )

    result = (
        service
        .reconcile_pending_executions(
            user_id=1
        )
    )

    assert result[
        "reconciled_count"
    ] == 0

    assert result[
        "unmatched_count"
    ] == 0

    assert result[
        "conflict_count"
    ] == 1

    assert execution.status == "PENDING"

    assert (
        repository.updated_executions
        == []
    )

    errors = (
        result["conflicts"][0][
            "errors"
        ]
    )

    assert (
        "Symbol does not match."
        in errors
    )

    assert (
        "Direction does not match."
        in errors
    )

    assert (
        "Volume does not match."
        in errors
    )


def test_duplicate_execution_correlation_is_conflict(
    monkeypatch,
):
    """
    Multiple broker evidence records using the
    same execution ID must be treated as
    ambiguous and left PENDING.
    """

    execution = make_pending_execution(
        execution_id=855
    )

    repository = (
        FakeExecutionRepository(
            [execution]
        )
    )

    service = (
        ExecutionReconciliationService(
            repository
        )
    )

    set_demo_mode(
        monkeypatch
    )

    monkeypatch.setattr(
        BrokerService,
        "get_open_positions",
        lambda: {
            "execution_mode": "DEMO",
            "connected": True,
            "position_count": 1,
            "positions": [
                {
                    "ticket": 9301,
                    "identifier": 9302,
                    "symbol": "EURUSD",
                    "direction": "BUY",
                    "volume": 0.01,
                    "comment": (
                        "ALADDIN E855"
                    ),
                }
            ],
        },
    )

    monkeypatch.setattr(
        BrokerService,
        "get_trade_history",
        lambda days=None: {
            "execution_mode": "DEMO",
            "connected": True,
            "history_days": days,
            "closed_trade_count": 1,
            "closed_trades": [
                {
                    "deal_ticket": 9306,
                    "order_ticket": 9305,
                    "opening_deal_ticket": 9303,
                    "opening_order_ticket": 9304,
                    "position_id": 9302,
                    "symbol": "EURUSD",
                    "direction": "BUY",
                    "volume": 0.01,
                    "comment": (
                        "ALADDIN E855"
                    ),
                }
            ],
        },
    )

    result = (
        service
        .reconcile_pending_executions(
            user_id=1
        )
    )

    assert result[
        "reconciled_count"
    ] == 0

    assert result[
        "conflict_count"
    ] == 1

    assert (
        result["conflicts"][0][
            "evidence_count"
        ]
        == 2
    )

    assert execution.status == "PENDING"

    assert (
        repository.updated_executions
        == []
    )


def test_legacy_aladdin_comment_is_not_reconciled(
    monkeypatch,
):
    """
    Old ALADDIN DEMO trades predate deterministic
    execution correlation and must not be guessed.
    """

    execution = make_pending_execution(
        execution_id=848
    )

    repository = (
        FakeExecutionRepository(
            [execution]
        )
    )

    service = (
        ExecutionReconciliationService(
            repository
        )
    )

    set_demo_mode(
        monkeypatch
    )

    monkeypatch.setattr(
        BrokerService,
        "get_open_positions",
        lambda: {
            "execution_mode": "DEMO",
            "connected": True,
            "position_count": 1,
            "positions": [
                {
                    "ticket": 9401,
                    "identifier": 9402,
                    "symbol": "EURUSD",
                    "direction": "BUY",
                    "volume": 0.01,
                    "comment": (
                        "ALADDIN DEMO"
                    ),
                }
            ],
        },
    )

    monkeypatch.setattr(
        BrokerService,
        "get_trade_history",
        lambda days=None: {
            "execution_mode": "DEMO",
            "connected": True,
            "history_days": days,
            "closed_trade_count": 0,
            "closed_trades": [],
        },
    )

    result = (
        service
        .reconcile_pending_executions(
            user_id=1
        )
    )

    assert result[
        "reconciled_count"
    ] == 0

    assert result[
        "unmatched_count"
    ] == 1

    assert execution.status == "PENDING"

    assert (
        repository.updated_executions
        == []
    )

# ============================================================
# SAFETY AUDIT RECONCILIATION GATE
# ============================================================


def _set_single_open_position_evidence(
    monkeypatch,
    *,
    execution_id: int,
    ticket: int,
):
    monkeypatch.setattr(
        BrokerService,
        "get_open_positions",
        lambda: {
            "execution_mode": "DEMO",
            "connected": True,
            "position_count": 1,
            "positions": [
                {
                    "ticket": ticket,
                    "identifier": ticket + 1,
                    "symbol": "EURUSD",
                    "direction": "BUY",
                    "volume": 0.01,
                    "comment": f"ALADDIN E{execution_id}",
                }
            ],
        },
    )

    monkeypatch.setattr(
        BrokerService,
        "get_trade_history",
        lambda days=None: {
            "execution_mode": "DEMO",
            "connected": True,
            "history_days": days,
            "closed_trade_count": 0,
            "closed_trades": [],
        },
    )


def test_reconciliation_requires_safety_audit(monkeypatch):
    execution = make_pending_execution(execution_id=856)
    repository = FakeExecutionRepository([execution])
    repository.get_safety_audit_by_execution_id = lambda execution_id: None
    service = ExecutionReconciliationService(repository)
    set_demo_mode(monkeypatch)
    _set_single_open_position_evidence(
        monkeypatch, execution_id=856, ticket=9501
    )

    result = service.reconcile_pending_executions(user_id=1)

    assert result["reconciled_count"] == 0
    assert result["conflict_count"] == 1
    assert execution.status == "PENDING"
    assert repository.updated_executions == []
    assert result["conflicts"][0]["reason"] == (
        "Execution safety audit is missing. "
        "Reconciliation was blocked."
    )


def test_reconciliation_requires_approved_safety_audit(monkeypatch):
    execution = make_pending_execution(execution_id=857)
    repository = FakeExecutionRepository([execution])
    repository.get_safety_audit_by_execution_id = (
        lambda execution_id: SimpleNamespace(
            execution_id=execution_id,
            user_id=1,
            safety_status="REJECTED",
            safety_engine="DETERMINISTIC",
            execution_mode="DEMO",
            symbol="EURUSD",
            direction="BUY",
            volume=0.01,
        )
    )
    service = ExecutionReconciliationService(repository)
    set_demo_mode(monkeypatch)
    _set_single_open_position_evidence(
        monkeypatch, execution_id=857, ticket=9601
    )

    result = service.reconcile_pending_executions(user_id=1)

    assert result["reconciled_count"] == 0
    assert result["conflict_count"] == 1
    assert execution.status == "PENDING"
    assert repository.updated_executions == []
    assert result["conflicts"][0]["reason"] == (
        "Execution safety audit does not contain "
        "an approved safety decision."
    )


def test_reconciliation_with_approved_safety_audit(monkeypatch):
    execution = make_pending_execution(execution_id=858)
    repository = FakeExecutionRepository([execution])
    service = ExecutionReconciliationService(repository)
    set_demo_mode(monkeypatch)
    _set_single_open_position_evidence(
        monkeypatch, execution_id=858, ticket=9701
    )

    result = service.reconcile_pending_executions(user_id=1)

    assert result["reconciled_count"] == 1
    assert result["conflict_count"] == 0
    assert execution.status == "EXECUTED"
    assert execution.broker_order_id == "9701"
