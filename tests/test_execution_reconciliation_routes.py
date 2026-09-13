"""
test_execution_reconciliation_routes.py

Tests manual MT5 execution reconciliation API.

All broker reconciliation behavior is mocked.
These tests do not contact real MT5 and do not
open, modify, or close broker trades.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi.testclient import TestClient

from app.api.main import app

from app.services.execution_reconciliation_service import (
    ExecutionReconciliationService,
)


client = TestClient(app)


def test_reconciliation_api_returns_summary(
    monkeypatch,
):
    """
    Test successful manual reconciliation
    API response.
    """

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
                    "broker_order_id": "123456",
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
        "/execution/reconcile-mt5/1"
        "?days=45"
    )

    assert response.status_code == 200

    data = response.json()

    assert captured["user_id"] == 1
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
        "/execution/reconcile-mt5/1"
    )

    assert response.status_code == 200

    assert captured["days"] == 30

    assert (
        response.json()["history_days"]
        == 30
    )


def test_reconciliation_api_rejects_mock_mode(
    monkeypatch,
):
    """
    PermissionError from MOCK mode should
    become HTTP 403.
    """

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
        "/execution/reconcile-mt5/1"
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
        "/execution/reconcile-mt5/1"
    )

    assert response.status_code == 400

    assert (
        response.json()["detail"]
        == "Invalid reconciliation request."
    )


def test_reconciliation_api_maps_runtime_error(
    monkeypatch,
):
    """
    Broker/runtime failures should become
    HTTP 503 responses.
    """

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
        "/execution/reconcile-mt5/1"
    )

    assert response.status_code == 503

    assert (
        response.json()["detail"]
        == "MT5 broker unavailable."
    )


def test_reconciliation_api_rejects_invalid_user_id():
    """
    FastAPI should reject zero or negative
    reconciliation user IDs.
    """

    response = client.post(
        "/execution/reconcile-mt5/0"
    )

    assert response.status_code == 422


def test_reconciliation_api_rejects_days_below_range():
    """
    History window must be at least one day.
    """

    response = client.post(
        "/execution/reconcile-mt5/1"
        "?days=0"
    )

    assert response.status_code == 422


def test_reconciliation_api_rejects_days_above_range():
    """
    History window must not exceed
    3650 days.
    """

    response = client.post(
        "/execution/reconcile-mt5/1"
        "?days=3651"
    )

    assert response.status_code == 422