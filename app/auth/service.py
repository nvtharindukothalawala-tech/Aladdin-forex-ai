"""
service.py

Authentication business logic.

Author: Tharindu Kothalwala
Project: Aladdin
"""

from app.auth.models import UserModel

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)


class AuthService:
    """
    Handles user registration and login.
    """

    def __init__(self, session):

        self.session = session

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
    ):
        """
        Create new user.
        """

        existing_user = (
            self.session.query(UserModel).filter(UserModel.username == username).first()
        )

        if existing_user:

            raise ValueError("Username already exists")

        user = UserModel(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )

        self.session.add(user)

        self.session.commit()

        self.session.refresh(user)

        return user

    def login_user(
        self,
        username: str,
        password: str,
    ):
        """
        Authenticate user.
        """

        user = (
            self.session.query(UserModel).filter(UserModel.username == username).first()
        )

        if not user:

            raise ValueError("Invalid username or password")

        if not verify_password(
            password,
            user.password_hash,
        ):

            raise ValueError("Invalid username or password")

        token = create_access_token({"sub": user.username})

        return token
