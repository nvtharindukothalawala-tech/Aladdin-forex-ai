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

from app.auth.dependencies import (
    get_current_user,
)

from app.schemas.auth_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
)


# ==========================================
# Router
# ==========================================

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
# Register
# ==========================================

@router.post("/register")
def register(
    user: UserRegisterRequest,
):
    """
    Register a new user.
    """

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
# Login
# ==========================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    user: UserLoginRequest,
):
    """
    Authenticate user and return JWT token.
    """

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
# Current User
# ==========================================

@router.get("/me")
def get_me(
    current_user=Depends(get_current_user),
):
    """
    Return information about the
    currently authenticated user.

    The user is identified from the
    JWT access token.
    """

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }