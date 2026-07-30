"""
test_auth_security.py

Tests authentication security.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)


def test_password_hashing():

    password = "test123"

    hashed = hash_password(password)

    assert hashed != password

    assert verify_password(
        password,
        hashed,
    )


def test_create_token():

    token = create_access_token({"username": "tharindu"})

    assert token is not None

    assert isinstance(
        token,
        str,
    )
