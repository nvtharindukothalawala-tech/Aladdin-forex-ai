"""
test_coaching_routes.py

Tests AI coaching API.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi.testclient import TestClient


from app.api.main import app

client = TestClient(app)


def test_get_coaching_report():

    response = client.get("/coaching/report")

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data

    assert "strengths" in data

    assert "recommendations" in data
