"""
test_execution_statistics.py

Tests execution statistics API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.main import app
from app.auth.dependencies import get_current_user


client = TestClient(app)


def test_get_execution_statistics():
    """
    Test that an authenticated user can
    retrieve their own execution statistics.
    """

    app.dependency_overrides[
        get_current_user
    ] = lambda: SimpleNamespace(
        id=1,
    )

    try:
        response = client.get(
            "/execution/statistics/1"
        )

        assert response.status_code == 200

        data = response.json()

        assert "total_executions" in data

        assert "successful_executions" in data

        assert "failed_executions" in data

        assert "success_rate" in data

        assert isinstance(
            data["total_executions"],
            int,
        )

        assert isinstance(
            data["success_rate"],
            (int, float),
        )

    finally:
        app.dependency_overrides.pop(
            get_current_user,
            None,
        )