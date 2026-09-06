"""
routes.py

Authentication API endpoints.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.database.connection import SessionLocal

from app.auth.service import AuthService

from app.auth.dependencies import get_current_user

from app.auth.models import UserModel

from app.schemas.auth_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ==========================================
# Authentication Service
# ==========================================


def get_service():

    session = SessionLocal()

    return AuthService(session)


# ==========================================
# REGISTER
# ==========================================


@router.post("/register")
def register(
    user: UserRegisterRequest,
):

    service = get_service()

    try:

        created_user = service.register_user(
            user.username,
            user.email,
            user.password,
        )

        return {
            "message": "User created successfully",
            "username": created_user.username,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


# ==========================================
# LOGIN
# ==========================================


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    user: UserLoginRequest,
):

    service = get_service()

    try:

        token = service.login_user(
            user.username,
            user.password,
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }

    except ValueError as error:

        raise HTTPException(
            status_code=401,
            detail=str(error),
        )


# ==========================================
# CURRENT USER
# ==========================================


@router.get("/me")
def get_me(
    current_user: UserModel = Depends(get_current_user),
):
    """
    Return the currently authenticated user.
    """

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }