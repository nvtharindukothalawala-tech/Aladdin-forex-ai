"""
security.py

Handles password hashing and JWT tokens.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from jose import jwt

from passlib.context import CryptContext

from app.core.config import settings

# ==========================================
# JWT Configuration
# ==========================================

SECRET_KEY = settings.SECRET_KEY

ALGORITHM = settings.JWT_ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


# ==========================================
# Password Hashing
# ==========================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(
    password: str,
):
    """
    Convert normal password into secure hash.
    """

    # bcrypt supports maximum 72 bytes
    password = password[:72]

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
):
    """
    Verify password during login.
    """

    # bcrypt supports maximum 72 bytes
    plain_password = plain_password[:72]

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# ==========================================
# JWT Token
# ==========================================


def create_access_token(
    data: dict,
):
    """
    Create JWT access token.
    """

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update(
        {
            "exp": expire,
        }
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
