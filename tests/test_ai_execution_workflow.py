"""
test_ai_execution_workflow.py

Tests complete AI execution workflow.

Author: Tharindu Kothalwala
Project: Aladdin
"""

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


def test_ai_execution_workflow():

    session = SessionLocal()

    repository = ExecutionRepository(session)

    execution_service = ExecutionService(repository)

    result = TradingService.generate_ai_execution_workflow(
        symbol="EUR/USD",
        # ==========================
        # Technical Agent Inputs
        # ==========================
        ema_signal="BULLISH",
        rsi_value=65,
        adx_value=30,
        volatility="NORMAL",
        # ==========================
        # News Agent Inputs
        # ==========================
        currency="USD",
        event_type="Interest Rate Decision",
        importance="HIGH",
        sentiment="BULLISH",
        # ==========================
        # Market Structure Agent Inputs
        # ==========================
        price_structure="BOS_BULLISH",
        liquidity_sweep=True,
        order_block="BULLISH",
        fair_value_gap=True,
        # ==========================
        # Trade Parameters
        # ==========================
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1150,
        # ==========================
        # Risk Parameters
        # ==========================
        account_balance=10000,
        risk_percent=1,
        trade_risk_amount=100,
        lot_size=0.10,
        # ==========================
        # Execution
        # ==========================
        execute=True,
        execution_service=execution_service,
        user_id=1,
    )

    # AI Decision validation

    assert result["decision"].action == "BUY"

    # Risk approval validation

    assert result["approval"].approved is True

    # Execution validation

    assert "execution_result" in result

    assert result["execution_result"].status == "EXECUTED"

    assert result["execution_result"].broker_order_id == "MOCK_ORDER_001"

    # Database cleanup

    session.close()

from types import SimpleNamespace


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
        "reasoning": "Blocked by Decision Gate.",
    }

    monkeypatch.setattr(
        TradingService,
        "generate_ai_trade_setup",
        staticmethod(
            lambda **kwargs: fake_result
        ),
    )

    execution_service = FakeExecutionService()

    inputs = get_execution_inputs()

    inputs["execution_service"] = (
        execution_service
    )

    result = (
        TradingService.generate_ai_execution_workflow(
            **inputs
        )
    )

    assert result["decision"].action == "HOLD"
    assert result["decision"].approved is False

    assert execution_service.called is False

    assert "execution_result" not in result


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
        "reasoning": "Risk Gate rejected trade.",
    }

    monkeypatch.setattr(
        TradingService,
        "generate_ai_trade_setup",
        staticmethod(
            lambda **kwargs: fake_result
        ),
    )

    execution_service = FakeExecutionService()

    inputs = get_execution_inputs()

    inputs["execution_service"] = (
        execution_service
    )

    result = (
        TradingService.generate_ai_execution_workflow(
            **inputs
        )
    )

    assert result["decision"].action == "BUY"

    assert result["risk_gate"].approved is False

    assert execution_service.called is False

    assert "execution_result" not in result


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
        "reasoning": "Final approval rejected trade.",
    }

    monkeypatch.setattr(
        TradingService,
        "generate_ai_trade_setup",
        staticmethod(
            lambda **kwargs: fake_result
        ),
    )

    execution_service = FakeExecutionService()

    inputs = get_execution_inputs()

    inputs["execution_service"] = (
        execution_service
    )

    result = (
        TradingService.generate_ai_execution_workflow(
            **inputs
        )
    )

    assert result["decision"].approved is True

    assert result["risk_gate"].approved is True

    assert result["approval"].approved is False

    assert execution_service.called is False

    assert "execution_result" not in result