"""
routes.py

Authentication API endpoints.

Author: Tharindu Kothalawala
Project: Aladdin
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.database.connection import (
    get_db,
)

from app.auth.service import AuthService

from app.auth.dependencies import (
    get_current_user,
)

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
# Authentication Service Dependency
# ==========================================


def get_service(
    db=Depends(get_db),
):
    """
    Provide an authentication service using
    a request-scoped database session.

    The underlying get_db dependency closes
    the SQLAlchemy session automatically after
    the request finishes.
    """

    return AuthService(
        db
    )


# ==========================================
# REGISTER
# ==========================================


@router.post("/register")
def register(
    user: UserRegisterRequest,
    service: AuthService = Depends(
        get_service
    ),
):
    """
    Register a new user.
    """

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
    service: AuthService = Depends(
        get_service
    ),
):
    """
    Authenticate a user and return a JWT.
    """

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
    current_user: UserModel = Depends(
        get_current_user
    ),
):
    """
    Return the currently authenticated user.
    """

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }