"""
test_execution_reconciliation_routes.py

Tests manual MT5 execution reconciliation API.

All broker reconciliation behavior is mocked.
These tests do not contact real MT5 and do not
open, modify, or close broker trades.

Execution reconciliation requires JWT
authentication and validates execution ownership.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.main import app

from app.services.execution_reconciliation_service import (
    ExecutionReconciliationService,
)


client = TestClient(app)


# ==========================================
# Authentication Helper
# ==========================================


def get_auth_context():
    """
    Create a unique test user and return
    authentication headers and the real
    database user ID.
    """

    unique_value = uuid4().hex

    username = (
        f"reconciliation_{unique_value}"
    )

    email = (
        f"reconciliation_{unique_value}"
        "@example.com"
    )

    password = "password123"

    register_response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )

    assert (
        register_response.status_code
        == 200
    )

    login_response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert (
        login_response.status_code
        == 200
    )

    token = (
        login_response
        .json()["access_token"]
    )

    headers = {
        "Authorization": (
            f"Bearer {token}"
        ),
    }

    me_response = client.get(
        "/auth/me",
        headers=headers,
    )

    assert (
        me_response.status_code
        == 200
    )

    user_id = (
        me_response
        .json()["id"]
    )

    return headers, user_id


# ==========================================
# Successful Reconciliation
# ==========================================


def test_reconciliation_api_returns_summary(
    monkeypatch,
):
    """
    Test successful manual reconciliation
    API response for the authenticated user.
    """

    headers, user_id = (
        get_auth_context()
    )

    captured = {
        "user_id": None,
        "days": None,
    }

    def fake_reconcile(
        self,
        user_id,
        days=30,
    ):
        captured["user_id"] = user_id
        captured["days"] = days

        return {
            "execution_mode": "DEMO",
            "history_days": days,
            "scanned_pending": 1,
            "reconciled_count": 1,
            "unmatched_count": 0,
            "conflict_count": 0,
            "reconciled": [
                {
                    "execution_id": 849,
                    "symbol": "EURUSD",
                    "direction": "BUY",
                    "volume": 0.01,
                    "broker_order_id": (
                        "123456"
                    ),
                    "evidence_source": (
                        "CLOSED_TRADE"
                    ),
                }
            ],
            "unmatched": [],
            "conflicts": [],
            "message": (
                "MT5 execution reconciliation "
                "finished successfully."
            ),
        }

    monkeypatch.setattr(
        ExecutionReconciliationService,
        "reconcile_pending_executions",
        fake_reconcile,
    )

    response = client.post(
        (
            "/execution/"
            f"reconcile-mt5/{user_id}"
            "?days=45"
        ),
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        captured["user_id"]
        == user_id
    )

    assert captured["days"] == 45

    assert (
        data["execution_mode"]
        == "DEMO"
    )

    assert data["history_days"] == 45

    assert (
        data["scanned_pending"]
        == 1
    )

    assert (
        data["reconciled_count"]
        == 1
    )

    assert (
        data["unmatched_count"]
        == 0
    )

    assert (
        data["conflict_count"]
        == 0
    )

    assert (
        data["reconciled"][0][
            "execution_id"
        ]
        == 849
    )

    assert (
        data["reconciled"][0][
            "broker_order_id"
        ]
        == "123456"
    )


def test_reconciliation_api_uses_default_days(
    monkeypatch,
):
    """
    Test that the API uses the default
    30-day broker history window.
    """

    headers, user_id = (
        get_auth_context()
    )

    captured = {
        "days": None,
    }

    def fake_reconcile(
        self,
        user_id,
        days=30,
    ):
        captured["days"] = days

        return {
            "execution_mode": "DEMO",
            "history_days": days,
            "scanned_pending": 0,
            "reconciled_count": 0,
            "unmatched_count": 0,
            "conflict_count": 0,
            "reconciled": [],
            "unmatched": [],
            "conflicts": [],
            "message": (
                "No PENDING executions "
                "require reconciliation."
            ),
        }

    monkeypatch.setattr(
        ExecutionReconciliationService,
        "reconcile_pending_executions",
        fake_reconcile,
    )

    response = client.post(
        (
            "/execution/"
            f"reconcile-mt5/{user_id}"
        ),
        headers=headers,
    )

    assert response.status_code == 200

    assert captured["days"] == 30

    assert (
        response.json()["history_days"]
        == 30
    )


# ==========================================
# Authentication and Ownership
# ==========================================


def test_reconciliation_api_requires_authentication():
    """
    Reconciliation must not be available
    without JWT authentication.
    """

    response = client.post(
        "/execution/reconcile-mt5/1"
    )

    assert response.status_code == 401


def test_reconciliation_api_rejects_other_user():
    """
    An authenticated user must not reconcile
    another user's execution records.
    """

    headers, user_id = (
        get_auth_context()
    )

    other_user_id = user_id + 1000000

    response = client.post(
        (
            "/execution/"
            f"reconcile-mt5/{other_user_id}"
        ),
        headers=headers,
    )

    assert response.status_code == 403

    assert (
        response.json()["detail"]
        == (
            "You are not authorized to access "
            "execution data for this user."
        )
    )


# ==========================================
# Service Error Mapping
# ==========================================


def test_reconciliation_api_rejects_mock_mode(
    monkeypatch,
):
    """
    PermissionError from MOCK mode should
    become HTTP 403.
    """

    headers, user_id = (
        get_auth_context()
    )

    def fake_reconcile(
        self,
        user_id,
        days=30,
    ):
        raise PermissionError(
            "MT5 execution reconciliation "
            "requires DEMO mode."
        )

    monkeypatch.setattr(
        ExecutionReconciliationService,
        "reconcile_pending_executions",
        fake_reconcile,
    )

    response = client.post(
        (
            "/execution/"
            f"reconcile-mt5/{user_id}"
        ),
        headers=headers,
    )

    assert response.status_code == 403

    assert (
        response.json()["detail"]
        == (
            "MT5 execution reconciliation "
            "requires DEMO mode."
        )
    )


def test_reconciliation_api_maps_value_error(
    monkeypatch,
):
    """
    Service validation errors should become
    HTTP 400 responses.
    """

    headers, user_id = (
        get_auth_context()
    )

    def fake_reconcile(
        self,
        user_id,
        days=30,
    ):
        raise ValueError(
            "Invalid reconciliation request."
        )

    monkeypatch.setattr(
        ExecutionReconciliationService,
        "reconcile_pending_executions",
        fake_reconcile,
    )

    response = client.post(
        (
            "/execution/"
            f"reconcile-mt5/{user_id}"
        ),
        headers=headers,
    )

    assert response.status_code == 400

    assert (
        response.json()["detail"]
        == (
            "Invalid reconciliation request."
        )
    )


def test_reconciliation_api_maps_runtime_error(
    monkeypatch,
):
    """
    Broker/runtime failures should become
    HTTP 503 responses.
    """

    headers, user_id = (
        get_auth_context()
    )

    def fake_reconcile(
        self,
        user_id,
        days=30,
    ):
        raise RuntimeError(
            "MT5 broker unavailable."
        )

    monkeypatch.setattr(
        ExecutionReconciliationService,
        "reconcile_pending_executions",
        fake_reconcile,
    )

    response = client.post(
        (
            "/execution/"
            f"reconcile-mt5/{user_id}"
        ),
        headers=headers,
    )

    assert response.status_code == 503

    assert (
        response.json()["detail"]
        == "MT5 broker unavailable."
    )


# ==========================================
# Request Validation
# ==========================================


def test_reconciliation_api_rejects_invalid_user_id():
    """
    FastAPI should reject zero or negative
    reconciliation user IDs.

    Authentication is supplied so this test
    specifically verifies path validation.
    """

    headers, _ = get_auth_context()

    response = client.post(
        "/execution/reconcile-mt5/0",
        headers=headers,
    )

    assert response.status_code == 422


def test_reconciliation_api_rejects_days_below_range():
    """
    History window must be at least one day.
    """

    headers, user_id = (
        get_auth_context()
    )

    response = client.post(
        (
            "/execution/"
            f"reconcile-mt5/{user_id}"
            "?days=0"
        ),
        headers=headers,
    )

    assert response.status_code == 422


def test_reconciliation_api_rejects_days_above_range():
    """
    History window must not exceed
    3650 days.
    """

    headers, user_id = (
        get_auth_context()
    )

    response = client.post(
        (
            "/execution/"
            f"reconcile-mt5/{user_id}"
            "?days=3651"
        ),
        headers=headers,
    )

    assert response.status_code == 422