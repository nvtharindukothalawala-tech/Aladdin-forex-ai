"""
test_execution_history.py

Tests execution history API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.main import app
from app.auth.dependencies import get_current_user


client = TestClient(app)


def test_get_execution_history():
    """
    Test that an authenticated user can
    retrieve their own execution history.
    """

    app.dependency_overrides[
        get_current_user
    ] = lambda: SimpleNamespace(
        id=1,
    )

    try:
        response = client.get(
            "/execution/history/1"
        )

        assert response.status_code == 200

        data = response.json()

        assert isinstance(
            data,
            list,
        )

    finally:
        app.dependency_overrides.pop(
            get_current_user,
            None,
        )