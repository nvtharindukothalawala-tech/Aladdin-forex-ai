"""
test_execution_security.py

Security tests for execution API ownership.

These tests verify that execution endpoints
require authentication and prevent one user
from accessing or executing under another
user's ID.

No real MT5 broker calls are made.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.main import app
from app.auth.dependencies import get_current_user


client = TestClient(app)


# ==========================================
# Helpers
# ==========================================


def install_authenticated_user(
    user_id: int = 1,
):
    """
    Override authentication with a
    deterministic authenticated user.
    """

    app.dependency_overrides[
        get_current_user
    ] = lambda: SimpleNamespace(
        id=user_id,
    )


def remove_authenticated_user():
    """
    Remove the authentication override.
    """

    app.dependency_overrides.pop(
        get_current_user,
        None,
    )


def valid_execution_request(
    user_id: int,
):
    """
    Return a valid direct-execution payload.
    """

    return {
        "user_id": user_id,
        "symbol": "EUR/USD",
        "direction": "BUY",
        "volume": 0.10,
        "approved": True,
    }


def valid_ai_execution_request(
    user_id: int,
):
    """
    Return a valid AI-execution payload.
    """

    return {
        "user_id": user_id,
        "symbol": "EUR/USD",
        "ema_signal": "BULLISH",
        "rsi_value": 65,
        "adx_value": 30,
        "volatility": "NORMAL",
        "currency": "USD",
        "event_type": (
            "Interest Rate Decision"
        ),
        "importance": "HIGH",
        "sentiment": "BULLISH",
        "price_structure": (
            "BOS_BULLISH"
        ),
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
    }


# ==========================================
# Authentication Protection
# ==========================================


def test_execute_requires_authentication():
    """
    Direct execution must reject requests
    without a valid authenticated user.
    """

    remove_authenticated_user()

    response = client.post(
        "/execution/execute",
        json=valid_execution_request(
            user_id=1,
        ),
    )

    assert response.status_code == 401


def test_ai_execute_requires_authentication():
    """
    AI execution must reject requests
    without a valid authenticated user.
    """

    remove_authenticated_user()

    response = client.post(
        "/execution/ai-execute",
        json=valid_ai_execution_request(
            user_id=1,
        ),
    )

    assert response.status_code == 401


def test_execution_history_requires_authentication():
    """
    Execution history must not be available
    without authentication.
    """

    remove_authenticated_user()

    response = client.get(
        "/execution/history/1"
    )

    assert response.status_code == 401


def test_execution_statistics_requires_authentication():
    """
    Execution statistics must not be available
    without authentication.
    """

    remove_authenticated_user()

    response = client.get(
        "/execution/statistics/1"
    )

    assert response.status_code == 401


# ==========================================
# Ownership Protection
# ==========================================


def test_execute_rejects_other_user():
    """
    An authenticated user must not execute
    a trade using another user's ID.
    """

    install_authenticated_user(
        user_id=1,
    )

    try:
        response = client.post(
            "/execution/execute",
            json=valid_execution_request(
                user_id=2,
            ),
        )

        assert response.status_code == 403

        assert (
            response.json()["detail"]
            == (
                "You are not authorized to access "
                "execution data for this user."
            )
        )

    finally:
        remove_authenticated_user()


def test_ai_execute_rejects_other_user():
    """
    An authenticated user must not start
    an AI execution workflow under another
    user's ID.
    """

    install_authenticated_user(
        user_id=1,
    )

    try:
        response = client.post(
            "/execution/ai-execute",
            json=valid_ai_execution_request(
                user_id=2,
            ),
        )

        assert response.status_code == 403

        assert (
            response.json()["detail"]
            == (
                "You are not authorized to access "
                "execution data for this user."
            )
        )

    finally:
        remove_authenticated_user()


def test_execution_history_rejects_other_user():
    """
    An authenticated user must not read
    another user's execution history.
    """

    install_authenticated_user(
        user_id=1,
    )

    try:
        response = client.get(
            "/execution/history/2"
        )

        assert response.status_code == 403

        assert (
            response.json()["detail"]
            == (
                "You are not authorized to access "
                "execution data for this user."
            )
        )

    finally:
        remove_authenticated_user()


def test_execution_statistics_rejects_other_user():
    """
    An authenticated user must not read
    another user's execution statistics.
    """

    install_authenticated_user(
        user_id=1,
    )

    try:
        response = client.get(
            "/execution/statistics/2"
        )

        assert response.status_code == 403

        assert (
            response.json()["detail"]
            == (
                "You are not authorized to access "
                "execution data for this user."
            )
        )

    finally:
        remove_authenticated_user()