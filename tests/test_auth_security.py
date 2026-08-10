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


from datetime import (
    datetime,
    timedelta,
    timezone,
)

from jose import jwt

from app.auth.security import (
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    create_access_token,
)


def test_create_access_token_contains_subject():
    token = create_access_token(
        {
            "sub": "testuser",
        }
    )

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    assert payload["sub"] == "testuser"


def test_create_access_token_contains_expiration():
    token = create_access_token(
        {
            "sub": "testuser",
        }
    )

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    assert "exp" in payload


def test_access_token_expiration_is_configured():
    assert ACCESS_TOKEN_EXPIRE_MINUTES > 0


def test_access_token_uses_configured_algorithm():
    token = create_access_token(
        {
            "sub": "testuser",
        }
    )

    header = jwt.get_unverified_header(token)

    assert header["alg"] == ALGORITHM
