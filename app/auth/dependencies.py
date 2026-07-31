"""
dependencies.py

Authentication dependencies.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal

from app.auth.models import UserModel

from app.auth.security import (
    SECRET_KEY,
    ALGORITHM,
)

# ==========================================
# Database Dependency
# ==========================================


def get_database():
    """
    Create and close a database session.
    """

    database = SessionLocal()

    try:
        yield database

    finally:
        database.close()


# ==========================================
# OAuth2 Authentication
# ==========================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)

# ==========================================
# Current User Dependency
# ==========================================


def get_current_user(
    token: str = Depends(oauth2_scheme),
    database: Session = Depends(get_database),
):
    """
    Verify JWT token and return the logged-in user.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        username = payload.get("sub")

        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = database.query(UserModel).filter(UserModel.username == username).first()

    if user is None:
        raise credentials_exception

    return user
