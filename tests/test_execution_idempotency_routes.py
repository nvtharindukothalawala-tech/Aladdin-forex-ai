"""
test_execution_idempotency_routes.py

API tests for duplicate execution protection.

These tests verify that execution idempotency works
through the FastAPI HTTP layer.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.auth.dependencies import get_current_user
from app.execution.execution_manager import (
    ExecutionManager,
)


client = TestClient(app)


# ==========================================
# Authentication Fixture
# ==========================================


@pytest.fixture(autouse=True)
def authenticated_execution_user():
    """
    Supply a deterministic authenticated user.

    Phase 7 idempotency tests use user_id=1.
    """

    app.dependency_overrides[
        get_current_user
    ] = lambda: SimpleNamespace(
        id=1,
    )

    yield

    app.dependency_overrides.pop(
        get_current_user,
        None,
    )


# ==========================================
# Helpers
# ==========================================


def create_idempotency_key(prefix):
    """
    Create a unique idempotency key so tests do not
    conflict with execution records left in the
    shared development test database.
    """

    return (
        f"{prefix}-{uuid4()}"
    )


# ==========================================
# Direct Execution Idempotency
# ==========================================


def test_direct_execution_replay_returns_existing_execution(
    monkeypatch,
):
    """
    Sending the same direct execution twice with the
    same idempotency key and payload must reuse the
    existing execution.

    The broker execution layer must only be contacted
    once.
    """

    broker_calls = {
        "count": 0,
    }

    original_execute = (
        ExecutionManager.execute_with_mt5
    )

    def counting_execute(
        execution_request,
    ):
        broker_calls["count"] += 1

        return original_execute(
            execution_request
        )

    monkeypatch.setattr(
        ExecutionManager,
        "execute_with_mt5",
        counting_execute,
    )

    idempotency_key = create_idempotency_key(
        "direct-replay"
    )

    payload = {
        "user_id": 1,
        "symbol": "EUR/USD",
        "direction": "BUY",
        "volume": 0.10,
        "approved": True,
        "idempotency_key": idempotency_key,
    }

    first_response = client.post(
        "/execution/execute",
        json=payload,
    )

    second_response = client.post(
        "/execution/execute",
        json=payload,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_data = first_response.json()
    second_data = second_response.json()

    assert first_data["status"] == "EXECUTED"
    assert second_data["status"] == "EXECUTED"

    assert (
        first_data["broker_order_id"]
        == second_data["broker_order_id"]
    )

    assert broker_calls["count"] == 1


def test_direct_execution_key_reuse_with_different_payload_returns_409():
    """
    Reusing an idempotency key for a different broker
    execution request must be rejected with HTTP 409.
    """

    idempotency_key = create_idempotency_key(
        "direct-conflict"
    )

    first_payload = {
        "user_id": 1,
        "symbol": "EUR/USD",
        "direction": "BUY",
        "volume": 0.10,
        "approved": True,
        "idempotency_key": idempotency_key,
    }

    second_payload = {
        "user_id": 1,
        "symbol": "EUR/USD",
        "direction": "BUY",
        "volume": 0.20,
        "approved": True,
        "idempotency_key": idempotency_key,
    }

    first_response = client.post(
        "/execution/execute",
        json=first_payload,
    )

    second_response = client.post(
        "/execution/execute",
        json=second_payload,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409

    data = second_response.json()

    assert "detail" in data


# ==========================================
# Idempotency Schema Validation
# ==========================================


def test_direct_execution_rejects_blank_idempotency_key():
    """
    A supplied idempotency key cannot contain only
    whitespace.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.10,
            "approved": True,
            "idempotency_key": "   ",
        },
    )

    assert response.status_code == 422


def test_direct_execution_rejects_too_long_idempotency_key():
    """
    Idempotency keys longer than 128 characters must
    be rejected by request validation.
    """

    response = client.post(
        "/execution/execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "direction": "BUY",
            "volume": 0.10,
            "approved": True,
            "idempotency_key": "x" * 129,
        },
    )

    assert response.status_code == 422


# ==========================================
# AI Execution Idempotency Forwarding
# ==========================================


def test_ai_execution_route_forwards_idempotency_key(
    monkeypatch,
):
    """
    Verify that /ai-execute forwards the client
    idempotency key into the AI execution workflow.

    The trading workflow itself is mocked here because
    service-level tests separately verify broker
    duplicate protection.
    """

    captured = {}

    expected_key = create_idempotency_key(
        "ai-forward"
    )

    def fake_workflow(**kwargs):
        captured["idempotency_key"] = (
            kwargs.get(
                "idempotency_key"
            )
        )

        return {
            "decision": {
                "action": "HOLD",
            },
        }

    monkeypatch.setattr(
        "app.api.routes.execution_routes."
        "TradingService.generate_ai_execution_workflow",
        fake_workflow,
    )

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
            "idempotency_key": expected_key,
        },
    )

    assert response.status_code == 200

    assert (
        captured["idempotency_key"]
        == expected_key
    )


def test_ai_execution_idempotency_conflict_returns_409(
    monkeypatch,
):
    """
    Verify that an idempotency conflict raised from
    the AI execution workflow becomes HTTP 409.
    """

    from app.services.execution_service import (
        ExecutionIdempotencyConflictError,
    )

    def conflicting_workflow(**kwargs):
        raise ExecutionIdempotencyConflictError(
            "Idempotency key was already used "
            "for a different execution request."
        )

    monkeypatch.setattr(
        "app.api.routes.execution_routes."
        "TradingService.generate_ai_execution_workflow",
        conflicting_workflow,
    )

    response = client.post(
        "/execution/ai-execute",
        json={
            "user_id": 1,
            "symbol": "EUR/USD",
            "ema_signal": "BULLISH",
            "rsi_value": 65,
            "adx_value": 30,
            "volatility": "NORMAL",
            "currency": "USD",
            "event_type": "Interest Rate Decision",
            "importance": "HIGH",
            "sentiment": "BULLISH",
            "price_structure": "BOS_BULLISH",
            "liquidity_sweep": True,
            "order_block": "BULLISH",
            "fair_value_gap": True,
            "entry_price": 1.1000,
            "stop_loss": 1.0950,
            "take_profit": 1.1150,
            "account_balance": 10000,
            "risk_percent": 1,
            "trade_risk_amount": 100,
            "lot_size": 0.10,
            "idempotency_key": create_idempotency_key(
                "ai-conflict"
            ),
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert "detail" in data