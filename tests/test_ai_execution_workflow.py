"""
test_ai_execution_workflow.py

Tests complete AI execution workflow.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from types import SimpleNamespace

from app.database.connection import SessionLocal

from app.execution.repository import (
    ExecutionRepository,
)

from app.services.execution_service import (
    ExecutionService,
)

from app.services.trading_service import (
    TradingService,
)

from app.planning.trade_plan import (
    TradePlan,
)


def get_execution_inputs():
    """
    Common inputs for deterministic
    execution safety tests.
    """

    return {
        "symbol": "EUR/USD",
        "ema_signal": "NEUTRAL",
        "rsi_value": 50,
        "adx_value": 0,
        "volatility": "NORMAL",
        "currency": "EUR",
        "event_type": "Test Event",
        "importance": "LOW",
        "sentiment": "NEUTRAL",
        "price_structure": "BOS_BULLISH",
        "liquidity_sweep": False,
        "order_block": "BULLISH",
        "fair_value_gap": False,
        "entry_price": 1.1000,
        "stop_loss": 1.0950,
        "take_profit": 1.1100,
        "account_balance": 10000,
        "risk_percent": 1,
        "trade_risk_amount": 50,
        "lot_size": 0.10,
        "execute": True,
        "user_id": 1,
    }


def test_ai_execution_workflow(
    monkeypatch,
):
    """
    Test a fully approved BUY trade
    reaches execution.

    Market intelligence is mocked so
    this test does not depend on live
    market conditions.
    """

    session = SessionLocal()

    repository = ExecutionRepository(
        session
    )

    execution_service = ExecutionService(
        repository
    )

    trade_plan = TradePlan(
        symbol="EUR/USD",
        direction="BUY",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1100,
        risk_reward=2.0,
    )

    fake_result = {
        "decision": SimpleNamespace(
            action="BUY",
            approved=True,
            decision_confidence=90,
        ),
        "trade_plan": trade_plan,
        "risk_gate": SimpleNamespace(
            approved=True,
        ),
        "risk_validation": SimpleNamespace(
            approved=True,
        ),
        "approval": SimpleNamespace(
            approved=True,
        ),
        "reasoning": (
            "Approved deterministic "
            "test trade."
        ),
    }

    monkeypatch.setattr(
        TradingService,
        "generate_ai_trade_setup",
        staticmethod(
            lambda **kwargs: fake_result
        ),
    )

    inputs = get_execution_inputs()

    inputs["execution_service"] = (
        execution_service
    )

    result = (
        TradingService.generate_ai_execution_workflow(
            **inputs
        )
    )

    # ==========================================
    # Decision Validation
    # ==========================================

    assert (
        result["decision"].action
        == "BUY"
    )

    assert (
        result["decision"].approved
        is True
    )

    # ==========================================
    # Risk Validation
    # ==========================================

    assert (
        result["risk_gate"].approved
        is True
    )

    assert (
        result["approval"].approved
        is True
    )

    # ==========================================
    # Execution Request Validation
    # ==========================================

    assert "execution" in result

    assert (
        result["execution"].symbol
        == "EUR/USD"
    )

    assert (
        result["execution"].order_type
        == "BUY"
    )

    assert (
        result["execution"].volume
        == 0.10
    )

    assert (
        result["execution"].entry_price
        == 1.1000
    )

    assert (
        result["execution"].stop_loss
        == 1.0950
    )

    assert (
        result["execution"].take_profit
        == 1.1100
    )

    # ==========================================
    # Execution Result Validation
    # ==========================================

    assert "execution_result" in result

    assert (
        result["execution_result"].status
        == "EXECUTED"
    )

    assert (
        result[
            "execution_result"
        ].broker_order_id
        == "MOCK_ORDER_001"
    )

    session.close()


class FakeExecutionService:
    """
    Fake execution service used to prove that
    blocked trades never reach execution.
    """

    def __init__(self):
        self.called = False

    def execute_trade(
        self,
        user_id,
        execution_request,
    ):
        self.called = True

        raise AssertionError(
            "Execution should not be reached."
        )


def test_blocked_decision_never_reaches_execution(
    monkeypatch,
):
    """
    A HOLD decision must never reach
    the execution service.
    """

    fake_result = {
        "decision": SimpleNamespace(
            action="HOLD",
            approved=False,
            decision_confidence=80,
        ),
        "risk_gate": SimpleNamespace(
            approved=True,
        ),
        "approval": SimpleNamespace(
            approved=True,
        ),
        "reasoning": (
            "Blocked by Decision Gate."
        ),
    }

    monkeypatch.setattr(
        TradingService,
        "generate_ai_trade_setup",
        staticmethod(
            lambda **kwargs: fake_result
        ),
    )

    execution_service = (
        FakeExecutionService()
    )

    inputs = get_execution_inputs()

    inputs["execution_service"] = (
        execution_service
    )

    result = (
        TradingService.generate_ai_execution_workflow(
            **inputs
        )
    )

    assert (
        result["decision"].action
        == "HOLD"
    )

    assert (
        result["decision"].approved
        is False
    )

    assert (
        execution_service.called
        is False
    )

    assert (
        "execution_result"
        not in result
    )


def test_failed_risk_gate_never_reaches_execution(
    monkeypatch,
):
    """
    Even with an approved BUY decision,
    a failed Risk Gate must stop execution.
    """

    fake_result = {
        "decision": SimpleNamespace(
            action="BUY",
            approved=True,
            decision_confidence=90,
        ),
        "risk_gate": SimpleNamespace(
            approved=False,
        ),
        "approval": SimpleNamespace(
            approved=True,
        ),
        "reasoning": (
            "Risk Gate rejected trade."
        ),
    }

    monkeypatch.setattr(
        TradingService,
        "generate_ai_trade_setup",
        staticmethod(
            lambda **kwargs: fake_result
        ),
    )

    execution_service = (
        FakeExecutionService()
    )

    inputs = get_execution_inputs()

    inputs["execution_service"] = (
        execution_service
    )

    result = (
        TradingService.generate_ai_execution_workflow(
            **inputs
        )
    )

    assert (
        result["decision"].action
        == "BUY"
    )

    assert (
        result["risk_gate"].approved
        is False
    )

    assert (
        execution_service.called
        is False
    )

    assert (
        "execution_result"
        not in result
    )


def test_failed_final_approval_never_reaches_execution(
    monkeypatch,
):
    """
    Decision Gate and Risk Gate may pass,
    but failed final approval must still
    prevent execution.
    """

    fake_result = {
        "decision": SimpleNamespace(
            action="BUY",
            approved=True,
            decision_confidence=90,
        ),
        "risk_gate": SimpleNamespace(
            approved=True,
        ),
        "approval": SimpleNamespace(
            approved=False,
        ),
        "reasoning": (
            "Final approval rejected trade."
        ),
    }

    monkeypatch.setattr(
        TradingService,
        "generate_ai_trade_setup",
        staticmethod(
            lambda **kwargs: fake_result
        ),
    )

    execution_service = (
        FakeExecutionService()
    )

    inputs = get_execution_inputs()

    inputs["execution_service"] = (
        execution_service
    )

    result = (
        TradingService.generate_ai_execution_workflow(
            **inputs
        )
    )

    assert (
        result["decision"].approved
        is True
    )

    assert (
        result["risk_gate"].approved
        is True
    )

    assert (
        result["approval"].approved
        is False
    )

    assert (
        execution_service.called
        is False
    )

    assert (
        "execution_result"
        not in result
    )